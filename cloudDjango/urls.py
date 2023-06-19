from django.urls import path
from appname.views import annotate_image, extract_text, detect_faces_endpoint, translate_endpoint, transcribe_endpoint


urlpatterns = [
    path('annotate', annotate_image, name='annotate_image'),
    path('extract-text', extract_text, name='extract_text'),
    path('detect-faces', detect_faces_endpoint, name='detect_faces'),
    path('translate', translate_endpoint, name='translate'),
    path('transcribe', transcribe_endpoint, name='transcribe'),
]
