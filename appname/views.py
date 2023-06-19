from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from google.cloud import vision_v1p3beta1 as vision
from google.cloud import translate_v2 as translate
from google.cloud import speech
from PIL import Image, ImageDraw
import json
import os
from cloudDjango.utils import tag_objects,extract_text_from_image, detect_faces, draw_faces, translate_text, transcribe_speech

path = '/Users/muhammedceylan/desktop/bulutBilisimPython/still-girder-317612-c58250876d2e.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path


@csrf_exempt
def annotate_image(request):
    if request.method == 'POST':
        image_file = request.FILES['image']
        image_path = 'temp.jpg'
        with open(image_path, 'wb') as f:
            f.write(image_file.read())

        tags = tag_objects(image_path)

        response = {
            'tags': tags
        }
        return JsonResponse(response)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def extract_text(request):
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        texts = extract_text_from_image(image_bytes)
        response = {
            'extracted_text': texts
        }
        return JsonResponse(response)


@csrf_exempt
def detect_faces_endpoint(request):
    if request.method == 'POST':
        image_file = request.FILES['image']
        image_bytes = image_file.read()

        detected_faces = detect_faces(image_bytes)

        result_image_bytes_io = draw_faces(image_bytes, detected_faces)
        return HttpResponse(result_image_bytes_io, content_type='image/jpeg')
    else:
        return HttpResponse(status=405)

@csrf_exempt
def translate_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        target_language = data.get('target_language')
        text = data.get('text')
        if not text:
            response = {
                'error': 'No text provided.'
            }
            return JsonResponse(response, status=400)

        translated_text = translate_text(text, target_language)

        response = {
            'translated_text': translated_text
        }
        return JsonResponse(response)
    else:
        return HttpResponse(status=405)


@csrf_exempt
def transcribe_endpoint(request):
    if request.method == 'POST':
        if 'audio' not in request.FILES:
            return JsonResponse({'error': 'No audio file provided'}, status=400)

        audio_file = request.FILES['audio']
        audio_path = 'audio.flac'
        with open(audio_path, 'wb') as f:
            f.write(audio_file.read())

        transcription = transcribe_speech(audio_path)

        response = {
            'transcription': transcription
        }
        return JsonResponse(response)
    else:
        return HttpResponse(status=405)
