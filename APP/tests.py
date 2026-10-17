import os
import subprocess
import sys
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

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

    def test_authenticated_session_persists_between_requests(self):
        self.assertTrue(self.client.login(username="reader", password="Strong-pass-123"))

        first_response = self.client.get(reverse("index"))
        second_response = self.client.get(reverse("index"))

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(str(self.customer.pk), self.client.session["_auth_user_id"])

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
        self.assertFalse(self.worker.has_perm("APP.can_change_book_status"))
        response = self.client.post(
            reverse("update", args=[self.book.pk]),
            {
                "title": "Dune Updated",
                "status": "rental",
                "category": self.category.pk,
            },
        )
        self.assertRedirects(response, reverse("index"))
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Dune Updated")
        self.assertEqual(self.book.status, "rental")
        response = self.client.post(reverse("delete", args=[self.book.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Books.objects.filter(pk=self.book.pk).exists())

    def test_customer_cannot_update_or_delete_book_with_direct_requests(self):
        self.client.force_login(self.customer)

        update_response = self.client.post(
            reverse("update", args=[self.book.pk]),
            {"title": "Tampered", "status": "sold"},
        )
        delete_response = self.client.post(reverse("delete", args=[self.book.pk]))

        self.assertEqual(update_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "Dune")
        self.assertEqual(self.book.status, "availble")

    def test_delete_requires_post_and_delete_permission(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("delete", args=[self.book.pk])).status_code, 200)
        self.assertTrue(Books.objects.filter(pk=self.book.pk).exists())
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


class CategoryCreationDispatchTests(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(username="category-worker", password="test-pass")
        self.worker.user_permissions.add(Permission.objects.get(codename="add_category"))
        self.worker.user_permissions.add(Permission.objects.get(codename="add_books"))
        self.customer = User.objects.create_user(username="category-reader", password="test-pass")

    def test_sidebar_category_form_has_expected_dispatch_marker(self):
        self.client.force_login(self.worker)

        response = self.client.get(reverse("index"))

        self.assertContains(response, 'name="add_category" value="1"')

    def test_authorized_user_creates_category_without_creating_book(self):
        self.client.force_login(self.worker)

        response = self.client.post(
            reverse("index"),
            {"add_category": "1", "name": "History", "title": "Must not become a book"},
        )

        self.assertRedirects(response, reverse("index"))
        self.assertTrue(Category.objects.filter(name="History").exists())
        self.assertFalse(Books.objects.filter(title="Must not become a book").exists())

    def test_user_without_category_permission_cannot_create_one(self):
        self.client.force_login(self.customer)

        self.client.post(
            reverse("index"),
            {"add_category": "1", "name": "Forbidden", "title": "Must not become a book"},
        )

        self.assertFalse(Category.objects.filter(name="Forbidden").exists())
        self.assertFalse(Books.objects.filter(title="Must not become a book").exists())

    def test_anonymous_user_cannot_create_category(self):
        response = self.client.post(
            reverse("index"), {"add_category": "1", "name": "Anonymous"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
        self.assertFalse(Category.objects.filter(name="Anonymous").exists())

    def test_invalid_category_submission_creates_neither_category_nor_book(self):
        self.client.force_login(self.worker)

        self.client.post(
            reverse("index"),
            {"add_category": "1", "name": "", "title": "Must not become a book"},
        )

        self.assertFalse(Category.objects.exists())
        self.assertFalse(Books.objects.filter(title="Must not become a book").exists())

    def test_book_creation_without_category_marker_still_works(self):
        self.client.force_login(self.worker)

        response = self.client.post(
            reverse("index"), {"title": "New book", "status": "availble"}
        )

        self.assertRedirects(response, reverse("index"))
        self.assertTrue(Books.objects.filter(title="New book").exists())
        self.assertFalse(Category.objects.filter(name="New book").exists())


class PermissionAwareControlsTests(TestCase):
    def setUp(self):
        self.book = Books.objects.create(title="Public catalog book")
        self.customer = User.objects.create_user(username="ui-reader", password="test-pass")
        self.worker = User.objects.create_user(username="ui-worker", password="test-pass")
        self.worker.user_permissions.add(
            Permission.objects.get(codename="add_books"),
            Permission.objects.get(codename="change_books"),
            Permission.objects.get(codename="add_category"),
        )
        self.book_creator = User.objects.create_user(username="ui-creator", password="test-pass")
        self.book_creator.user_permissions.add(Permission.objects.get(codename="add_books"))
        self.admin = User.objects.create_superuser(
            username="ui-admin", email="ui-admin@example.com", password="test-pass"
        )

    def test_customer_sees_public_catalog_but_no_write_controls(self):
        self.client.force_login(self.customer)

        dashboard = self.client.get(reverse("index"))
        public_catalog = self.client.get(reverse("books"))

        self.assertEqual(dashboard.status_code, 200)
        self.assertNotContains(dashboard, 'id="add-book-dialog"')
        self.assertNotContains(dashboard, 'name="add_category"')
        self.assertNotContains(dashboard, reverse("update", args=[self.book.pk]))
        self.assertNotContains(dashboard, reverse("delete", args=[self.book.pk]))
        self.assertEqual(public_catalog.status_code, 200)
        self.assertContains(public_catalog, self.book.title)
        self.assertNotContains(public_catalog, 'name="add_category"')
        self.assertNotIn("form", public_catalog.context)
        self.assertIn("cat_form", public_catalog.context)

    def test_worker_sees_only_controls_granted_by_permissions(self):
        self.client.force_login(self.worker)

        response = self.client.get(reverse("index"))

        self.assertContains(response, 'id="add-book-dialog"')
        self.assertContains(response, 'name="add_category"')
        self.assertContains(response, reverse("update", args=[self.book.pk]))
        self.assertNotContains(response, reverse("delete", args=[self.book.pk]))
        self.assertNotContains(response, 'id="bookform"')
        self.assertEqual(response.content.decode().count('name="title"'), 1)

    def test_book_creator_does_not_see_category_or_book_edit_controls(self):
        self.client.force_login(self.book_creator)

        response = self.client.get(reverse("index"))

        self.assertContains(response, 'id="add-book-dialog"')
        self.assertNotContains(response, 'name="add_category"')
        self.assertNotContains(response, reverse("update", args=[self.book.pk]))
        self.assertNotContains(response, reverse("delete", args=[self.book.pk]))

    def test_superuser_keeps_all_catalog_controls_and_admin_access(self):
        self.client.force_login(self.admin)

        dashboard = self.client.get(reverse("index"))

        self.assertContains(dashboard, 'id="add-book-dialog"')
        self.assertContains(dashboard, 'name="add_category"')
        self.assertContains(dashboard, reverse("update", args=[self.book.pk]))
        self.assertContains(dashboard, reverse("delete", args=[self.book.pk]))
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)


class BookCoverTemplateTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cover-reader", password="test-pass")
        self.client.force_login(self.customer)
        image = BytesIO()
        Image.new("RGB", (1, 1), color="red").save(image, format="PNG")
        with patch(
            "django.core.files.storage.FileSystemStorage.save",
            return_value="photos/cover.png",
        ):
            self.covered_book = Books.objects.create(
                title="Book with cover",
                photo_book=SimpleUploadedFile(
                    "cover.png",
                    image.getvalue(),
                    content_type="image/png",
                ),
            )
        self.coverless_book = Books.objects.create(title="Book without cover")

    def test_both_listing_pages_render_books_with_and_without_cover_images(self):
        for page_name in ("index", "books"):
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'class="book-cover-image"')
                self.assertContains(response, 'class="book-cover-placeholder"')
                self.assertContains(response, self.covered_book.title)
                self.assertContains(response, self.coverless_book.title)
                self.assertContains(response, self.covered_book.photo_book.url)
                self.assertContains(response, 'alt="غلاف كتاب Book with cover"')


class SharedTemplateJavaScriptTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="script-reader", password="test-pass")
        self.client.force_login(user)

    def test_shared_layout_loads_local_assets_without_dashboard_code_on_public_page(self):
        for page_name in ("index", "books"):
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "/static/dist/css/dashboard.css")
                self.assertContains(response, "/static/dist/js/dashboard.js")
                self.assertNotContains(response, "jquery_datepacker")
                self.assertNotContains(response, "/static/https%3A/")
                self.assertNotContains(response, "new Chart(")

    def test_dashboard_chart_scripts_load_only_when_chart_data_exists(self):
        Books.objects.create(title="Available chart book", status="availble")
        Books.objects.create(title="Sold chart book", status="sold", price=12)
        Books.objects.create(title="Rented chart book", status="rental", total_rental=5)
        dashboard = self.client.get(reverse("index"))
        public_catalog = self.client.get(reverse("books"))

        self.assertContains(dashboard, 'id="sales-chart"')
        self.assertContains(dashboard, 'id="status-chart"')
        self.assertContains(dashboard, "/static/plugins/chart.js/Chart.min.js")
        self.assertContains(dashboard, "/static/dist/js/dashboard.js")
        self.assertNotContains(public_catalog, "/static/plugins/chart.js/Chart.min.js")
        self.assertNotContains(public_catalog, "new Chart(")

    def test_empty_dashboard_shows_chart_empty_states(self):
        response = self.client.get(reverse("index"))

        self.assertNotContains(response, 'id="sales-chart"')
        self.assertNotContains(response, 'id="status-chart"')
        self.assertEqual(response.content.decode().count('class="empty-chart"'), 2)


class SecretKeyConfigurationTests(SimpleTestCase):
    @staticmethod
    def run_settings_import(*, debug, secret_key=None, code="import library.settings"):
        env = os.environ.copy()
        env["DJANGO_DEBUG"] = debug
        env.pop("DJANGO_SECRET_KEY", None)
        if secret_key is not None:
            env["DJANGO_SECRET_KEY"] = secret_key
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_production_requires_secret_key(self):
        result = self.run_settings_import(debug="false")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY must be set", result.stderr)

    def test_supplied_secret_key_is_used(self):
        result = self.run_settings_import(
            debug="false",
            secret_key="test-only-configured-secret",
            code=(
                "import os; import library.settings; "
                "assert library.settings.SECRET_KEY == os.environ['DJANGO_SECRET_KEY']"
            ),
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_local_debug_configuration_works_without_secret_key(self):
        result = self.run_settings_import(
            debug="true",
            code=(
                "import library.settings; assert library.settings.DEBUG; "
                "assert library.settings.SECRET_KEY"
            ),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
