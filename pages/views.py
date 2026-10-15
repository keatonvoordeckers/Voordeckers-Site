from django.shortcuts import render

def home(request):
    return render(request, "pages/home.html") # Render loads a template, fills it in, and returns it as the HTTP response.

# TODO: placeholder
def about(request):
    return render(request, "pages/about.html")

# TODO: placeholder
def contact(request):
    return render(request, "pages/contact.html")