from django.contrib import admin
from .models import *
# Register your models here.
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    

admin.site.register(Books, BookAdmin)
admin.site.register(Category)