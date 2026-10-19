"""Forms for the portfolio admin."""

from django import forms

from .models import Project


class MultipleFileInput(forms.ClearableFileInput):
    """A file input that lets the user select several files at once."""

    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """An image field that validates and returns a list of images."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean # The parent's clean() validates one image
        if isinstance(data, (list, tuple)):
            return [single_clean(file, initial) for file in data]
        return [single_clean(data, initial)] if data else []


class ProjectAdminForm(forms.ModelForm):
    """The project admin form, plus a field for uploading many photos at once."""

    upload_photos = MultipleImageField(
        required=False,
        help_text="Select several photos at once. They're added in filename order (01.jpg, 02.jpg, ...).",
    )

    class Meta:
        model = Project
        fields = "__all__"