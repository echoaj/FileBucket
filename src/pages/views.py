from django.shortcuts import render
from .models import Info
from django.core.files.storage import FileSystemStorage


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
            uploaded_file = request.FILES['doc']
            fs = FileSystemStorage()
            fs.save(uploaded_file.name, uploaded_file)

    return render(request, "home.html", {'text_info': text})

