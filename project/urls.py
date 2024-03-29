"""
URL configuration for Lesson21_Django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from posts.views import home_page_view, create_note_view, show_note_view, show_about_view, update_note_view, delete_note_view

urlpatterns = [
    path('admin/', admin.site.urls),  # Подключение панели администратора.

    path("", home_page_view, name="home"),  # Добавим главную страницу.
    path("create", create_note_view, name="create-note"),
    path("about", show_about_view, name="about"),
    path("post/<note_uuid>", show_note_view, name="show-note"),
    path("update/<note_uuid>", update_note_view, name="update-note"),
    path("delete/<note_uuid>", delete_note_view, name="delete-note"),
]
