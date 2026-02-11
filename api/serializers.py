from rest_framework import serializers
from business.models import Customer, Order, Remission, Sale, CreditAssignment

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        
class RemissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remission
        fields = [
            'id',
            'order',
            'folio',
            'status',
            'created_at'
        ]
        
class SaleSerializer(serializers.ModelSerializer):
    
    total = serializers.ReadOnlyField()
    
    class Meta:
        model = Sale
        fields = [
            'id',
            'remission',
            'subtotal',
            'tax',
            'total',
            'created_at'
        ]

class CreditAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditAssignment
        fields = '__all__'
        
        