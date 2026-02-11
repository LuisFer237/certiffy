from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count
from business.models import Customer, Order, Remission, Sale
from .serializers import CustomerSerializer, OrderSerializer, RemissionSerializer
from django.db.models.functions import TruncDate

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de Órdenes.
    Utiliza select_related para optimizar la carga del cliente asociado y evitar N+1.
    """
    queryset = Order.objects.select_related('customer').all()
    serializer_class = OrderSerializer
    
class RemissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de Remisiones.
    Implementa select_related y prefetch_related para optimizar las consultas y evitar N+1.
    """
    queryset = Remission.objects.select_related('order__customer').prefetch_related('sales', 'credits').all()
    serializer_class = RemissionSerializer
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        remission = self.get_object()
        try:
            remission.close()
            return Response({'message': 'Remisión cerrada'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Genera un resumen de la remisión.
        """
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

class DailySalesReportViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        Retorna un listado de ventas agrupado por fecha dentro de un rango determinado.
        """
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        
        if not date_from or not date_to:
            return Response(
                {'error': 'Los parametros "from" y "to" son necesarios para ejecutar esta acción'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        report = (
            Sale.objects.filter(created_at__date__range=[date_from,date_to])
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                total_sales=Sum('subtotal') + Sum('tax'),
                total_tax=Sum('tax'),
                sales_count=Count('id')
            )
            .order_by('date')
        )
        
        return Response(report)