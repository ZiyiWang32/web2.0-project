from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from forum.models import User
# Create your views here.

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        uname = request.POST.get("uname", "")
        pwd = request.POST.get("pwd","")
        print(uname, pwd)
        if User.objects.filter(user_name = uname, user_password=pwd).count() == 1:
            return HttpResponse("Success")
        else:
            return HttpResponse("Failed")

def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html')
    uname = request.POST.get("uname", "")
    pwd = request.POST.get("pwd","")
    if User.objects.filter(user_name = uname, user_password=pwd).count() == 1:
        return HttpResponse("Username already taken")
    else:
        user = User(user_name=uname, user_password=pwd)
        user.save()
        return HttpResponse("Sign up successfully")