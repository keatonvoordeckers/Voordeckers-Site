from django.shortcuts import get_object_or_404, render

from .models import Category


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug) # Fetch category, show 404 if not found
    return render(request, "portfolio/category_detail.html", {"category": category})
