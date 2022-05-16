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
    media_root_path = settings.MEDIA_ROOT
    media_folder = Path(media_root_path)
    if media_folder.exists():
        shutil.rmtree(media_root_path)


def db_save_text(text):
    db_cur = Info()
    if Info.objects.count() != 0:
        db_last = Info.objects.last()
        db_cur.file = db_last.file
        db_cur.file_location = db_last.file_location
    db_cur.text = text
    db_cur.save()


# Create your views here.
def home_view(request):

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
            text = request.POST.get('user-input-text', False)
            db_save_text(text)
        elif "file-upload-button" in request.POST:
            # InfoForm is a form that we defined in forms.py
            form = InfoForm(request.POST, request.FILES)
            if form.is_valid():
                if Info.objects.count() > 0:
                    clear_media()                                           # saves file to media folder
                    db_last = Info.objects.last()
                form.save()
                media_path = settings.MEDIA_URL[1:]
                file = request.FILES['file']                                # name of field we define in forms.py
                file_name = file.name
                file_data = dissect_file(file_name)                         # gets file data from file.name
                file_local_path = media_path + file_name        # Remove / at the beginning
                # Fixes issue with names files with spaces.
                # By default django renames those files with _
                # Causes problem with retrieving that file
                current_file_name = media_path + os.listdir(media_path)[0]
                os.rename(current_file_name, file_local_path)
                # 1st way of storing file on firebase
                # storage.child(file_name).put(file=file_local_path)
                blob = bucket.blob(file_name)
                blob.upload_from_filename(file_local_path)                  # Upload file to firebase
                blob.make_public()                                          # Make file download url accessible
                file_url = blob.public_url
                file_data.update({"url": file_url})
                # db portion
                db_last_form = Info.objects.last()
                if Info.objects.count() > 1:
                    db_last_form.text = db_last.text
                db_last_form.file_location = file_url
                text = db_last_form.text
                db_last_form.save()
                # storage.child("gs://filebucketapp.appspot.com/hello.txt").download(path=".", filename="sup.txt")
    return render(request, "home.html", {'text_info': text, "file": file_data, "form": form})


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
