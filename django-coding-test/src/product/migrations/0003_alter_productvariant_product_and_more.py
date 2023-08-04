# Generated by Django 4.2.4 on 2023-08-03 20:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_alter_productvariantprice_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_variant_item', to='product.product'),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variant_product_item', to='product.variant'),
        ),
    ]
