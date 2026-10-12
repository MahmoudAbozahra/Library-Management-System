from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .forms import BookForm, CategoryForm, CreateUserForm, LoginForm
from .models import Books, Category


@login_required(login_url="login")
def index(request):
    book_form = BookForm()
    category_form = CategoryForm()
    if request.method == "POST":
        if "add_category" in request.POST:
            if request.user.has_perm("APP.add_category"):
                category_form = CategoryForm(request.POST)
                if category_form.is_valid():
                    category_form.save()
                    messages.success(request, "Category added successfully.")
                    return redirect("index")
            else:
                messages.error(request, "You do not have permission to add categories.")
        elif request.user.has_perm("APP.add_books"):
            book_form = BookForm(request.POST, request.FILES)
            if book_form.is_valid():
                book_form.save()
                messages.success(request, "Book added successfully.")
                return redirect("index")
        else:
            messages.error(request, "You do not have permission to add books.")

    context = {
        "category": Category.objects.all(),
        "books": Books.objects.select_related("category").all(),
        "form": book_form,
        "cat_form": category_form,
        "all_books": Books.objects.filter(active=True).count(),
        "books_sold": Books.objects.filter(status="sold").count(),
        "books_rental": Books.objects.filter(status="rental").count(),
        "books_availble": Books.objects.filter(status="availble").count(),
    }
    return render(request, "pages/index.html", context)


def books(request):
    search = Books.objects.select_related("category").all()
    title = request.GET.get("search_name", "").strip()
    if title:
        search = search.filter(title__icontains=title)
    return render(
        request,
        "pages/books.html",
        {
            "category": Category.objects.all(),
            "books": search,
            "form": BookForm(),
            "cat_form": CategoryForm(),
            "search_name": title,
        },
    )


@login_required(login_url="login")
@permission_required("APP.delete_books", raise_exception=True)
@require_http_methods(["GET", "POST"])
def delete(request, id):
    book = get_object_or_404(Books, pk=id)
    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully.")
        return redirect("index")
    return render(request, "pages/delete.html", {"book": book})


@login_required(login_url="login")
@permission_required("APP.change_books", raise_exception=True)
@require_http_methods(["GET", "POST"])
def update(request, id):
    book = get_object_or_404(Books, pk=id)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book updated successfully.")
        return redirect("index")
    return render(request, "pages/update.html", {"form": form, "book": book})


@require_http_methods(["GET", "POST"])
def register(request):
    form = CreateUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Registration was successful.")
        return redirect("login")
    return render(request, "pages/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def my_login(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Login successful.")
        destination = request.POST.get("next") or request.GET.get("next")
        if destination and url_has_allowed_host_and_scheme(
            destination, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(destination)
        return redirect("index")
    return render(request, "pages/login.html", {"form": form, "next": request.GET.get("next", "")})


@login_required(login_url="login")
@require_POST
def my_logout(request):
    logout(request)
    messages.success(request, "Logout successful.")
    return redirect("login")
