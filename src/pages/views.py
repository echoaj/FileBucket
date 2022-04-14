from django.shortcuts import render
from .models import Info
from django.core.files.storage import FileSystemStorage
import shutil


# Create your views here.
def home_view(request):
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
            fss = FileSystemStorage()
            shutil.rmtree(fss.base_location)
            file = request.FILES['doc']
            fss.save(file.name, file)
            result = str(file.name).split('.')
            extension = result.pop()
            name = ".".join(result)
            title = file.name
            limit = 35
            if len(title) > limit:
                title = title[0:limit] + "...." + extension

            data = {'text_info': text,
                    "file_name": name,
                    "file_extension": extension,
                    "file_title": title,
                    "file_size": file.size,
                    "file_url": fss.url(file)}

            return render(request, "home.html", data)

    return render(request, "home.html", {'text_info': text})
