from django import forms
from PIL import Image

MAX_IMAGE_MB = 5
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


class MessageSendForm(forms.Form):
    content = forms.CharField(required=False, widget=forms.Textarea)
    image = forms.ImageField(required=False)

    def clean(self):
        cleaned = super().clean()
        content = (cleaned.get("content") or "").strip()
        image = cleaned.get("image")

        if not content and not image:
            raise forms.ValidationError("Please type a message or attach an image.")

        if image:
            # Size check
            if image.size > MAX_IMAGE_MB * 1024 * 1024:
                raise forms.ValidationError(f"Image too large. Max is {MAX_IMAGE_MB}MB.")

            # MIME check (best effort)
            content_type = getattr(image, "content_type", "")
            if content_type and content_type.lower() not in ALLOWED_MIME:
                raise forms.ValidationError("Only JPG, PNG, or WEBP images are allowed.")

            # Pillow validation (actually open the file)
            try:
                img = Image.open(image)
                img.verify()
            except Exception:
                raise forms.ValidationError("Invalid image file.")

        return cleaned
