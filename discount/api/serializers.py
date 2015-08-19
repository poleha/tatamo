from rest_framework.serializers import ModelSerializer
from discount import models


class ProductSerializer(ModelSerializer):
    class Meta:
        model = models.Product
        #fields = ('title', 'body')

