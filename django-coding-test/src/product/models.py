from django.db import models
from config.g_model import TimeStampMixin


# Create your models here.
class Variant(TimeStampMixin):
    title = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class Product(TimeStampMixin):
    title = models.CharField(max_length=255)
    sku = models.SlugField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.id}. {self.title}"


class ProductImage(TimeStampMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file_path = models.URLField()

    def __str__(self):
        return self.product.title


class ProductVariant(TimeStampMixin):
    variant_title = models.CharField(max_length=255)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_product_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_variant_items")
    
    def __str__(self):
        return f"{self.id}. {self.product.title}-{self.variant.title}-{self.variant_title}"
   
class ProductVariantPrice(TimeStampMixin):
    product_variant_one = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True,
                                            related_name='product_variant_one')
    product_variant_two = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True,
                                            related_name='product_variant_two')
    product_variant_three = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True,
                                              related_name='product_variant_three')
    price = models.FloatField()
    stock = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_item_variation_price")

    def __str__(self):
        if self.product_variant_one is not None:
            variant_one = self.product_variant_one.variant_title
        else:
            variant_one = ""
        if self.product_variant_two is not None:
            variant_two = self.product_variant_two.variant_title
        else:
            variant_two = ""
        if self.product_variant_three is not None:
            variant_three = self.product_variant_three.variant_title
        else:
            variant_three = ""
        return f"{self.id}. {self.product.title}  Combination: {variant_one}/{variant_two}/{variant_three}   Price: {self.price}   Stock: {self.stock}"
