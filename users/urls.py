from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('add_face', views.add_face, name='add_face'),
    path('face_recognition', views.face_recognition_view, name='face_recognition'),
    path('known_faces', views.known_faces, name='known_faces'),
    path('emotion_recognition', views.emotion_recognition_view, name='emotion_recognition'),
] 