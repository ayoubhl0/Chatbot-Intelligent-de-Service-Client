from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot_page'),
    path('new_chat/', views.new_chat, name='new_chat'),
    path('chat_json/', views.chatbot_json, name='chatbot_json'),
    path('live_gesture/', views.live_gesture, name='live_gesture'),  
    path('start_live_camera/', views.start_live_camera_view, name='start_live_camera'),
    path('history/', views.chat_history, name='chat_history'),
    path('delete_day/<str:day_date>/', views.delete_day, name='delete_day'),
    path('rename_day/<str:day_date>/', views.rename_day, name='rename_day'),


    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
        path('motdepasse_oublie/', views.password_reset_view, name='motdepasse_oublie'),
         path('welcome/', views.welcome_view, name='welcome'),
          path('aa/', views.aa_view, name='aa'),
              path('bye/', views.bye_view, name='bye'),
              path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_page, name='account'),
    path('home/', views.home, name='home'),
    path('predict_sign/', views.predict_sign, name='predict_sign'),
    
]