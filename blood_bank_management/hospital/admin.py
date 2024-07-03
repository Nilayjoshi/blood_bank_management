from django.contrib import admin
from .models import BloodRequest, Hospital, Donor, BloodInventory

# Register your models here.
class hospitalDetails(admin.ModelAdmin):
    list_display=["hospital_name"]
admin.site.register(Hospital,hospitalDetails)

class donorDetails(admin.ModelAdmin):
    list_display=["donor_name"]
admin.site.register(Donor,donorDetails)

class inventoryDetails(admin.ModelAdmin):
    list_display=["hospital","blood_group"]
admin.site.register(BloodInventory,inventoryDetails)    

class requestsOfBlood(admin.ModelAdmin):
    list_display=["patient"]
admin.site.register(BloodRequest,requestsOfBlood)
