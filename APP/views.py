from django.shortcuts import render,redirect
from .models import *
from .forms import BookForm , CategoryForm
from django.contrib.auth import authenticate, login

# Create your views here.

def index(request):
    if request.method == 'POST':
        add_book= BookForm(request.POST , request.FILES)
        if add_book.is_valid():
            add_book.save()
        
        add_cat =CategoryForm(request.POST)
        if add_cat.is_valid():
           add_cat.save()
    context={
        'category': Category.objects.all(),
        'books': Books.objects.all(),
        'form' : BookForm(),
        'cat_form' : CategoryForm(),
        'all_books' : Books.objects.filter(active=True).count(),
        'books_sold' : Books.objects.filter(status='sold').count(),
        'books_rental' : Books.objects.filter(status='rental').count(),
        'books_availble' : Books.objects.filter(status='availble').count(),
    }
    
    return render(request , 'pages/index.html',context)
    

def books(request):
    search = Books.objects.all()
    title = None
    if 'search_name' in request.GET:
        title= request.GET['search_name']
        if title :
           search = search.filter(title__icontains=title)
    
    
    if request.method == 'POST':
        add_book= BookForm(request.POST , request.FILES)
        if add_book.is_valid():
            add_book.save()
        
        add_cat =CategoryForm(request.POST)
        if add_cat.is_valid():
           add_cat.save()
    context={
        'category': Category.objects.all(),
        'books': search,
        'form' : BookForm(),
        'cat_form' : CategoryForm(),
    }
    return render(request , 'pages/books.html',context)

def delete(request,id):
    book_del = Books.objects.get(id=id)
    if request.method == 'POST':
        book_del.delete()
        return redirect('/')
    return render(request , 'pages/delete.html')

def update(request, id):
    book_id = Books.objects.get(id=id)
    if request.method == 'POST':
        book_save = BookForm(request.POST , request.FILES , instance=book_id)
        if book_save.is_valid():
            book_save.save()
            return redirect('/')
    else:
        book_save = BookForm(instance=book_id)
    
    context={
        'form': book_save,
    }
    return render(request , 'pages/update.html', context)


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)  

        if user is not None:
            login(request, user)  
            return redirect("/")  
        else:
            return render(request, "pages/login.html", {"error": "Invalid username or password"})

    return render(request, "pages/login.html")