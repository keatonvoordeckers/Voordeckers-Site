from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "pages/home.html") # Render loads a template, fills it in, and returns it as the HTTP response.
