from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("login", views.user_login, name="login"),
    path("signup", views.user_signup, name="signup"),
    path("logout", views.user_logout, name="logout"),
    path("forgot-password", views.forgot_password, name="forgot_password"),
    path(
        "password-reset/<uidb64>/<token>/", views.password_reset, name="password_reset"
    ),
    path(
        "password-reset-success",
        views.password_reset_success,
        name="password_reset_success",
    ),
]
