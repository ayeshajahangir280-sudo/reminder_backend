from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import CurrentUserView, LoginView, LogoutView, PasswordResetConfirmView, PasswordResetRequestView, RegisterView
from documents.views import DocumentViewSet
from notifications.views import NotificationViewSet
from reminders.views import ReminderViewSet

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="document")
router.register("reminders", ReminderViewSet, basename="reminder")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/me/", CurrentUserView.as_view()),
    path("api/auth/forgot-password/", PasswordResetRequestView.as_view()),
    path("api/auth/reset-password/", PasswordResetConfirmView.as_view()),
    path("api/", include(router.urls)),
]
