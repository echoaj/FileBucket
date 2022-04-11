from django.shortcuts import render
from .models import Info
from django.core.files.storage import FileSystemStorage


# Create your views here.
def home_view(request):
    if request.method == "GET":
        text = Info.objects.last().text
        return render(request, "home.html", {'text_info': text})
    if request.method == "POST":
        uploaded_file = request.FILES['doc']
        print("*****************************************")
        print(uploaded_file.name)
        print(uploaded_file.size)
        print("*****************************************")
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file);
        # TEXT
        # text = request.POST.get('user_input', False)
        # db = Info(text=text)
        # db.save()
        text=''
        return render(request, "home.html", {'text_info': text})

