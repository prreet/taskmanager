from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tasks.models import Task

class Command(BaseCommand):
    help = "Create Admin and User groups and assign Task permissions"

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        user_group, _ = Group.objects.get_or_create(name="User")

        task_ct = ContentType.objects.get_for_model(Task)
        # all permissions on Task
        perms = Permission.objects.filter(content_type=task_ct)
        for p in perms:
            admin_group.permissions.add(p)
        # For users, give add/change/delete/view their own tasks through object permission checks
        self.stdout.write(self.style.SUCCESS("Created groups and assigned permissions."))
