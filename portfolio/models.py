"""Models for the portfolio: categories of work, project groupings, and photos."""

from django.db import models
from django.urls import reverse

from .images import DISPLAY_SIZE, THUMBNAIL_SIZE, resize_image

class Category(models.Model):
    """A type of work with its own gallery page, e.g. Stair Rails or Ceilings."""

    # Database columns:
    name = models.CharField(max_length=100) # Name of Category: Stair rails, wall accents, etc.
    slug = models.SlugField(unique=True) # URL text, no two Categories can share one
    description = models.TextField(blank=True) 
    order = models.PositiveIntegerField(default=0)


    class Meta:
        ordering = ["order", "name"] # whenever you fetch Categories, sort by order, break ties by name
        verbose_name_plural = "categories" # categorys -> categories 


    # Method to return string representation of Category
    def __str__(self):
        return self.name


    def get_absolute_url(self):
        """The category's gallery page URL, e.g. /work/ceilings/."""
        return reverse("portfolio:category", args=[self.slug])
    

    @property
    def cover(self):
        """Returns the cover photo of the first published project to be used as Category cover, if available."""
        project = self.projects.filter(is_published=True).first() # Get the first published project in the category
        return project.cover if project else None 
    

# (inherits model from Django's Model to create database table)
class Project(models.Model):
    """A grouping containing multiple photos within a Category"""

    # Database columns:
    category = models.ForeignKey(
        Category, # each Project belongs to a Category
        on_delete=models.PROTECT, # refuse deletion of Category while Project still uses it
        related_name="projects"  # Allows for getting all Projects in a given Category
    )
    title = models.CharField(max_length=200) # Name of Project: Toll Brother's, Sandy Remodel, etc.
    slug = models.SlugField(unique=True) # URL text, cannot have duplicate Projects
    description = models.TextField(blank=True) 
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True) # T/F column for admin to make visible
    created_at = models.DateTimeField(auto_now_add=True) # Set once when row is created
    updated_at = models.DateTimeField(auto_now=True) # Set every time the row is saved


    class Meta:
        ordering = ["order", "title"] # whenever you fetch Projects, sort by order, break ties by title


    # Method to return string representation of Project
    def __str__(self):
        return self.title


    # Get the first photo in the Project for the thumbnail
    @property # allows for using method as if it were a field: project.cover
    def cover(self):
        """The first photo is the thumbnail shown in the gallery grid"""
        return self.photos.first()


class Photo(models.Model):
    """Represents a photo within a Project"""

    # Database columns:
    project = models.ForeignKey(
        Project, # each Photo belongs to a Project
        on_delete=models.CASCADE, # on deletion of a project, delete photos
        related_name="photos" # Allows for getting all Photos in a given Project
    )
    image = models.ImageField(upload_to="projects/%Y/%m/") # store image file path, ex: projects/2026/10/
    thumbnail = models.ImageField(
        upload_to="projects/%Y/%m/thumbs/", # keep thumbnails in their own subfolder
        blank=True, 
        editable=False # hide from admin forms, thumbnails are generated
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True) # Store when row is created and photo is uploaded


    class Meta:
        ordering = ["order", "uploaded_at" ] # whenever you fetch photos, sort by order, break ties by uploaded_at


    # Method to return string representation of Photo, ex: Sandy House Ceiling - photo 3
    def __str__(self):
        return f"{self.project.title} - photo {self.order}" 


    @property
    def thumbnail_url(self):
        """Returns the thumbnail URL if available, if not returns full image URL"""
        return (self.thumbnail or  self.image).url


    # Method to override Model.save() to call image_processing method
    def save(self, *args, **kwargs):
        # Only process a newly uploaded file, not every time the photo is updated
        if self.image and not self.image._committed:
            self.thumbnail = resize_image(self.image, THUMBNAIL_SIZE)
            self.image = resize_image(self.image, DISPLAY_SIZE)
        super().save(*args, **kwargs) # Call Djangos orginal save()

    