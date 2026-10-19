"""Define how Models appear in admin panel"""

from django.contrib import admin
from django.db.models import Max
from django.utils.html import format_html

from .forms import ProjectAdminForm
from .models import Category, Project, Photo

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Override for admin behavior. Show the Category model in the admin, using the settings in the class"""
    
    # configuration options
    list_display = ["name", "order"] # display Categories name and order columns
    list_editable = ["order"] # allow for editing order
    prepopulated_fields = {"slug": ["name"]} # turns Fireplace Mantels into fireplace-mantels

# Use TabularInlin (inherited from admin) to display a compact table, one photo per row
class PhotoInline(admin.TabularInline):
    """Inline to make project's photos appear on the project's edit page"""

    model = Photo
    extra = 0 # Bulk upload replaces the empty rows; "Add another Photo" still works
    fields = ["preview", "image", "caption", "order"] # which columns appear
    readonly_fields = ["preview"] # preview is display-only

    def preview (self, photo):
        """Method called for each photo row for display"""

        # use thumbnail for preview
        image = photo.thumbnail or photo.image
        if photo.image: # if theres an image, build <img> tag.
            return format_html('<img src="{}"  style="height: 80px">', image.url)
        return "" # show nothing for empty rows

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Override for admin behavior. Show Project model in admin, using the settings in the class"""

    # configuration options
    form = ProjectAdminForm
    list_display = ["title", "category", "order", "is_published"] # diplay Project's title, category, order, and is_published columns
    list_editable = ["order", "is_published"] 
    list_filter = ["category", "is_published"] # side bar to filter based on category 
    search_fields = ["title", "description"] # search box to search titles and descriptions
    prepopulated_fields = {"slug": ["title"]} # turns Sandy House Ceiling into sandy-house-ceiling
    inlines = [PhotoInline] # attach photo table to each project's page


    def save_related(self, request, form, formsets, change):
        """After saving the project and its inline photos, add any bulk-uploaded photos."""
        super().save_related(request, form, formsets, change)

        files = sorted(form.cleaned_data["upload_photos"], key=lambda file: file.name)
        current_max = form.instance.photos.aggregate(Max("order"))["order__max"]
        next_order = (current_max or 0) + 1

        for offset, file in enumerate(files):
            Photo.objects.create(project=form.instance, image=file, order=next_order + offset)

        if files:
            self.message_user(request, f"Added {len(files)} photo(s).")

