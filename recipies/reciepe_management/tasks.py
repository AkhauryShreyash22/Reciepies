from celery import shared_task
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from .models import ReciepeImagess
from authentication.models import UserDetails
from django.core.mail import send_mail
from django.conf import settings
import boto3
from django.contrib.auth import get_user_model
from datetime import datetime
import csv
import io


User = get_user_model()




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

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None),
        region_name=getattr(settings, "AWS_S3_REGION_NAME", "us-east-1"),
    )

@shared_task
def export_users_weekly():
    users = User.objects.all().values("id", "username", "email")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Username", "Email"])
    for u in users:
        writer.writerow([u["id"], u["username"], u["email"]])
    csv_bytes = output.getvalue().encode("utf-8")
    s3 = get_s3_client()
    file_name = f"weekly_exports/users_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_name,
        Body=csv_bytes,
        ContentType="text/csv",
    )
    return {"status": "success", "file": file_name}