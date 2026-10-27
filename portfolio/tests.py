"""Tests for the portfolio: image processing, models, and gallery pages."""

from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

from .images import resize_image
from .models import Category, Photo, Project


def make_image(name="test.jpg", size=(3000, 1000), exif=None):
    """Build an in-memory JPEG upload, optionally with EXIF metadata."""
    buffer = BytesIO()
    image = Image.new("RGB", size, "white")
    if exif is not None:
        image.save(buffer, format="JPEG", exif=exif)
    else:
        image.save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


def open_result(content_file):
    """Open the processed file returned by resize_image as a Pillow image."""
    return Image.open(BytesIO(content_file.read()))


class ResizeImageTests(SimpleTestCase):
    def test_shrinks_to_fit_max_size(self):
        result = open_result(resize_image(make_image(size=(3000, 1000)), (600, 600)))
        self.assertEqual(result.size, (600, 200))

    def test_strips_gps_and_camera_metadata(self):
        exif = Image.Exif()
        exif[0x010F] = "TestCam"         # Camera make
        exif.get_ifd(0x8825)[1] = "N"    # GPS latitude reference
        result = open_result(resize_image(make_image(exif=exif), (2000, 2000)))
        self.assertEqual(len(result.getexif()), 0)

    def test_rotates_sideways_phone_photos_upright(self):
        exif = Image.Exif()
        exif[0x0112] = 6                 # Orientation: rotate 90 degrees
        result = open_result(resize_image(make_image(size=(300, 100), exif=exif), (2000, 2000)))
        self.assertEqual(result.size, (100, 300))

    def test_renames_to_jpg(self):
        result = resize_image(make_image(name="IMG_1234.png"), (600, 600))
        self.assertEqual(result.name, "IMG_1234.jpg")


class PhotoModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="ceilings") # Created by the seed migration
        self.project = Project.objects.create(category=self.category, title="Oak Beams", slug="oak-beams")

    def test_save_creates_display_image_and_thumbnail(self):
        photo = Photo.objects.create(project=self.project, image=make_image())
        self.assertEqual((photo.image.width, photo.image.height), (2000, 667))
        self.assertEqual((photo.thumbnail.width, photo.thumbnail.height), (600, 200))

    def test_project_cover_is_lowest_order_photo(self):
        Photo.objects.create(project=self.project, image=make_image("b.jpg"), order=2)
        first = Photo.objects.create(project=self.project, image=make_image("a.jpg"), order=1)
        self.assertEqual(self.project.cover, first)

    def test_category_cover_skips_unpublished_projects(self):
        self.project.is_published = False
        self.project.save()
        Photo.objects.create(project=self.project, image=make_image())
        self.assertIsNone(self.category.cover)


class GalleryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.get(slug="ceilings")
        published = Project.objects.create(category=category, title="Oak Beams", slug="oak-beams")
        Photo.objects.create(project=published, image=make_image("1.jpg"), order=1)
        Photo.objects.create(project=published, image=make_image("2.jpg"), order=2)
        hidden = Project.objects.create(
            category=category, title="Secret Job", slug="secret-job", is_published=False
        )
        Photo.objects.create(project=hidden, image=make_image())

    def test_shows_published_projects_with_photo_count(self):
        response = self.client.get(reverse("portfolio:category", args=["ceilings"]))
        self.assertContains(response, "Oak Beams")
        self.assertContains(response, "2 photos")

    def test_hides_unpublished_projects(self):
        response = self.client.get(reverse("portfolio:category", args=["ceilings"]))
        self.assertNotContains(response, "Secret Job")

    def test_unknown_category_returns_404(self):
        response = self.client.get("/work/kitchens/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_gallery_uses_a_fixed_number_of_queries(self):
        # Category + projects + all their photos, however many projects there are
        with self.assertNumQueries(3):
            self.client.get(reverse("portfolio:category", args=["ceilings"]))