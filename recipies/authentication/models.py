from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserDetails(models.Model):
    CUSTOMER = "customer"
    SELLER = "seller"
    USER_TYPES = (
        (CUSTOMER, 'Customers'),
        (SELLER, 'Seller'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    mobile = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.email} - {self.user_type} - {self.mobile}"

    def is_seller(self):
        return self.user_type == self.SELLER

    def is_customer(self):
        return self.user_type == self.CUSTOMER