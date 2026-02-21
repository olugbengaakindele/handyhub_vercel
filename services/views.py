from django.shortcuts import render, redirect
from django.http import HttpResponse as hp
from .forms import *
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# Decorator to allow only staff users
def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required)
def add_service_category(request):
    if request.method == "POST":
        form = ServiceCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            return redirect("users:index")
    else:
        form = ServiceCategoryForm()

    return render(request, "services/add_service_category.html", {"form": form})



@login_required
@user_passes_test(staff_required)
def add_subcategory(request):
    if request.method == "POST":
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:index")
    else:
        form = SubCategoryForm()
    
    return render(request, 'services/add_subcategory.html', {'form': form})



# this is an ajax view
@login_required
@user_passes_test(staff_required)
def get_subcategories_by_category(request):
    category_id = request.GET.get("category_id")

    subcategories = []
    if category_id:
        subcategories = list(
            SubCategory.objects
            .filter(category_id=category_id)
            .values_list("name", flat=True)
        )

    return JsonResponse({"subcategories": subcategories})