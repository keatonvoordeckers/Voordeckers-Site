"""
Image processing for uploaded photos that involves: 
    - Fixing rotation
    - Strip metadata (GPS coordinates)
    - Resize to create a display version (max 2000px) and a thumbnail version (max 600px)
"""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

DISPLAY_SIZE = (2000, 2000)
THUMBNAIL_SIZE = (600, 600)
JPEG_QUALITY = 85


def resize_image(uploaded, max_size):
    """Return a correctly rotated, metadata-free JPEG that fits within the given max_size"""

    uploaded.seek(0)
    with Image.open(uploaded) as original: # File is closed automatically when this block ends
        # Save color profile, perform rotations, convert to rgb (exclude transparency), and resize
        icc_profile = original.info.get("icc_profile")
        img = ImageOps.exif_transpose(original)
        img = img.convert("RGB")
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save JPEG to memory, then hand bytes to Django
        buffer = BytesIO()
        # Exclude exif= argument to strip metadata like GPS coordinates, camera details and timestamps
        img.save( 
            buffer,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
            icc_profile=icc_profile,
        )

    name = f"{Path(uploaded.name).stem}.jpg" # Takes filename without extension, ex: IMG_1234.HEIC -> IMG_1234.jpg
    return ContentFile(buffer.getvalue(), name=name) # Wrap bytes so ImageField can save.
