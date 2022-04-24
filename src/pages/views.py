from django.shortcuts import render
from .models import Info
from django.core.files.storage import FileSystemStorage
from pathlib import Path
import shutil


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
    size = fss.size(filename)
    name = ".".join(split_name)
    data = {"name": name,
            "extension": extension,
            "title": title,
            "size": size}
    return data


# Create your views here.
def home_view(request):

    text = ""
    # Retrieve last text from database
    if Info.objects.count() != 0:
        text = Info.objects.last().text

    # Retrieve name of file in media
    file_data = {}

    if media_folder.exists():
        folder_items = [p.name for p in media_folder.iterdir()]
        if folder_items:
            file_data = dissect_file(folder_items[0])
            file_data.update({"url": fss.url(folder_items[0])})

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
            if media_folder.exists():
                shutil.rmtree(media_path)
            file = request.FILES['doc']
            fss.save(file.name, file)
            file_data = dissect_file(file.name)
            file_data.update({"url": fss.url(file)})
            print(fss.url(file))
            return render(request, "home.html", {'text_info': text, "file": file_data})

    return render(request, "home.html", {'text_info': text, "file": file_data})


fss = FileSystemStorage()
media_path = fss.base_location
media_folder = Path(media_path)
