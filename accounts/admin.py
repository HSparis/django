from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = 'Profile Detail'
    verbose_name_plural = 'Profile Details'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    def save_formset(self, request, form, formset, change):
        # Prevent duplicated insertion when User is created via signal
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Profile):
                # Update existing profile created by post_save signal
                profile, created = Profile.objects.get_or_create(user=instance.user)
                profile.role = instance.role
                profile.student_id = instance.student_id
                profile.save()
            else:
                instance.save()
        formset.save_m2m()

# Unregister default User admin and register customized UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)