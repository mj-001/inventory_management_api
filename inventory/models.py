from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
import json

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
    #low_stock_alert=models.IntegerField(default=0,null=True)
    inventory_item_history = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def append_to_history(self, field_name, old_value, new_value, user):
        """
        Appends a change to the history field in JSON format.
        """
        change = {
            'field': field_name,
            'old_value': old_value,
            'new_value': new_value,
            'changed_by': user.username,
            'timestamp': timezone.now().isoformat()  # Use timezone.now() from django.utils
        }

        # If the history already exists, append to it; otherwise, start a new history
        if self.inventory_item_history:  # Ensure to use 'inventory_item_history' instead of 'history'
            history_data = json.loads(self.inventory_item_history)  # Load existing history
        else:
            history_data = []

        history_data.append(change)  # Append the new change

        # Update the history field with the new data
        self.inventory_item_history = json.dumps(history_data)


    def save(self, *args, **kwargs):
        """
        Override save method to track changes and update history.
        """
        if self.pk:  # If the instance already exists (i.e., it is being updated)
            original = InventoryItem.objects.get(pk=self.pk)
            
            # Track changes for each field
            if self.name != original.name:
                self.append_to_history('name', original.name, self.name, self.managed_by)
            if self.description != original.description:
                self.append_to_history('description', original.description, self.description, self.managed_by)
            if self.price != original.price:
                self.append_to_history('price', original.price, self.price, self.managed_by)
            if self.quantity != original.quantity:
                self.append_to_history('quantity', original.quantity, self.quantity, self.managed_by)
            if self.category != original.category:
                self.append_to_history('category', original.category, self.category, self.managed_by)

        super().save(*args, **kwargs)  # Call the original save method

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
    

