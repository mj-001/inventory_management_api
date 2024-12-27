from django.db import models
from django.contrib.auth.models import PermissionsMixin, User
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from django.contrib.auth.views import LoginView

# Create your models here.
class InventoryItem(models.Model):
    name=models.CharField(max_length=250, null=True)
    description=models.TextField(blank=True,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity=models.PositiveIntegerField(default=0, null=True)
    category=models.CharField(max_length=250, null=True)
    date_added = models.DateTimeField(auto_created=True, null=True)
    last_updated_period=models.DateTimeField(auto_now=True, null=True)
    managed_by=models.ForeignKey(User,on_delete=models.CASCADE, null=True)
    low_stock_alert=models.IntegerField(default=0,null=True)

    def __str__(self):
        return self.name
    
    """
    this is experimantal
    def filter_thresholds(quantity):
        if quantity <= 2:
            return f"Quantity is less than {quantity}"
    """
    
class InventoryFilter(FilterSet):
    name=filters.CharFilter(lookup_expr='icontains')
    category=filters.CharFilter(lookup_expr='icontains')
    price_min=filters.NumberFilter(field_name='price',lookup_expr='gte')
    price_max=filters.NumberFilter(field_name='price',lookup_expr='lte')
    low_stock=filters.BooleanFilter(field_name='low_stock_alert')
    
    def filter_low_stock(querySet,name,value, quantity):
        if value:
            for item in querySet:
                if querySet.filter(quantity=2):
                     # Raise alert logic here
                    print(f"Alert: {item.name} is below the threshold stock of {quantity}. Current stock: {item.quantity}")
        return f"Alert: {item.name} is below the threshold stock of {quantity}. Current stock: {item.quantity}"

class InventoryChangeLog(models.Model):
    item=models.ForeignKey(InventoryItem,on_delete=models.CASCADE)
    changed_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)  
    time_changed=models.DateTimeField(auto_now_add=True)
    changed_quantities=models.IntegerField(null=False)
    

