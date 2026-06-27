from django.urls import path
from .views import RegisterView , LogoutView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout")
]
