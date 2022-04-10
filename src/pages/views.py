from django.shortcuts import render
from .models import Info


# Create your views here.
def home_view(request):
    if request.method == "GET":
        text = Info.objects.last().text
        print(" --------------------------------------- ")
        print(text)
        print(" --------------------------------------- ")
        # print("*" * 40)
        # text = text.replace("\n", "<br>")
        # print(text)
        # print("*" * 40)
        return render(request, "home.html", {'text_info': text})
    if request.method == "POST":
        text = request.POST.get('user_input', False)
        db = Info(text=text)
        db.save()
        return render(request, "home.html", {'text_info': text})

