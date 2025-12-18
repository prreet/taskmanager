from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterAPIView, CustomTokenObtainPairView, CustomTokenRefreshView, TaskViewSet
from rest_framework_simplejwt.views import TokenVerifyView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    # auth
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth-login"),  # returns access + refresh
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token-verify"),
    # tasks
    path("", include(router.urls)),
]

"""
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet)

urlpatterns = router.urls
"""