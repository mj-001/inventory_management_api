from django.db import models

# Create your models here.
class InventoryItem(models.Model):
    name=models.CharField(max_length=250)
    description=models.TextField()
    price=models.DecimalField(max_digits=6,decimal_places=2)
    quantity=models.IntegerField()

    def __str__(self):
        return self.name
