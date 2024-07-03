from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from login.models import CustomUser

# Create your models here.
class Hospital(models.Model):
    hospital_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.hospital_name

class BloodInventory(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.blood_group} - {self.quantity} units at {self.hospital}"
    
class Donor(models.Model):
    donor_name = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BloodInventory.BLOOD_GROUPS)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    donor_city = models.CharField(max_length=100, default="city1")
    donor_area = models.CharField(max_length=500, default="area1")
    donor_phone_number = models.CharField(max_length=15, default="1234567890")
    last_donation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.donor_name} : ({self.blood_group})"
    
    def donate_blood(self, quantity):
        self.last_donation_date = timezone.now().date()
        self.save()

        inventory, created = BloodInventory.objects.get_or_create(
            hospital=self.hospital,
            blood_group=self.blood_group,
            defaults={'quantity': 0}
        )
        inventory.quantity += quantity
        print("blood save")
        inventory.save()

    def save(self, *args, **kwargs):
        # Check if this is a new donor entry or an update
        if self.pk is None:
            # New donor entry, set the donation date to today
            self.last_donation_date = timezone.now().date()
            super(Donor, self).save(*args, **kwargs)
            self.donate_blood(0)  # Assume 1 unit of blood is donated by default
        else:
            super(Donor, self).save(*args, **kwargs)

class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3, choices=BloodInventory.BLOOD_GROUPS)
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request for {self.quantity} units of {self.blood_group} at {self.hospital}"