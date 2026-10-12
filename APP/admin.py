from django.contrib import admin

from .models import Books, Category


@admin.register(Books)
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Category)
