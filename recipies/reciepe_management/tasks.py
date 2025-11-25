from celery import shared_task
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from .models import ReciepeImagess
from authentication.models import UserDetails
from django.core.mail import send_mail
from django.conf import settings



@shared_task
def compress_recipe_image(image_id):
    try:
        img_obj = ReciepeImagess.objects.get(id=image_id)
        image = Image.open(img_obj.image)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        max_size = (1024, 1024)
        image.thumbnail(max_size)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", optimize=True, quality=70)
        buffer.seek(0)

        img_obj.image.save(
            f"{img_obj.image.name}_compressed",
            ContentFile(buffer.read()),
            save=True
        )

        return f"Compressed image: {image_id}"

    except Exception as e:
        return str(e)

@shared_task
def send_daily_emails():
    subject = "Daily recipes — what's new"
    message = "Hi Seller! Please add dishes to your menu..."
    from_email = settings.DEFAULT_FROM_EMAIL

    user_det = UserDetails.objects.filter(user_type = 'seller')

    recipient_list = [user.user.email for user in user_det]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    print("Email sent!")