from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Books(models.Model):
    BOOK_STATUS = [("sold", "Sold"), ("availble", "Available"), ("rental", "Rental")]
    book_status = BOOK_STATUS  # Backward-compatible alias for existing imports.
    title = models.CharField(max_length=250, default="boooook")
    author = models.CharField(max_length=250, null=True, blank=True, default="MAHMOzz")
    photo_book = models.ImageField(upload_to="photos", null=True, blank=True)
    photo_author = models.ImageField(upload_to="photos", null=True, blank=True)
    pages = models.IntegerField(
        null=True, blank=True, default=300, validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=500,
        validators=[MinValueValidator(0)],
    )
    retal_price_day = models.DecimalField(
        null=True,
        blank=True,
        max_digits=5,
        decimal_places=2,
        default=4.5,
        validators=[MinValueValidator(0)],
    )
    retal_period = models.IntegerField(
        null=True, blank=True, default=8, validators=[MinValueValidator(1)]
    )
    total_rental = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=50, choices=BOOK_STATUS, null=True, blank=True, default="availble"
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        permissions = [
            ("can_view_books", "Can view books"),
            ("can_change_book_status", "Can change book status"),
        ]

    def __str__(self):
        return self.title
