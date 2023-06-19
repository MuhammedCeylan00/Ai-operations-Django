from google.cloud import vision_v1p3beta1 as vision
from google.cloud import translate_v2 as translate
from google.cloud import speech
from PIL import Image, ImageDraw
import io
import os
path = '/Users/muhammedceylan/desktop/bulutBilisimPython/still-girder-317612-c58250876d2e.json'
from django.http import HttpRequest, JsonResponse


def tag_objects(image_path):
    # Google Cloud Vision API'sini kullanarak resimdeki nesneleri etiketler
    client = vision.ImageAnnotatorClient()

    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.object_localization(image=image)

    tags = [obj.name for obj in response.localized_object_annotations]
    return tags


def extract_text_from_image(image_bytes):
    # Google Cloud Vision API'sini kullanarak resimden metin çıkarır
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)

    texts = []
    for text in response.text_annotations:
        texts.append(text.description)

    return texts


def detect_faces(image_bytes):
    # Google Cloud Vision API'sini kullanarak resimdeki yüzleri tespit eder
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.face_detection(image=image)
    faces = []
    for face in response.face_annotations:
        faces.append({
            'bounding_box': {
                'vertices': [
                    {'x': vertex.x, 'y': vertex.y} for vertex in face.bounding_poly.vertices
                ]
            },
            'joy_likelihood': face.joy_likelihood,
            'sorrow_likelihood': face.sorrow_likelihood,
            'anger_likelihood': face.anger_likelihood,
            'surprise_likelihood': face.surprise_likelihood,
            'under_exposed_likelihood': face.under_exposed_likelihood,
            'blurred_likelihood': face.blurred_likelihood,
            'headwear_likelihood': face.headwear_likelihood
        })
    return faces


def draw_faces(image_bytes, faces):
    # Resim üzerine tespit edilen yüzleri çizer
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)
    for face in faces:
        vertices = face['bounding_box']['vertices']
        draw.polygon([
            (vertices[0]['x'], vertices[0]['y']),
            (vertices[1]['x'], vertices[1]['y']),
            (vertices[2]['x'], vertices[2]['y']),
            (vertices[3]['x'], vertices[3]['y'])
        ], outline='red')
    image_bytes_io = io.BytesIO()
    image.save(image_bytes_io, format='JPEG')
    image_bytes_io.seek(0)
    return image_bytes_io


def translate_text(text, target_language):
    # Metni belirtilen hedef dilde çevirir
    client = translate.Client()
    result = client.translate(text, target_language=target_language)
    translated_text = result['translatedText']
    return translated_text


def transcribe_speech(audio_file):
    # Ses dosyasından konuşmayı transkribe eder
    client = speech.SpeechClient()
    with open(audio_file, "rb") as audio_data:
        content = audio_data.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=24000,
        audio_channel_count=2,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript
