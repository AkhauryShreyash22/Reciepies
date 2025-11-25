from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Reciepe(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    reciepe_name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.reciepe_name
    
class ReciepeImagess(models.Model):
    reciepe = models.ForeignKey(Reciepe, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='reciepe_images/')

    def __str__(self):
        return f"Image for {self.reciepe.reciepe_name}"


class ReciepeRating(models.Model):
    reciepe = models.ForeignKey(Reciepe, on_delete=models.CASCADE, related_name="rating")
    rating = models.IntegerField()
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Rating for {self.reciepe.reciepe_name} is {self.rating} for user {self.customer}"