from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile, Meep
from .forms import MeepForm
from django.contrib.auth import authenticate, login, logout

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



def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST["password"]

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
