from django.urls import path
from . import views

app_name = 'recognition'

urlpatterns = [
    path('home', views.IndexView.as_view()),
    path('video_feed', views.video_feed_view(), name="video_feed"),
    path('recognition_video_feed/', views.recognition_video_feed(), name='recognition_video_feed'),
    path('add_face_data/', views.add_face_data, name='add_face_data'),
    path('train_face_data/', views.train_face_data, name='train_face_data'),
    path('video_index/', views.video_index, name='video_index'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('webcam_feed/', views.webcam_feed, name='webcam_feed'),
    path('mask_feed/', views.mask_feed, name='mask_feed'),
	path('livecam_feed/', views.livecam_feed, name='livecam_feed'),
]