from django.urls import path
from . import views



urlpatterns = [
    path('' , views.index , name='index'),
    path('books' , views.books , name='books'),
    path('delete<int:id>' , views.delete , name='delete'),
    path('update<int:id>' , views.update , name='update'),
    path('register',views.register,name='register'),
    path('login',views.my_login,name='login'),
    path('logout',views.my_logout,name='logout'),
    
]

