from django.urls import path
from account.views import UserRegistrationView, UserLoginView, UserVerifyTokenView, UserRefreshTokenView, UserLogoutView

app_name = 'account'
urlpatterns = [
    path('refresh-token', name='refresh-token', view= UserRefreshTokenView.as_view()),
    path('verify-token', name='verify-token', view= UserVerifyTokenView.as_view()),
    path('signup', name='signup', view= UserRegistrationView.as_view(), ),
    path('login', name='login', view= UserLoginView.as_view()),
    path('logout', name='logout', view= UserLogoutView.as_view()),
]