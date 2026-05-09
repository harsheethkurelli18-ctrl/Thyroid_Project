from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("upload/", views.upload_dataset, name="upload_dataset"),
    path("classify/", views.classification_view, name="classification"),
    path("predict/", views.predict_view, name="prediction"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("activate/<int:user_id>/", views.activate_user, name="activate_user"),
]
