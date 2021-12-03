from django.http import response
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.shortcuts import render
import nltk
from nltk.corpus import stopwords
from nltk.corpus.reader.wordnet import POS_LIST
from forum.models import Favorite, User, Post, Response, Like, UserInterest
import time
from django.db.models import Q
import datetime
from django.db import connection
import re
from django.db.models import Count

# Create your views here.


def index(request):
    cursor = connection.cursor()
    cursor.execute(
        "select owner_id, post_id, topic_text, favorite_num, like_num, response_num, (favorite_num + like_num + response_num) as score from forum_post order by score desc limit 10")
    desc = cursor.description
    trend_posts = [dict(zip([col[0] for col in desc], row))
                   for row in cursor.fetchall()]
    request.session["trend_posts"] = trend_posts
    if "isLogin" not in request.session or request.session["isLogin"] == False:
        return render(request, 'index.html', {"isLogin": False, "username": "", "trend_posts": trend_posts})
    else:
        # tags = Favorite.objects.filter(user_name=request.session["currentUserId"]).exclude(tag="").values_list("tag", flat=True)
        # tag_list = [x for x in tags]
        # posts = Favorite.objects.filter(user_name=request.session["currentUserId"]).exclude(tag="").values_list("post_id", flat=True)
        # post_list = [x for x in posts]
        # related_posts = Favorite.objects.filter(tag__in = tag_list).exclude(Q(user_name=request.session["currentUserId"]) | Q(post_id__in=posts)).values_list("post_id", flat=True)
        # rec_posts = Post.objects.filter(post_id__in = related_posts).order_by('-favorite_num')
        currentFavorite = Favorite.objects.filter(user_name=request.session["currentUserId"]).values_list("post_id", flat=True)
        favorite_list = [x for x in currentFavorite]

        users = (Favorite.objects.filter(post_id__in=favorite_list)
                          .values('user_name').exclude(user_name = request.session["currentUserId"])
                          .annotate(dcount=Count('post_id'))
                          )
        
        print("user:", users)
        related_users = []
        for user in users:
            if user["dcount"] >= 3:
                related_users.append(user["user_name"])
        print("related users:", related_users)
        rec_posts = set()
        for user in related_users:
            recommand_posts = Favorite.objects.filter(user_name=user).exclude(post_id__in=favorite_list)
            if len(recommand_posts)> 0:
                for post in recommand_posts:
                    if post.post_id not in rec_posts:
                        rec_posts.add(post.post_id)

        rec_posts_list = Post.objects.filter(post_id__in = rec_posts)
        print(rec_posts_list)
        data = {"isLogin": request.session["isLogin"],
                "username": request.session["currentUserId"],
                "trend_posts": trend_posts,
                "rec_posts": rec_posts_list
                }
        return render(request, 'index.html', data)


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
        hasLike = Like.objects.filter(
            post_id=pid, user_name=request.session["currentUserId"]).count()
        hasFavorite = Favorite.objects.filter(
            post_id=pid, user_name=request.session["currentUserId"]).count()
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
    response = Response(r_id=str(time.time(
    )), owner_id=request.session["currentUserId"], post_id=pid, text=content, create_date=date)
    response.save()

    return redirect("/readpost?pid=" + pid, request)


def likePost(request):
    pid = request.GET.get("pid")
    post = Post.objects.get(post_id=pid)
    original_like = post.like_num
    Post.objects.filter(post_id=pid).update(like_num=original_like+1)
    like = Like(
        post_id=pid, user_name=request.session["currentUserId"], topic_text=post.topic_text)
    like.save()
    user_add_exp(request.session["currentUserId"], 1)
    addToInterest(request.session["currentUserId"], post)
    return redirect("/readpost?pid=" + pid, request)


def favoritePost(request):
    pid = request.GET.get("pid")
    post = Post.objects.get(post_id=pid)
    original_favorite = post.favorite_num
    Post.objects.filter(post_id=pid).update(favorite_num=original_favorite+1)
    favorite = Favorite(
        post_id=pid, user_name=request.session["currentUserId"], topic_text=post.topic_text)
    favorite.save()
    user_add_exp(request.session["currentUserId"], 2)
    addToInterest(request.session["currentUserId"], post)
    return redirect("/readpost?pid=" + pid, request)


def addToInterest(uname, post):
    topic_text = post.topic_text.split(" ")
    content_text = re.split(" |\r\n ", post.content_text)
    tag_text = post.tag.split(" ")

    for text in topic_text:
        text = text.lower()
        if text in stopwords.words():
            continue
        text = re.sub(r'\W+', '', text)

        user_interest = UserInterest.objects.filter(user_name=uname, term=text)
        if len(user_interest) > 0:
            user_interest = UserInterest.objects.get(
                user_name=uname, term=text)
            UserInterest.objects.filter(user_name=uname, term=text).update(
                term_count=user_interest.term_count+1)
        else:
            user_interest = UserInterest(
                user_name=uname, term=text, term_count=1)
            user_interest.save()

    for text in content_text:
        text = text.lower()
        if text in stopwords.words():
            continue
        text = re.sub(r'\W+', '', text)

        user_interest = UserInterest.objects.filter(user_name=uname, term=text)
        if len(user_interest) > 0:
            user_interest = UserInterest.objects.get(
                user_name=uname, term=text)
            UserInterest.objects.filter(user_name=uname, term=text).update(
                term_count=user_interest.term_count+1)
        else:
            user_interest = UserInterest(
                user_name=uname, term=text, term_count=1)
            user_interest.save()

    for text in tag_text:
        text = text.lower()
        if text in stopwords.words():
            continue
        text = re.sub(r'\W+', '', text)
        if text == "":
            continue
        user_interest = UserInterest.objects.filter(user_name=uname, term=text)
        if len(user_interest) > 0:
            user_interest = UserInterest.objects.get(
                user_name=uname, term=text)
            UserInterest.objects.filter(user_name=uname, term=text).update(
                term_count=user_interest.term_count+1)
        else:
            user_interest = UserInterest(
                user_name=uname, term=text, term_count=1)
            user_interest.save()


def dashboard(request):
    like_list = Like.objects.filter(user_name=request.session["currentUserId"])
    favorite_list = Favorite.objects.filter(
        user_name=request.session["currentUserId"])
    user = User.objects.get(user_name=request.session["currentUserId"])
    level = user.user_level
    data = {
        "isLogin": request.session["isLogin"],
        "username": request.session["currentUserId"],
        "like_num": len(like_list),
        "favorite_num": len(favorite_list),
        "like_list": like_list,
        "favorite_list": favorite_list,
        "level": level,
        "exp": user.user_exp
    }
    return render(request, "dashboard.html", data)


def addTag(request):
    pid = request.POST.get("pid")
    new_tag = request.POST.get("tag")
    Favorite.objects.filter(
        post_id=pid, user_name=request.session["currentUserId"]).update(tag=new_tag)

    tag_text = Post.objects.get(post_id=pid).tag
    tag_text += new_tag + " "
    Post.objects.filter(post_id=pid).update(tag=tag_text)

    return redirect("/dashboard", request)


def user_add_exp(username, exp):
    user = User.objects.get(user_name=username)
    level = user.user_level
    current_exp = user.user_exp
    if current_exp + exp >= 2**level:
        level += 1
        current_exp = (current_exp + exp) % (2**level)
    else:
        current_exp += exp
    User.objects.filter(user_name=username).update(
        user_exp=current_exp, user_level=level)


def search(request):
    query = request.POST.getlist("query_term[]")

    query_set = set(query)
    post_list = Post.objects.filter()
    result_dict = {}
    for post in post_list:
        topic_text = post.topic_text
        content_text = post.content_text
        tag_text = post.tag
        topic_list = topic_text.split(" ")
        content_list = content_text.split(" ")
        tag_list = tag_text.split(" ")

        score = 0
        document_score = 0
        for topic in topic_list:
            topic_text = re.sub(r'\W+', '', topic.lower())
            if topic_text in query_set:
                score += 1
            if UserInterest.objects.filter(user_name=request.session["currentUserId"], term=topic_text).count() == 1:
                document_score += UserInterest.objects.get(
                    user_name=request.session["currentUserId"], term=topic_text).term_count

        for content in content_list:
            content_text = re.sub(r'\W+', '', content.lower())
            if content_text in query_set:
                score += 1
            if UserInterest.objects.filter(user_name=request.session["currentUserId"], term=content_text).count() == 1:
                document_score += UserInterest.objects.get(
                    user_name=request.session["currentUserId"], term=content_text).term_count

        for tag in tag_list:
            tag_text = re.sub(r'\W+', '', tag.lower())
            if tag_text in query_set:
                score += 1

            if UserInterest.objects.filter(user_name=request.session["currentUserId"], term=tag_text).count() == 1:
                document_score += UserInterest.objects.get(
                    user_name=request.session["currentUserId"], term=tag_text).term_count

        if score >= 1:
            result_dict[post.post_id] = document_score
    
    result = sorted(result_dict.items(), key=lambda item: item[1], reverse=True)
    search_list = []
    if len(result) > 0:
        for id in result:
            print(id)
            search_list.append(Post.objects.get(post_id=id[0]))
    data = {
        "isLogin": request.session["isLogin"],
        "username": request.session["currentUserId"],
        "search_list": search_list
    }
    return render(request, "search.html", data)
