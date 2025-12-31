from django.shortcuts import render
from .models import Staff
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import StaffUserRegistrationForm, StaffProfileForm

def staff_register(request):
    if request.method == 'POST':
        user_form = StaffUserRegistrationForm(request.POST)
        profile_form = StaffProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            staff = profile_form.save(commit=False)
            staff.user = user
            staff.is_approved = False
            staff.save()

            login(request, user)

            return render(request, 'staff/registration_success.html')

    else:
        user_form = StaffUserRegistrationForm()
        profile_form = StaffProfileForm()

    return render(request, 'staff/staff_register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def staff_list(request):
    academic_staff = Staff.objects.filter(
        category=Staff.ACADEMIC,
        is_approved=True
    )

    non_academic_staff = Staff.objects.filter(
        category=Staff.NON_ACADEMIC,
        is_approved=True
    )

    return render(request, 'staff/staff_list.html', {
        'academic_staff': academic_staff,
        'non_academic_staff': non_academic_staff,
    })


def management_staff(request):
    management = Staff.objects.filter(
        category=Staff.MANAGEMENT,
        is_approved=True
    ).order_by('display_order')

    return render(request, 'staff/management_list.html', {
        'management': management
    })
