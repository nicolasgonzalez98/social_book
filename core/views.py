from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *
from .decorators import unauthorized_user
from itertools import chain

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.all()
    
    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower = request.user.username)

    for user in user_following:
        user_following_list.append(user)

    print(user_following_list)

    for username in user_following_list:
        newuser = User.objects.get(username = username)
        profile = Profile.objects.get(user=newuser)
        feed_lists = Post.objects.filter(user=profile)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))
    ctx = {'user_profile':user_profile, 'posts':feed_list }
    return render(request, 'index.html', ctx)

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = User.objects.get(username = request.user.username)
        profile = Profile.objects.get(user = user)
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=profile, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = user_profile)
    no_of_posts = len(user_posts)
    local_user = request.user.username

    if FollowersCount.objects.filter(follower=local_user, user = pk).first() == None:    
        text_button = 'Follow'
    else:
        text_button = 'Unfollow'

    if local_user == pk:
        text_button = ''

    followers = len(FollowersCount.objects.filter(user = pk))
    following = len(FollowersCount.objects.filter(follower = pk))                
    ctx = {
        'user_object':user_object,
        'user_profile':user_profile,
        'user_posts':user_posts,
        'no_of_posts':no_of_posts,
        'text_button': text_button,
        'followers':followers,
        'following':following
    }

    return render(request, 'profile.html',ctx)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        user_local = request.user
        user_followed = request.GET.get('user_followed')
        
        if FollowersCount.objects.filter(follower=user_local, user = user_followed).first() == None:
            new_follow = FollowersCount.objects.create(follower=user_local.username, user = user_followed)
            new_follow.save()
            return redirect(f'profile/{user_followed}') 
        else:
            follow = FollowersCount.objects.filter(follower=user_local, user = user_followed).first() 
            follow.delete()
            return redirect(f'profile/{user_followed}')
        
    else:
        return redirect(f'profile/{user_followed}')

@login_required(login_url='signin')
def like_post(request):
    post_id = request.GET.get('post_id')
    username = request.user.username
    post = Post.objects.get(id = post_id)
    
    like_post = LikePost.objects.filter(post_id = post, username=username).first()
    
    if like_post == None:
        new_like = LikePost.objects.create(post_id = post, username = username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_post.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')
    

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('settings')
    

    return render(request, 'setting.html', {'user_profile': user_profile})

@unauthorized_user
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)


                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user = user_model, id_user = user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Passwords not matching')
            return redirect('signup') 
    else:
        return render(request, 'signup.html')

@unauthorized_user
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request,'Credentials invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')