from django.shortcuts import render
from .models import Info
from django.core.files.storage import FileSystemStorage
from pathlib import Path
import shutil


# limits file name size
def chop_file(filename, limit):
    extension = str(filename).split('.').pop()
    title = filename
    if len(filename) > limit:
        title = filename[0:limit]
        title += "...." + extension
    return title


# returns dictionary of general file information
def dissect_file(file):
    filename = file.name
    result = str(filename).split('.')
    extension = result.pop()
    name = ".".join(result)
    title = chop_file(filename, limit=25)
    data = {"name": name,
            "extension": extension,
            "title": title,
            "size": file.size}
    return data


# Create your views here.
def home_view(request):
    # Retrieve last text from database
    text = Info.objects.last().text

    # Retrieve name of file in media
    fss = FileSystemStorage()
    media_root = fss.base_location
    file_data = {}

    if Path(media_root).exists():
        tuple = fss.listdir(media_root)
        flatten_list = sum(tuple, [])
        print(flatten_list)
        print(list(Path(media_root).glob('*.*')))

        if len(flatten_list) > 0:
            title = flatten_list[0]
            size = fss.size(title)
            result = str(title).split('.')
            extension = result.pop()
            name = ".".join(result)
            file_data = {"name": name,
                         "extension": extension,
                         "title": title,
                         "size": size}
            file_data.update({"url": fss.url(title)})

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
            if Path(media_root).exists():
                shutil.rmtree(fss.base_location)
            file = request.FILES['doc']
            fss.save(file.name, file)
            file_data = dissect_file(file)
            file_data.update({"url": fss.url(file)})
            print(file_data)
            return render(request, "home.html", {'text_info': text, "file": file_data})

    return render(request, "home.html", {'text_info': text, "file": file_data})
