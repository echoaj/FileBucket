from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
from .forms import InfoForm
from .models import Info
from pathlib import Path
import shutil
import environ
import pyrebase
import os


# Limits file name size
def chop_filename(filename, limit):
    extension = str(filename).split('.').pop()
    title = filename
    if len(filename) > limit:
        title = filename[0:limit]
        title += "...." + extension
    return title


# Returns dictionary of general file information
def dissect_file(filename: str) -> dict:
    title = chop_filename(filename, limit=25)
    split_name = str(filename).split('.')
    extension = split_name.pop()
    name = ".".join(split_name)
    data = {"name": name,
            "extension": extension,
            "title": title}
    return data


def clear_media():
    media_folder = Path(MEDIA_ROOT)
    if media_folder.exists():
        shutil.rmtree(MEDIA_ROOT)


def db_save_text(text):
    db_cur = Info()
    if Info.objects.count() != 0:
        db_last = Info.objects.last()
        db_cur.file = db_last.file
        db_cur.file_location = db_last.file_location
    db_cur.text = text
    db_cur.save()


def handle_spaces(file_local_path):
    # Fixes issue with names files with spaces.
    # By default django renames those files with _
    # Causes problem with retrieving that file
    current_file_name = MEDIA_PATH + os.listdir(MEDIA_PATH)[0]
    os.rename(current_file_name, file_local_path)


def cloud_upload(file_name, file_local_path):
    # 1st way of storing file on firebase
    # storage.child(file_name).put(file=file_local_path)
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_local_path)  # Upload file to firebase
    blob.make_public()  # Make file download url accessible
    return blob.public_url


# Create your views here.
def home_view(request):
    # global REFRESH_ON
    # REFRESH_ON = False
    text = ""
    form = InfoForm()
    file_data = {}
    # Retrieve last text from database if db not empty
    if Info.objects.count() > 0:
        text = Info.objects.last().text
        file_name = Info.objects.last().file.name
        file_data = dissect_file(file_name)
        file_url = Info.objects.last().file_location
        file_data.update({"url": file_url})

    if request.method == "POST":
        if "text-clear-button" in request.POST:
            text = ''
            db_save_text(text)
        elif "text-enter-button" in request.POST:
            # REFRESH_ON = True
            text = request.POST.get('user-input-text', False)
            db_save_text(text)
        elif "file-upload-button" in request.POST:
            # REFRESH_ON = True
            # InfoForm is a form that we defined in forms.py
            form = InfoForm(request.POST, request.FILES)
            if form.is_valid():
                # Check if any items in media
                if Info.objects.count() > 0:
                    clear_media()
                    db_last = Info.objects.last()
                form.save()                                                 # save file to /media and to DB
                file = request.FILES['file']                                # name of field we define in forms.py
                file_name = file.name                                       # name of file
                file_local_path = MEDIA_PATH + file_name                    # local path of file in /media
                file_data = dissect_file(file_name)                         # gets file data from file.name
                # Reverses django's default action of
                # replacing ' ' with _ in file names
                handle_spaces(file_local_path)
                # Upload file to firebase and make url to it public
                file_url = cloud_upload(file_name, file_local_path)
                file_data.update({"url": file_url})
                # Inject last DB record with previous text and file url
                db_last_form = Info.objects.last()
                if Info.objects.count() > 1:
                    db_last_form.text = db_last.text
                db_last_form.file_location = file_url
                text = db_last_form.text
                db_last_form.save()
    return render(request, "home.html", {'text_info': text, "file": file_data, "form": form})

"""
def refresh_view(request):
    print(request.method)
    global REFRESH_ON
    if request.method == "POST":
        print("POSt create =============")
        REFRESH_ON = False
    return HttpResponse(REFRESH_ON)
"""

MEDIA_PATH = settings.MEDIA_URL[1:]     # Remove / at the beginning
MEDIA_ROOT = settings.MEDIA_ROOT
# REFRESH_ON = False

# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

firebaseConfig = {
                    "apiKey": env("FIREBASE_API_KEY"),
                    "authDomain": "filebucketapp.firebaseapp.com",
                    "projectId": "filebucketapp",
                    "storageBucket": "filebucketapp.appspot.com",
                    "messagingSenderId": "602108448767",
                    "appId": "1:602108448767:web:b210cf7a7caa3bf963a1ca",
                    "serviceAccount": env("GOOGLE_APPLICATION_CREDENTIALS"),
                    "databaseURL": ""
                 }

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
bucket = storage.bucket
