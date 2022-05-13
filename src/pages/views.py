from django.shortcuts import render
from django.conf import settings
from .forms import InfoForm
from .models import Info
import environ


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


# Create your views here.
def home_view(request):

    text = ""
    form = InfoForm()
    file_data = {}

    # Retrieve last text from database
    if Info.objects.count() != 0:
        text = Info.objects.last().text

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
            print("file sent")
            form = InfoForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                file = request.FILES['file']
                file_data = dissect_file(file.name)
                url = ""
                file_data.update({"url": url})
                return render(request, "home.html", {'text_info': text, "file": file_data, "form": form})

    return render(request, "home.html", {'text_info': text, "file": file_data, "form": form})

import pyrebase
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
                    "databaseURL": ""
                 }

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
storage.child("test.txt").put("media/test.txt")
