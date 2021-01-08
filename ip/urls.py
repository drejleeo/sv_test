from django.urls import path
from ip import views


urlpatterns = [
    path('track/<str:action>', views.TrackActionAPI.as_view(), name='track_api'),
]
