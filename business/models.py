from django.db import models, transaction
from django.db.models import Sum
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    folio = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Remission(models.Model):
    """
    Modelo que gestiona las remisiones de una orden.
    Maneja los estados 'open' y 'closed' y aplica las reglas de validación de cierre.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='remissions')
    folio = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def close(self):
        """
        Ejecuta el cierre de la remisión de forma atómica.
        
        Reglas de validación:
        1. Requiere al menos una venta asociada.
        2. El total de créditos no debe exceder el total de ventas.
        """
        with transaction.atomic():
            sales_data = self.sales.aggregate(
                total_subtotal = Sum('subtotal'),
                total_tax = Sum('tax')
            )
        
            total_sales = (sales_data['total_subtotal'] or 0) + (sales_data['total_tax'] or 0)
            total_credits = self.credits.aggregate(total=Sum('amount'))['total'] or 0
            sales_count = self.sales.count()
            
            if sales_count == 0:
                raise ValidationError("No es posible cerrar una remisión si no tiene al menos 1 venta")
            
            if total_credits > total_sales:
                raise ValidationError(
                    f"No es posible cerrar la remisión debido a que la suma de créditos ({total_credits}) "
                    f"excede del total vendido ({total_sales})"
                )
                
            self.status = 'closed'
            self.save()
    
class Sale(models.Model):
    """
    Registra las ventas individuales asociadas a una remisión.
    Asegura que los montos de subtotal e impuestos no sean negativos.
    El total se calcula como la suma de subtotal e impuestos para mantener la consistencia de los datos.
    """
    remission = models.ForeignKey(Remission, on_delete=models.CASCADE, related_name='sales')
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]              
    )
    tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]              
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total(self):
        return self.subtotal + self.tax
    
class CreditAssignment(models.Model):
    remission = models.ForeignKey(Remission,on_delete=models.CASCADE, related_name='credits')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
