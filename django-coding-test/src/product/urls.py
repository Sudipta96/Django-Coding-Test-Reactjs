from django.urls import path
from django.views.generic import TemplateView

from product.views import product
from product.views.product import CreateProductView
from product.views.variant import VariantView, VariantCreateView, VariantEditView

app_name = "product"

urlpatterns = [
    # Variants URLs
    path('variants/', VariantView.as_view(), name='variants'),
    path('variant/create', VariantCreateView.as_view(), name='create.variant'),
    path('variant/<int:id>/edit', VariantEditView.as_view(), name='update.variant'),

    # Products URLs
    path('create/', CreateProductView.as_view(), name='create.product'),

    path('list/', product.product_list, name='list.product'),

    path("filter/", product.product_filter_view, name="filter.product"),

    path('api/create/', product.create_product),
    path('api/create/<int:product_id>/upload_images/', product.ProductImageUploadView.as_view(), name='upload_images'),
    path('api/create/product-variants/', product.create_product_variant, name="create_product_variant"),
    path('api/create/product-variant-prices/', product.create_product_variant_price, name="create_product_variant_prices"),
]


