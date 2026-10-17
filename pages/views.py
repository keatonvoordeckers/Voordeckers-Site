from django.shortcuts import render

from portfolio.models import Category

def home(request):
    categories = Category.objects.all()
    return render(request, "pages/home.html", {"categories": categories})

# TODO: placeholder
def about(request):
    return render(request, "pages/about.html")

# TODO: placeholder
def contact(request):
    return render(request, "pages/contact.html")