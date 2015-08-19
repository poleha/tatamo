from rest_framework.generics import ListCreateAPIView
from discount.api import serializers
from discount.models import Product


class ProductListCreateAPIView(ListCreateAPIView):
    model = Product
    serializer_class = serializers.ProductSerializer