from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name= "index"),
    path('about/', views.about, name= "about"),
    path('contact/', views.contact, name= "contact"),
    
    path('profile/',views.profile,name="profile"),
    path('checkout/', views.checkout, name="Checkout"),
    # path('handlerequest/', views.handlerequest, name="HandleRequest"),
]
