from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField()

    def __str__(self):
        return self.name

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_text = models.CharField(max_length=255)
    stock = models.PositiveIntegerField()
    last_updated = models.DateTimeField()

    def __str__(self):
        return f"{self.product.name} - {self.variation_text}"
