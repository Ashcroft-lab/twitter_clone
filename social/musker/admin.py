from django.contrib import admin
# from django.contrib.auth.Models import Groups
from django.contrib.auth.models import Group, User
from .models import Profile,Meep

# Register your models here.
admin.site.unregister(Group)

# mix profile info
class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    model = User

    fields = ["username"]
    inlines = [ProfileInline]

# unregister init user
admin.site.unregister(User)

# admin.site.register(User)
admin.site.register(User, UserAdmin)
# admin.site.register(Profile)

admin.site.register(Meep)
