from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponseRedirect, Http404, HttpRequest, HttpResponseForbidden
from django.core.handlers.wsgi import WSGIRequest

from .models import Note, User


def home_page_view(request: HttpRequest):
    """
    Обязательно! Каждая функция view должна принимать первым параметром request.
    """
    context: dict = {
        "notes": Note.objects.all()
    }
    print(request.user)
    return render(request, "home.html", context)


def filter_notes_view(request: WSGIRequest):
    """
    Фильтруем записи по запросу пользователя.
    HTTP метод - GET.
    Обрабатывает URL вида: /filter/?search=<text>
    """

    search: str = request.GET.get("search", "")  # `get` - получение по ключу. Если такого нет, то - "",

    # Если строка поиска не пустая, то фильтруем записи по ней.
    if search:
        # ❗️Нет обращения к базе❗️
        # Через запятую запросы формируются c ❗️AND❗️
        # notes_queryset = Note.objects.filter(title__icontains=search, content__icontains=search)
        # SELECT "posts_note"."uuid", "posts_note"."title", "posts_note"."content", "posts_note"."created_at"
        # FROM "posts_note" WHERE (
        # "posts_note"."title" LIKE %search% ESCAPE '\' AND "posts_note"."content" LIKE %search% ESCAPE '\')

        # ❗️Все импорты сверху файла❗️
        # from django.db.models import Q

        notes_queryset = Note.objects.filter(title__icontains=search, content__icontains=search)
        # Аналогия
        notes_queryset = Note.objects.filter(Q(title__icontains=search), Q(content__icontains=search))

        # Оператор - `|` Означает `ИЛИ`.
        # Оператор - `&` Означает `И`.
        notes_queryset = Note.objects.filter(Q(title__icontains=search) | Q(content__icontains=search))

    else:
        # Если нет строки поиска.
        notes_queryset = Note.objects.all()  # Получение всех записей из модели.

    notes_queryset = notes_queryset.order_by("-created_at")  # ❗️Нет обращения к базе❗️

    # SELECT "posts_note"."uuid", "posts_note"."title", "posts_note"."content", "posts_note"."created_at"
    # FROM "posts_note" WHERE
    # ("posts_note"."title" LIKE %python% ESCAPE '\' OR "posts_note"."content" LIKE %python% ESCAPE '\')
    # ORDER BY "posts_note"."created_at" DESC

    print(notes_queryset.query)

    context: dict = {
        "notes": notes_queryset,
        "search_value_form": search,
    }
    return render(request, "home.html", context)


def create_note_view(request: WSGIRequest):
    print(request.user)  # В каждом запросе есть пользователь!
    # НО, только если он вошел на сайте, в ином случае это аноним.
    if not request.user.is_authenticated:
        return render(request, "registration/login.html", {"errors": "Необходимо войти"})

    if request.method == "POST":
        images: list | None = request.FILES.getlist("noteImage")

        note = Note.objects.create(
            title=request.POST["title"],
            content=request.POST["content"],
            user=request.user,
            image=request.FILES.get("noteImage"),
        )
        return HttpResponseRedirect(reverse('show-note', args=[note.uuid]))

    # Вернется только, если метод не POST.
    return render(request, "create_form.html")

def show_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)  # Получение только ОДНОЙ записи.

    except Note.DoesNotExist:
        # Если не найдено такой записи.
        raise Http404

    return render(request, "note.html", {"note": note})


def update_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)

        if note.user != request.user:
            return HttpResponseForbidden("Запрещено!")

        if request.method == "POST":
            note.title = request.POST.get("title")
            note.content = request.POST.get("content")
            note.mod_time = timezone.now()
            if request.FILES.get("noteImage"):
                if note.image:
                    note.image.delete()
                note.image = request.FILES.get("noteImage")

            note.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "updatenote.html", {"note": note})
    except Note.DoesNotExist:
        raise Http404

def edit_note_view(request: WSGIRequest, note_uuid):
    try:
        note = Note.objects.get(uuid=note_uuid)
    except Note.DoesNotExist:
        raise Http404

    if note.user != request.user:
        return HttpResponseForbidden("Запрещено!")

    if request.method == "POST":
        note.title = request.POST["title"]
        note.content = request.POST["content"]
        note.mod_time = timezone.now()
        if request.FILES.get("noteImage"):
            if note.image:
                note.image.delete()
            note.image = request.FILES.get("noteImage")
        note.save()
        return HttpResponseRedirect(reverse('show-note', args=[note.uuid]))
    return render(request, "edit_form.html", {"note": note})

def delete_note_view(request: WSGIRequest, note_uuid):
    note = Note.objects.get(uuid=note_uuid)
    if note.user != request.user:
        return HttpResponseForbidden("Запрещено!")

    if request.method == "POST":
        Note.objects.filter(uuid=note_uuid).delete()
    return HttpResponseRedirect(reverse("home"))

def user_posts(request: WSGIRequest, username):
    notes = Note.objects.filter(user__username=username)
    context: dict = {
        "notes": notes
    }
    return render(request, "home.html", context)



def register(request: WSGIRequest):
    if request.method != "POST":
        return render(request, "registration/register.html")
    print(request.POST)
    if not request.POST.get("username") or not request.POST.get("email") or not request.POST.get("password1"):
        return render(
            request,
            "registration/register.html",
            {"errors": "Укажите все поля!"}
        )
    print(User.objects.filter(
            Q(username=request.POST["username"]) | Q(email=request.POST["email"])
    ))
    # Если уже есть такой пользователь с username или email.
    if User.objects.filter(
            Q(username=request.POST["username"]) | Q(email=request.POST["email"])
    ).count() > 0:
        return render(
            request,
            "registration/register.html",
            {"errors": "Если уже есть такой пользователь с username или email"}
        )

    # Сравниваем два пароля!
    if request.POST.get("password1") != request.POST.get("password2"):
        return render(
            request,
            "registration/register.html",
            {"errors": "Пароли не совпадают"}
        )

    # Создадим учетную запись пользователя.
    # Пароль надо хранить в БД в шифрованном виде.
    User.objects.create_user(
        username=request.POST["username"],
        email=request.POST["email"],
        password=request.POST["password1"]
    )
    return HttpResponseRedirect(reverse('home'))

def show_about_view(request: WSGIRequest):
    return render(request, "about.html")
