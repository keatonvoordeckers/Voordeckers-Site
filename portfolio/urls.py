from  django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("<slug:slug>/", views.category_detail, name="category")
]