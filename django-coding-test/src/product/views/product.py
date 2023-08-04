from django.views import generic
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from product.models import Variant, Product, ProductVariant, ProductVariantPrice, ProductImage
from ..serializers import ProductSerializer, VariantSerializer, ProductVariantSerializer, ProductVariantPriceSerializer, ProductImageSerializer
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import OuterRef, Subquery
from django.utils import timezone


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    


def product_list(request):
    products = Product.objects.all()

    # Number of items to display per page
    items_per_page = 2

    paginator = Paginator(products, items_per_page)
    page_number = request.GET.get('page')

    try:
        paginated_products = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        paginated_products = paginator.get_page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), show the last page
        paginated_products = paginator.get_page(paginator.num_pages)
    
     # Calculate the starting and ending item numbers in the current page
    start_item_number = (paginated_products.number - 1) * items_per_page + 1
    end_item_number = start_item_number + len(paginated_products) - 1

    # Calculate the range of pages to display
    current_page = paginated_products.number
    num_pages = paginator.num_pages
    page_range = range(max(1, current_page - 2), min(current_page + 3, num_pages + 1))
   
    variants = Variant.objects.all()

    # Subquery to get the latest ProductVariant for each variant_title
    latest_variant_subquery = ProductVariant.objects.filter(
        variant_title=OuterRef('variant_title')
    ).order_by('-created_at').values('id')[:1]

    # Get distinct ProductVariant objects by variant_title
    distinct_variants = ProductVariant.objects.filter(
        id__in=Subquery(latest_variant_subquery)
    )


    context = {
        "products": paginated_products,
        "start_item_number": start_item_number,
        "end_item_number": end_item_number,
        "variants": variants,
        "distinct_variants": distinct_variants,
        "page": "product_list",
    }
    return render(request, "products/list.html", context=context)


def product_filter_view(request):
    title = request.GET.get('title', '')
    variant = request.GET.get('variant', '')
    price_from = request.GET.get('price_from', '')
    price_to = request.GET.get('price_to', '')
    date_str = request.GET.get('date', '')

    variants = Variant.objects.all()
    # Subquery to get the latest ProductVariant for each variant_title
    latest_variant_subquery = ProductVariant.objects.filter(
        variant_title=OuterRef('variant_title')
    ).order_by('-created_at').values('id')[:1]

    # Get distinct ProductVariant objects by variant_title
    distinct_variants = ProductVariant.objects.filter(
        id__in=Subquery(latest_variant_subquery)
    )
    
    # Start with the full queryset of products
    queryset = Product.objects.all()
    product_variation_price_qs = None

    # Filter based on title (if provided)
    if title:
        queryset = queryset.filter(title__icontains=title)
    
    if variant:
        variant_qs = ProductVariant.objects.filter(variant_title=variant)
        print("variant_qs")
        print(variant_qs)

        # Extract unique product IDs from the queryset using distinct()
        unique_product_ids = variant_qs.values_list('product__id', flat=True).distinct()
       
        # Convert the unique_product_ids queryset to a list, if needed
        unique_product_ids_list = list(unique_product_ids)
        print(unique_product_ids_list)
       
        # Now, filter the Product model using the unique product IDs
        queryset = queryset.filter(id__in=unique_product_ids_list)

        product_variation_price_qs = ProductVariantPrice.objects.filter(
                    Q(product_variant_one__variant_title=variant) |
                    Q(product_variant_two__variant_title=variant) |
                    Q(product_variant_three__variant_title=variant)
                )

    # Filter based on price range (if provided)
    if price_from or price_to:
        if price_from:
            product_variation_price_qs = ProductVariantPrice.objects.filter(
                    Q(price__gte=float(price_from))
                )
        
        if price_to:
            product_variation_price_qs = ProductVariantPrice.objects.filter(
                Q(price__lte=float(price_to))
                )
        if price_from and price_to:
            product_variation_price_qs = ProductVariantPrice.objects.filter(
                    Q(price__gte=float(price_from)) & Q(price__lte=float(price_to))
                )
        
        if variant:
            product_variation_price_qs =  product_variation_price_qs.filter(
                    Q(product_variant_one__variant_title=variant) |
                    Q(product_variant_two__variant_title=variant) |
                    Q(product_variant_three__variant_title=variant)
            )

        # Extract unique product IDs from the queryset using distinct()
        unique_product_ids = product_variation_price_qs.values_list('product__id', flat=True).distinct()
       
        # Convert the unique_product_ids queryset to a list, if needed
        unique_product_ids_list = list(unique_product_ids)
       
        # Now, filter the Product model using the unique product IDs
        queryset = queryset.filter(id__in=unique_product_ids_list)

    # Filter based on date (if provided)
    if date_str:
        date = timezone.datetime.strptime(date_str, "%Y-%m-%d")
    
        # to filter by date within the whole day (from midnight to the next midnight).
        queryset = queryset.filter(created_at__range=(date, date + timezone.timedelta(days=1)))
       
    context = {
        'products': queryset,
        "variants": variants,
        "distinct_variants": distinct_variants,
        "page": "product_filter",
        "product_variation_price_qs": product_variation_price_qs,
    }

    return render(request, 'products/list.html', context)

@api_view(['POST'])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_product_variant(request):
    serializer = ProductVariantSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_product_variant_price(request):
    serializer = ProductVariantPriceSerializer(data=request.data)
    print("Product Variation Price")
    # print(serializer)

    title = request.data["title"]
    print(title)
    title_array = title.split('/')
    if title_array[-1] == '':
        title_array.pop()

    product_id = request.data["product"]
    price = request.data["price"]
    stock = request.data["stock"]
    print(title_array)

    product_obj = Product.objects.filter(id=product_id).first()

    product_variant_qs = []
    print("loop through variant_tags")
    for variant in title_array:
        print(f"Variant: {variant}")
        product_variants = ProductVariant.objects.filter(variant_title=variant, product__id=product_id)
        print(f"Product Variants: {product_variants}")
        if len(product_variants) > 0:
            product_variant_qs.append(product_variants[0])
    print("product variant qs")
    print(product_variant_qs)
    if len(product_variant_qs) == 3:
        ProductVariantPrice.objects.create(
            product_variant_one = product_variant_qs[0],
            product_variant_two = product_variant_qs[1],
            product_variant_three = product_variant_qs[2],
            price = price,
            stock = stock,
            product = product_obj
        )
    if len(product_variant_qs) == 2:
        ProductVariantPrice.objects.create(
            product_variant_one = product_variant_qs[0],
            product_variant_two = product_variant_qs[1],
            price = price,
            stock = stock,
            product = product_obj
        )
    if len(product_variant_qs) == 1:
        ProductVariantPrice.objects.create(
            product_variant_one = product_variant_qs[0],
            price = price,
            stock = stock,
            product = product_obj
        )
     
    if serializer.is_valid():
    #     serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductImageUploadView(APIView):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        files = request.FILES.getlist('file')
        for file in files:
            product_image = ProductImage.objects.create(product=product, file_path=file)
            # You can perform additional processing or validation here if required.

        return Response({'message': f'{len(files)} image(s) uploaded successfully.'})

