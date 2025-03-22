from django.shortcuts import render,redirect
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.decorators import permission_required,login_required
# Create your views here.

@login_required(login_url='login')
def index(request):
    if request.method == 'POST':
        if request.user.has_perm('APP.add_books'):
            add_book = BookForm(request.POST, request.FILES)
            if add_book.is_valid():
                add_book.save()
                messages.success(request, "Add book successfuly")
        if request.user.has_perm('APP.add_category'):
            add_cat = CategoryForm(request.POST)
            if add_cat.is_valid():
                add_cat.save()
                messages.success(request,'Add category successfuly')
    context = {
        'category': Category.objects.all(),
        'books': Books.objects.all(),
        'form': BookForm(),
        'cat_form': CategoryForm(),
        'all_books': Books.objects.filter(active=True).count(),
        'books_sold': Books.objects.filter(status='sold').count(),
        'books_rental': Books.objects.filter(status='rental').count(),
        'books_availble': Books.objects.filter(status='availble').count(),
    }

    return render(request, 'pages/index.html', context)


def books(request):
    search = Books.objects.all()
    title = None
    if 'search_name' in request.GET:
        title = request.GET['search_name']
        if title:
            search = search.filter(title__icontains=title)

    if request.method == 'POST':
        if request.user.has_perm('APP.add_books'):
            add_book = BookForm(request.POST, request.FILES)
            if add_book.is_valid():
                add_book.save()
        if request.user.has_perm('APP.add_category'):
            add_cat = CategoryForm(request.POST)
            if add_cat.is_valid():
                add_cat.save()
                


    context = {
        'category': Category.objects.all(),
        'books': search,
        'form': BookForm(),
        'cat_form': CategoryForm(),
    }
    return render(request, 'pages/books.html', context)


@permission_required('APP.delete_books', raise_exception=True)
def delete(request, id):
    book_del = Books.objects.get(id=id)
    if request.method == 'POST':
        book_del.delete()
        messages.success(request,'Book delete successfuly!')
        return redirect('/')
    return render(request, 'pages/delete.html')

@login_required(login_url='login') 
@permission_required('APP.change_books', raise_exception=True)
def update(request, id):
    book_id = Books.objects.get(id=id)
    if request.method == 'POST':
        book_save = BookForm(request.POST, request.FILES, instance=book_id)
        if book_save.is_valid():
            book_save.save()
            messages.success(request,'Book Update successfuly!')
            return redirect('/')
    else:
        book_save = BookForm(instance=book_id)

    context = {
        'form': book_save,
    }
    return render(request, 'pages/update.html', context)




def register(request):
    user = CreateUserForm()
    if request.method == 'POST':
        user = CreateUserForm(request.POST)
        if user.is_valid():
            user.save()
            messages.success(request,'Register is successfuly!')
            return redirect('login')
    else:
        user = CreateUserForm()
        
    return render(request,'pages/register.html',{'form':user})
            
        
    
def my_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form=LoginForm(request , data=request.POST)
        if form.is_valid():
            username=request.POST.get('username')
            password=request.POST.get('password')
            
            user = authenticate(request , username=username , password=password)
            
            if user is not None:
                login(request,user)
                messages.success(request,'Login successfuly!')
                return redirect('/')
        else:
            form=LoginForm()
        
    context={'form':form}
        
    return render(request, 'pages/login.html' ,context)

def my_logout(request):
    logout(request)
    messages.success(request,'Logout successfuly!')
    return redirect('login')