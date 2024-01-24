from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from users.forms import CreateUserForm, AddFaceForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .utils import VideoCamera, f_recognition, e_recognition
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import face_recognition
import os
from threading import Thread
from keras.models import model_from_json
import numpy as np
import cv2
from users.models import Face

@login_required(login_url='login')
def home_view(request):
    return render(request, 'home.html', {})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Username or password is incorrect!')
                

        context = { 'login_color': '#f2f2f2', 'signup_color': 'white', 'form': form }
        return render(request, 'login.html', context)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f'Account was created for {form.cleaned_data.get("username")}')
                return redirect('login')

        context = { 'login_color': 'white', 'signup_color': '#f2f2f2', 'form': form }
        return render(request, 'signup.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

@gzip.gzip_page
def face_recognition_view(request):
    faces = Face.objects.all()
    dir = 'D:/MMProject/media/known_faces'
    known_face_encodings = []
    known_face_names = []

    for person in os.listdir(dir):
        person_image = face_recognition.load_image_file(os.path.join(dir, person))
        known_face_encodings.append(face_recognition.face_encodings(person_image)[0])
        for face in faces:
            if str(person) in str(face.picture): known_face_names.append(face.name)

    try:
        webcam = VideoCamera()
        thread = Thread(target=f_recognition, args=(webcam, known_face_encodings, known_face_names))
        thread.start()
        return StreamingHttpResponse(f_recognition(webcam, known_face_encodings, known_face_names), content_type="multipart/x-mixed-replace;boundary=frame")    
    except Exception as e:
        print(e)
    return render(request, 'face_recognition.html')



def emotion_recognition_view(request):
    json_file = open("./mm/trained_model_files/facialemotionmodel.json", "r")
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)
    model.load_weights("./mm/trained_model_files/facialemotionmodel.h5")

    haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(haar_file)

    labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

    try:
        webcam = VideoCamera()
        thread = Thread(target=e_recognition, args=(webcam, face_cascade, model, labels))
        thread.start()
        return StreamingHttpResponse(e_recognition(webcam, face_cascade, model, labels), content_type="multipart/x-mixed-replace;boundary=frame")    
    except Exception as e:
        print(e)
    return render(request, 'emotion_recognition.html', {})

def known_faces(request):
    all_faces = Face.objects.filter(user=request.user)
    return render(request, 'known_faces.html', {'all': all_faces})

def add_face(request):
    if request.method == 'POST':
        form = AddFaceForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            face = Face.objects.create(user=request.user, name=form.cleaned_data['name'], picture=form.cleaned_data['picture'])
            face.save()
    else:
        form = AddFaceForm(request.user)

    return render(request, 'add_face.html', {'form': form})
