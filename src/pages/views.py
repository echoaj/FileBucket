from django.shortcuts import render
from .models import Info


# Create your views here.
def home_view(request):
    text_result = request.POST.get('user_input', False)
    Info.text = text_result
    print(Info.text)
    return render(request, "home.html", {'text_info' : Info.text})
