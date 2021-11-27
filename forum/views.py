from django.http import response
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.shortcuts import render
from forum.models import Favorite, User, Post, Response, Like
import time
import datetime
from django.db import connection
# Create your views here.


def index(request):
    cursor = connection.cursor()
    cursor.execute(
        "select owner_id, post_id, topic_text, favorite_num, like_num, response_num, (favorite_num + like_num + response_num) as score from forum_post order by score desc limit 10")
    desc = cursor.description
    trend_posts = [dict(zip([col[0] for col in desc], row))
                   for row in cursor.fetchall()]
    request.session["trend_posts"] = trend_posts
    if "isLogin" not in request.session:
        return render(request, 'index.html', {"isLogin": False, "username": "", "trend_posts": trend_posts})
    else:
        return render(request, 'index.html', {"isLogin": request.session["isLogin"], "username": request.session["currentUserId"], "trend_posts": trend_posts})


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        uname = request.POST.get("uname", "")
        pwd = request.POST.get("pwd", "")
        if User.objects.filter(user_name=uname, user_password=pwd).count() == 1:
            request.session["isLogin"] = True
            request.session["currentUserId"] = uname
            data = {
            "isLogin": request.session["isLogin"], 
            "username": request.session["currentUserId"], 
            "trend_posts": request.session["trend_posts"]
            }
            return render(request, 'index.html', data)
        else:
            return render(request, 'login.html', {"error": "Username or Password Error"})


def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html')
    uname = request.POST.get("uname", "")
    pwd = request.POST.get("pwd", "")
    if User.objects.filter(user_name=uname).count() == 1:
        return render(request, 'signup.html', {"error": "Username already taken"})
    else:
        user = User(user_name=uname, user_password=pwd)
        user.save()
        request.session["isLogin"] = True
        request.session["currentUserId"] = uname
        data = {
        "isLogin": request.session["isLogin"], 
        "username": request.session["currentUserId"], 
        "trend_posts": request.session["trend_posts"]
    }
    return render(request, 'index.html', data)

def logout(request):
    request.session["isLogin"] = False
    request.session["currentUserId"] = ""
    data = {
        "isLogin": request.session["isLogin"], 
        "username": request.session["currentUserId"], 
        "trend_posts": request.session["trend_posts"]
    }
    return render(request, 'index.html', data)


def newPost(request):
    return render(request, 'newPost.html', {"isLogin": request.session["isLogin"], "username": request.session["currentUserId"]})


def insertPost(request):
    pid = str(time.time())
    topic = request.POST.get("title", "")
    content = request.POST.get("content", "")
    date = time.strftime("%Y-%m-%d", time.localtime())
    post = Post(post_id=pid, topic_text=topic, content_text=content,
                create_date=date, owner_id=request.session["currentUserId"])
    post.save()
    return readPost(requests={"request": request, "post_id": pid})


def readPost(requests):

    if (type(requests) is dict):
        request = requests["request"]
        pid = requests["post_id"]
    else:
        request = requests
        pid = request.GET.get("pid")
    post = Post.objects.get(post_id=pid)
    responses = Response.objects.filter(post_id=pid)
    data = {
        "isLogin": request.session["isLogin"], 
        "username": request.session["currentUserId"], 
        "post": post,
        "responses": responses
    }
    if request.session["isLogin"]:
        hasLike = Like.objects.filter(post_id=pid, user_name=request.session["currentUserId"]).count()
        hasFavorite = Favorite.objects.filter(post_id=pid, user_name=request.session["currentUserId"]).count()
        data["hasLike"] = hasLike
        data["hasFavorite"] = hasFavorite
    else:
        data["hasLike"] = 0
        data["hasFavorite"] = 0
    return render(request, 'post.html', data)


def newResponse(request):
    pid = request.GET.get("pid")
    post = Post.objects.get(post_id=pid)
    content = request.POST.get("response")
    date = time.strftime("%Y-%m-%d", time.localtime())
    current_response = post.response_num
    Post.objects.filter(post_id=pid).update(response_num=current_response+1)
    response = Response(r_id=str(time.time()), owner_id = request.session["currentUserId"], post_id=pid, text=content, create_date=date)
    response.save()

    return redirect("/readpost?pid=" + pid, request)

def likePost(request):
    pid = request.GET.get("pid")
    post = Post.objects.get(post_id=pid)
    original_like = post.like_num
    Post.objects.filter(post_id=pid).update(like_num=original_like+1)
    like = Like(post_id=pid, user_name=request.session["currentUserId"], topic_text=post.topic_text)
    like.save()
    return redirect("/readpost?pid=" + pid, request)

def favoritePost(request):
    pid = request.GET.get("pid")
    post = Post.objects.get(post_id=pid)
    original_favorite = post.favorite_num
    Post.objects.filter(post_id=pid).update(favorite_num=original_favorite+1)
    favorite = Favorite(post_id=pid, user_name=request.session["currentUserId"], topic_text=post.topic_text)
    favorite.save()
    return redirect("/readpost?pid=" + pid, request)

def dashboard(request):
    like_list = Like.objects.filter(user_name=request.session["currentUserId"])
    favorite_list = Favorite.objects.filter(user_name=request.session["currentUserId"])

    data = {
        "isLogin": request.session["isLogin"], 
        "username": request.session["currentUserId"], 
        "like_num": len(like_list),
        "favorite_num": len(favorite_list),
        "like_list": like_list,
        "favorite_list": favorite_list
        }
    print("tag", favorite_list[0].tag)
    return render(request, "dashboard.html",data)

def addTag(request):
    pid = request.POST.get("pid")
    new_tag = request.POST.get("tag")
    Favorite.objects.filter(post_id=pid, user_name=request.session["currentUserId"]).update(tag=new_tag)
    return redirect("/dashboard", request)