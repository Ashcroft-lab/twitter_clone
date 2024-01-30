from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Meep
from .forms import MeepForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

# Create your views here.
def home(request):

    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request, "Your meep has been posted.")
                return redirect("home")

        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, "home.html", {"meeps": meeps, "form":form})
    else:
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, "home.html", {"meeps": meeps})

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)


        return render(request, "profile_list.html", {"profiles":profiles})
    else:
        messages.success(request, ("you must be logged in to view this page"))
        return redirect("home")

def follow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)

        request.user.profile.follows.add(profile)
        request.user.profile.save()

        messages.success(request, f'You just folllowed {profile.user.username}.')
        return redirect(request.META.get('HTTP_REFERER'))
    messages.success(request, 'you must be logged in...')
    return redirect('login')

def unfollow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id= pk)
        
        request.user.profile.follows.remove(profile)
        request.user.profile.save()

        messages.success(request, f'You have successfully unfollowed { profile.user.username }.')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.success(request, 'you must be logged in..')
        return redirect('home')

def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")


        #  Post Form Logic
        if request.method == "POST":
            # Get curr user id
            current_user_profile = request.user.profile

            #  get form data
            action = request.POST['follow']

            # Decide to follow/Unfollow

            if action == "unfollow":
                current_user_profile.follows.remove(profile)

            elif action == "follow":
                current_user_profile.follows.add(profile)

            # Save profile
            current_user_profile.save()




        return render(request, "profile.html", {"profile" : profile, "meeps":meeps})
    else:
        messages.success(request, ("you must be logged in to view this page"))
        return redirect("home")

def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:

            profiles = Profile.objects.get(user_id=pk)
            return render(request, "followers.html", {"profiles":profiles})
    
    messages.success(request, ("you are not allowed to view this page"))
    return redirect("home")


def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:

            profiles = Profile.objects.get(user_id=pk)
            return render(request, "follows.html", {"profiles":profiles})
    
    messages.success(request, ("you are not allowed to view this page"))
    return redirect("home")



def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("Logged in Successfully"))
            return redirect("home")
        else:
            messages.success(request, ("Enter Correct Username/Password... "))
            return redirect("login")

    else:
        return render(request, "login.html", {})

def logout_user(request):
    logout(request)
    messages.success(request, ("You have been Logged Out."))
    return redirect("home")



def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']


            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # email = form.cleaned_data['email']

            # Login user
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request, user)
                messages.success(request, ('You have Successfully registered'))
                return redirect('home')

    return render(request, "register.html", {'form':form})


def update_user(request):
    if request.user.is_authenticated:


        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)

        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)

        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            login(request, current_user)
            messages.success(request, "Your Profile has been updated ")

        return render(request, "update_user.html", {'user_form':user_form, 'profile_form':profile_form})
        
    else:
        messages.success(request, ("You must be Logged in to view that page"))
        return redirect("home")


def meep_like(request, pk):

    referer = request.META.get('HTTP_REFERER', 'home')
    
    if request.user.is_authenticated:

        meep = get_object_or_404(Meep, id=pk)
        if meep.likes.filter(id=request.user.id):
            meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)

    else:
        messages.success(request, 'You must be logged in' )
    return redirect(referer)

def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    
    if meep:
        # url = request.url
        return render(request, 'show_meep.html', {'meep':meep})
    else:
        messages.success(request,'Meep doesn\'t exist')
        return redirect('home') 

def delete_meep(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)

        if request.user.username == meep.user.username:
            meep.delete()
            messages.success(request, "You have deleted the meep")
        else:
            messages.success(request, "You are not allowed to delete this meep!!")
        return redirect(request.META.get("HTTP_REFERER", 'home'))

    else:
        messages.success(request, 'please Login to continue')
        return redirect('login')


def edit_meep(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        

        if request.user.username == meep.user.username:
            form = MeepForm(request.POST or None, instance=meep)
            if request.method == "POST":
                if form.is_valid():
                    meep = form.save(commit=False)
                    meep.user = request.user
                    meep.save()
                    messages.success(request, "You have edited a meep")
                    return redirect('home')


            context = {'form': form, 'meep': meep}
            return render(request, 'edit_meep.html', context)

        else:
            messages.success(request, "You are not allowed to edit this meep!!")
        return redirect(request.META.get("HTTP_REFERER", 'home'))

    else:
        messages.success(request, 'please Login to continue')
        return redirect('login')

def search(request):

    if request.method == "POST":
        search = request.POST['search']
        searched = Meep.objects.filter(body__contains = search)

        return render(request, 'search.html', {'search':search, 'searched':searched})
    
    else:
        return render(request, 'search.html', {})

def search_user(request):
    if request.method == "POST":
        search = request.POST['search']
        searched = User.objects.filter(username__contains=search)
        return render(request, 'search_user.html', {'search':search, "searched":searched })
    return render(request, 'search_user.html', {})

    # context = {}
    # if request.method == "POST":
    #     context['search'] = request.POST['search']
    #     context['searched'] = User.objects.filter(username__contains = search)

    # return render(request, 'search_user.html', context)