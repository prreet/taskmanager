from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.viewsets import ModelViewSet # Combined import
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from .models import Task
from .serializers import RegisterSerializer, TaskSerializer
from .permissions import IsAdminOrOwner

User = get_user_model()

# --- Authentication Views ---

class RegisterAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)

# --- Task ViewSet ---

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]
    
    # BONUS: Enable Search and Filtering [cite: 102, 105]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']     # Filter by status (completed/incomplete)
    search_fields = ['title', 'description'] # Search by title or description
    ordering_fields = ['updated_at']  # Optional: Allow ordering

    def get_queryset(self):
        user = self.request.user
        
        # Check if user is Staff OR in the 'Admin' group [cite: 55, 73]
        if user.is_staff or user.groups.filter(name='Admin').exists():
            return Task.objects.all()
            
        # Standard users see only their own tasks [cite: 74]
        return Task.objects.filter(owner=user)

    def perform_create(self, serializer):
        # Auto-assign the current user as the owner [cite: 40]
        serializer.save(owner=self.request.user)