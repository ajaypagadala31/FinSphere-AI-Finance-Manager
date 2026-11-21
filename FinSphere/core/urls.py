from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("verify/", views.verify_otp, name="verify"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dataset/", views.dataset, name="dataset"),
    path("clusters/", views.clusters, name="clusters"),
    path("forecast/", views.forecast, name="forecast"),
    path("budget/", views.budget, name="budget"),
    path("feedback/", views.feedback, name="feedback"),
]
