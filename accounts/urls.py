from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard' ),
    path('register/', views.register, name='register' ),
    path('login/', views.login, name='login' ),
    path('logout/', views.logout, name='logout' ),
    path('dashboard/', views.dashboard, name='dashboard' ),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword' ),

    # Activate Link URL
    path('activate/<uid64>/<token>/', views.activate, name='activate'),
    
    # Reset Password Link URL
    path('resetpassword_validate/<uid64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword' ),
]
