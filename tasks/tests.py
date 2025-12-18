from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User, Group
from .models import Task

class TaskPermissionsTests(APITestCase):
    def setUp(self):
        # 1. Setup Users
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.user_stranger = User.objects.create_user(username='stranger', password='password123')
        self.user_admin = User.objects.create_user(username='admin_user', password='password123')

        # 2. Setup Admin Role
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        self.user_admin.groups.add(admin_group)

        # 3. Setup Data
        self.task = Task.objects.create(
            title="Owner's Task",
            description="Secret details",
            owner=self.user_owner
        )
        
        # 4. URLs
        self.list_url = reverse('task-list')
        self.detail_url = reverse('task-detail', kwargs={'pk': self.task.id})

    def test_user_can_manage_own_task(self):
        """
        Verify a user can retrieve and update their own task.
        """
        self.client.force_authenticate(user=self.user_owner)
        
        # Retrieve
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        data = {'title': 'Updated Title', 'status': True}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=self.task.id).title, 'Updated Title')

    def test_stranger_cannot_access_others_task(self):
        """
        Verify a standard user CANNOT access or delete someone else's task.
        This confirms your RBAC/Permission class is working.
        """
        self.client.force_authenticate(user=self.user_stranger)
        
        # Try to Retrieve (GET)
        response = self.client.get(self.detail_url)
        # DRF typically returns 404 (Not Found) for queryset filtering 
        # or 403 (Forbidden) depending on where the check happens.
        # Given your get_queryset, it likely returns 404 because the object isn't in their list.
        self.assertTrue(response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # Try to Delete (DELETE)
        response = self.client.delete(self.detail_url)
        self.assertTrue(response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_admin_can_manage_any_task(self):
        """
        Verify an Admin can access and delete ANY user's task.
        """
        self.client.force_authenticate(user=self.user_admin)
        
        # Admin retrieve
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin delete
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'test@example.com' # Email is often required by RegisterSerializer
        }
        self.user = User.objects.create_user(
            username='existinguser', 
            password='testpassword123'
        )

    def test_login_returns_jwt_token(self):
        """
        Bonus: Verify login endpoint returns access and refresh tokens.
        """
        data = {
            'username': 'existinguser',
            'password': 'testpassword123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)