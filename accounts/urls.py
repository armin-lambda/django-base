from django.urls import path

from . import views


app_name = 'accounts'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('send-otp-code/', views.SendOTPCodeView.as_view(), name='send_otp_code'),
    path('verify-otp-code/', views.VerifyOTPCodeView.as_view(), name='verify_otp_code'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),

    path('edit/', views.AccountEditView.as_view(), name='edit'),
    path('delete/', views.AccountDeleteView.as_view(), name='delete'),
    path('delete-profile-image/', views.ProfileImageDeleteView.as_view(), name='profile_image_delete'),
    
    path('', views.PeopleView.as_view(), name='people'),
    
    path('<username>/', views.ProfileView.as_view(), name='profile'),
    path('<username>/follow/', views.FollowView.as_view(), name='follow'),
    path('<username>/unfollow/', views.UnfollowView.as_view(), name='unfollow'),
    
    path('<username>/followers/', views.FollowersView.as_view(), name='followers'),
    path('<username>/following/', views.FollowingView.as_view(), name='following'),
]