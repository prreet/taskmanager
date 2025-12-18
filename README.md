# Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd taskmanager
```

### 2. Build and Run

This command builds the image and starts the server on port `8000`.

```
docker-compose up --build
```

*The API is now live at `http://localhost:8000/`.*

### 3. Initialize Database & Roles

Open a **new terminal** window (while the server is running) to set up the database and user roles inside the container.

```
# Apply database migrations
docker-compose exec web python manage.py migrate

# Create 'Admin' and 'User' groups (Required for RBAC)
docker-compose exec web python manage.py create_groups

# Create 'Admin' credentials 
docker-compose exec web python manage.py createsuperuser
```


---

## Authentication

Before managing tasks, you must get an **Access Token** .

### Step A: Register

**POST** `/api/auth/register/`

```
curl -X POST http://localhost:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"username": "myuser", "email": "user@test.com", "password": "mypassword123", "password2": "mypassword123"}'
```

### Step B: Login

**POST** `/api/auth/login/`

```
curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "myuser", "password": "mypassword123"}'
```

**Response:**

**JSON**

```
{
  "refresh": "eyJ0eX...",
  "access": "eyJ0eX..."  <-- COPY THIS TOKEN
}
```

---

## Task Management (CRUD)

**IMPORTANT:** For all commands below, replace `<YOUR_ACCESS_TOKEN>` with the "access" token you got from the Login step.

### List All Tasks

**GET** `/api/tasks/`

```
curl -X GET http://localhost:8000/api/tasks/ \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### Create a Task

**POST** `/api/tasks/`

```
curl -X POST http://localhost:8000/api/tasks/ \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Finish Docker setup", "description": "Write the README file", "status": false}'
```

### Get One Task

**GET** `/api/tasks/<id>/`

```
curl -X GET http://localhost:8000/api/tasks/1/ \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### Update a Task (Mark as Complete)

**PATCH** `/api/tasks/<id>/`

```
curl -X PATCH http://localhost:8000/api/tasks/1/ \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"status": true}'
```

### Delete a Task

**DELETE** `/api/tasks/<id>/`

```
curl -X DELETE http://localhost:8000/api/tasks/1/ \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## Filtering & Search

You can add query parameters to the **List** command.

* **Filter by Status:** `http://localhost:8000/api/tasks/?status=True`

  ```
  curl -X GET "http://localhost:8000/api/tasks/?status=True" \
       -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
  ```
* **Search Text:** `http://localhost:8000/api/tasks/?search=Docker`

---



## Role-Based Access Control (RBAC) Check

1. **Standard User:**
   * Register a new user (User B).
   * Try to access User A's task ID.
   * **Result:** `404 Not Found` (Security works).
2. **Admin User:**
   * Make a user an Admin via Docker:

     ```
     docker-compose exec web python manage.py shell
     ```

     ```
     from django.contrib.auth.models import User, Group
     u = User.objects.get(username='myuser')
     u.groups.add(Group.objects.get(name='Admin'))
     exit()
     ```
   * Try to access User A's task ID.
   * **Result:** `200 OK` (Admin access works).

---



## API Endpoints

### Authentication

| **Method** | **Endpoint**      | **Description**          |
| ---------------- | ----------------------- | ------------------------------ |
| POST             | `/api/auth/register/` | Register a new user            |
| POST             | `/api/auth/login/`    | Login and retrieve pair tokens |
| POST             | `/api/auth/refresh/`  | Refresh access token           |

### Tasks

*All task endpoints require `Authorization: Bearer <token>` header.*

| **Method** | **Endpoint**          | **Description**                                |
| ---------------- | --------------------------- | ---------------------------------------------------- |
| GET              | `/api/tasks/`             | List all tasks (Users see their own; Admins see all) |
| POST             | `/api/tasks/`             | Create a new task                                    |
| GET              | `/api/tasks/?status=True` | Filter tasks by completion status                    |
| GET              | `/api/tasks/?search=work` | Search tasks by title or description                 |
| GET              | `/api/tasks/<id>/`        | Retrieve specific task details                       |
| PUT              | `/api/tasks/<id>/`        | Update specific task                                 |
| PATCH            | `/api/tasks/<id>/`        | Partial update (e.g., mark complete)                 |
| DELETE           | `/api/tasks/<id>/`        | Delete a task                                        |

---

## Running Tests

To run the automated test suite inside the Docker container:

```
docker-compose exec web python manage.py test tasks
```
