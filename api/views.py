from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count
from business.models import Customer, Order, Remission
from .serializers import CustomerSerializer, OrderSerializer, RemissionSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
class RemissionViewSet(viewsets.MidelViewSet):
    queryset = Remission.objects.all()
    serializer_class = RemissionSerializer
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        remission = self.get_object()
        try:
            remission.close()
            return Response({'message': 'Remisión cerrada'}, status= status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        remission = self.get_object()
        
        sales_data = remission.sales.aggregate(
            total_sales = Sum('subtotal') + Sum('tax'),
            sales_count = Count('id')
        )
        
        total_credits = remission.credits.aggregate(total=Sum('amount'))['total'] or 0
        total_sales = sales_data['total_sales'] or 0
        
        return Response({
            'total_sales': total_sales,
            'total_credits': total_credits,
            'balance': total_sales - total_credits,
            'sales_count': sales_data['sales_count']
        })