from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .forms import BookForm
from .models import Books, Category


class LibraryWorkflowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fiction")
        self.book = Books.objects.create(
            title="Dune", author="Frank Herbert", category=self.category
        )
        self.customer = User.objects.create_user(username="reader", password="Strong-pass-123")
        self.worker = User.objects.create_user(username="worker", password="Strong-pass-123")
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="Strong-pass-123"
        )
        self.worker.user_permissions.add(Permission.objects.get(codename="change_books"))
        self.worker.user_permissions.add(Permission.objects.get(codename="add_books"))
        self.worker.user_permissions.add(Permission.objects.get(codename="add_category"))
        self.worker.user_permissions.add(Permission.objects.get(codename="can_view_books"))

    def test_registration_and_login(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new-reader",
                "password1": "V3ry-Strong-Pass!",
                "password2": "V3ry-Strong-Pass!",
            },
        )
        self.assertRedirects(response, reverse("login"))
        response = self.client.post(
            reverse("login"),
            {
                "username": "new-reader",
                "password": "V3ry-Strong-Pass!",
            },
        )
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_rejects_external_redirect(self):
        response = self.client.post(
            reverse("login") + "?next=https://example.org",
            {"username": "reader", "password": "Strong-pass-123", "next": "https://example.org"},
        )
        self.assertRedirects(response, reverse("index"))

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(reverse("login"), {"username": "reader", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("index"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('index')}")

    def test_public_book_search_filters_by_title(self):
        Books.objects.create(title="Foundation", category=self.category)
        response = self.client.get(reverse("books"), {"search_name": "dun"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["books"]), [self.book])

    def test_customer_cannot_add_books_or_categories(self):
        self.client.force_login(self.customer)
        self.client.post(reverse("index"), {"title": "Forbidden"})
        self.client.post(reverse("index"), {"add_category": "1", "name": "Forbidden"})
        self.assertFalse(Books.objects.filter(title="Forbidden").exists())
        self.assertFalse(Category.objects.filter(name="Forbidden").exists())

    def test_worker_can_add_book_and_category(self):
        self.client.force_login(self.worker)
        response = self.client.post(reverse("index"), {"title": "New title", "status": "availble"})
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(Books.objects.filter(title="New title").exists())
        response = self.client.post(reverse("index"), {"add_category": "1", "name": "History"})
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(Category.objects.filter(name="History").exists())

    def test_worker_can_update_but_cannot_delete_book(self):
        self.client.force_login(self.worker)
        response = self.client.post(
            reverse("update", args=[self.book.pk]),
            {
                "title": "Dune Updated",
                "status": "availble",
                "category": self.category.pk,
            },
        )
        self.assertRedirects(response, reverse("index"))
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Dune Updated")
        response = self.client.post(reverse("delete", args=[self.book.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Books.objects.filter(pk=self.book.pk).exists())

    def test_delete_requires_post_and_delete_permission(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("delete", args=[self.book.pk])).status_code, 200)
        response = self.client.post(reverse("delete", args=[self.book.pk]))
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(Books.objects.filter(pk=self.book.pk).exists())

    def test_book_form_does_not_expose_primary_key(self):
        self.assertNotIn("id", BookForm().fields)

    def test_book_form_rejects_invalid_numeric_values(self):
        form = BookForm(data={"title": "Invalid", "pages": 0, "price": -1, "retal_period": 0})
        self.assertFalse(form.is_valid())
        self.assertIn("pages", form.errors)
        self.assertIn("price", form.errors)
        self.assertIn("retal_period", form.errors)

    def test_category_protects_books_from_orphaning(self):
        from django.db.models.deletion import ProtectedError

        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_logout_requires_post(self):
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))


class UnauthenticatedBookOperationsTests(TestCase):
    def test_update_and_delete_redirect_anonymous_users_to_login(self):
        book = Books.objects.create(title="Public")
        for name in ("update", "delete"):
            response = self.client.post(reverse(name, args=[book.pk]))
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("login"), response["Location"])
        self.assertTrue(Books.objects.filter(pk=book.pk).exists())
