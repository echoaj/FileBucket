from django.shortcuts import render
from django.conf import settings
from .forms import InfoForm
from .models import Info
from pathlib import Path
import shutil
import environ
import pyrebase


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


# Create your views here.
def home_view(request):

    text = ""
    form = InfoForm()
    file_data = {}

    # Retrieve last text from database if db not empty
    if request.method == "GET" and Info.objects.count() != 0:
        text = Info.objects.last().text
        file_name = Info.objects.last().file.name
        file_data = dissect_file(file_name)
        blob = bucket.blob(file_name)
        file_url = blob.public_url
        file_data.update({"url": file_url})

    if request.method == "POST":
        if "text-clear-button" in request.POST:
            text = ''
            db = Info(text=text)
            db.save()
        elif "text-enter-button" in request.POST:
            text = request.POST.get('user-input-text', False)
            db = Info(text=text)
            db.save()
        elif "file-upload-button" in request.POST:
            # InfoForm is a form that we defined in forms.py
            form = InfoForm(request.POST, request.FILES)
            if form.is_valid():
                clear_media()
                form.save()                                                 # saves file to media folder
                file = request.FILES['file']                                # name of field we define in forms.py
                file_name = file.name
                file_data = dissect_file(file_name)                         # gets file data from file.name
                file_local_path = settings.MEDIA_URL[1:] + file_name        # Remove / at the beginning
                # 1st way of storing file on firebase
                # storage.child(file_name).put(file=file_local_path)
                blob = bucket.blob(file_name)
                blob.upload_from_filename(file_local_path)                  # Upload file to firebase
                blob.make_public()                                          # Make file download url accessible
                file_url = blob.public_url
                file_data.update({"url": file_url})
                # storage.child("gs://filebucketapp.appspot.com/hello.txt").download(path=".", filename="sup.txt")
                return render(request, "home.html", {'text_info': text, "file": file_data, "form": form})

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
