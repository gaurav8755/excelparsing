import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, ProductVariation
from django.shortcuts import render
import pytz

def format_datetime(dt):
    # Define the custom date format
    date_format = "%d %B %Y %I:%M %p"
    # Convert datetime to IST timezone
    ist = pytz.timezone('Asia/Kolkata')
    dt_ist = dt.astimezone(ist)  # Convert to IST timezone

    # Format the datetime to desired format
    return dt_ist.strftime(date_format) + " IST"

def products_list(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        products = Product.objects.prefetch_related("variations").all()

        # Manually construct the response data
        data = []
        sno =1
        for product in products:
            variations = product.variations.all()
            product_data = {
                'id': sno,
                'name': product.name,
                # Convert Decimal to string for JSON compatibility
                'lowest_price': str(product.lowest_price),
                'variations': [
                    {
                        'variation_text': variation.variation_text,
                        'stock': variation.stock
                    } for variation in variations
                ],
                'last_updated': format_datetime(product.last_updated)
            }
            data.append(product_data)
            sno+=1

        # Return JsonResponse
        return JsonResponse(data, safe=False)
    return render(request, 'products/products_list.html')


@csrf_exempt
def upload_products(request):
    if request.method == 'POST':
        file = request.FILES.get('file')

        # Check if a file was uploaded
        if not file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        # Validate file type
        if not (file.name.endswith('.xlsx') or file.name.endswith('.xls')):
            return JsonResponse({'error': 'Invalid file type. Only .xls and .xlsx are allowed.'}, status=400)

        # Validate file size
        if file.size > 2 * 1024 * 1024:  # 2 MB
            return JsonResponse({'error': 'File size must not exceed 2 MB'}, status=400)

        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(file)

            # Check required columns
            required_columns = {'Product Name', 'Variation', 'Stock'}
            if not required_columns.issubset(df.columns):
                return JsonResponse({'error': f'Missing required columns: {required_columns - set(df.columns)}'}, status=400)

            # Process each row
            for _, row in df.iterrows():
                product_name = row.get('Product Name')
                variation_text = row.get('Variation')
                stock = row.get('Stock')

                # Check if the row contains valid data
                if pd.isna(product_name) or pd.isna(variation_text) or pd.isna(stock) or not isinstance(stock, (int, float)):
                    return JsonResponse({'error': 'Invalid data in file. Ensure all rows have valid product name, variation, and stock.'}, status=400)

                # Get or create product
                product, created = Product.objects.get_or_create(
                    name=product_name,
                    defaults={'lowest_price': 0,
                              'last_updated': pd.Timestamp.now()}
                )
                if(not created):
                    product.last_updated = pd.Timestamp.now()
                    product.save()

                # Get or create product variation
                product_variation, created = ProductVariation.objects.get_or_create(
                    product=product,
                    variation_text=variation_text,
                    defaults={'stock': stock,
                              'last_updated': pd.Timestamp.now()}
                )

                # Update stock if variation already exists
                if not created:
                    product_variation.stock += stock
                    product_variation.last_updated = pd.Timestamp.now()
                    product_variation.save()

            return JsonResponse({'success': 'Products uploaded successfully'}, status=200)

        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method. Only POST requests are allowed.'}, status=405)
