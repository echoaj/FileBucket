from django.shortcuts import render
from django.conf import settings
from .forms import InfoForm
from .models import Info


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
                url = "https://{}.s3.{}.amazonaws.com/{}/{}"
                url = url.format(*aws_variables, file_data['title'])
                file_data.update({"url": url})
                return render(request, "home.html", {'text_info': text, "file": file_data, "form": form})

    return render(request, "home.html", {'text_info': text, "file": file_data, "form": form})


aws_variables = (settings.AWS_STORAGE_BUCKET_NAME,
                 settings.AWS_S3_REGION_NAME,
                 settings.AWS_LOCATION)

