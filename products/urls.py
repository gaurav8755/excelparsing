from django.urls import path
from .views import products_list, upload_products

urlpatterns = [
    #home page product list
    path('', products_list, name='products_list'),
    #endpoin to handle upload post request
    path('upload/', upload_products, name='upload_products'),
]