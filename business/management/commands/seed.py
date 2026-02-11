import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from business.models import Customer, Order, Remission, Sale, CreditAssignment

fake = Faker()

class Command(BaseCommand):
    """
    Comando para poblar la base de datos con datos.
    
    Genera una estructura jerárquica de Clientes, Órdenes, Remisiones, Ventas y Créditos
    utilizando la librería Faker para asegurar datos realistas y variabilidad en las fechas,
    lo que permite validar correctamente los reportes diarios.
    """
    help = 'Seed database with random data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        customers = []
        for _ in range(50):
            c = Customer.objects.create(
                name=fake.name(),
                email=fake.email(),
                is_active=True
            )
            customers.append(c)
            
        for i in range(100):
            customer = random.choice(customers)
            order = Order.objects.create(
                customer=customer,
                folio=f"ORD-{fake.unique.bothify(text='####??')}"
            )
            
            remission = Remission.objects.create(
                order=order,
                folio=f"REM-{fake.unique.bothify(text='####??')}",
                status='open'
            )
        
            current_date = fake.date_time_between(
                start_date='-30d', 
                end_date='now', 
                tzinfo=timezone.get_current_timezone()
            )
            
            total_sales_amount = Decimal('0.00')
            for _ in range(random.randint(1,3)):
                subtotal = Decimal(random.uniform(10.0,500.0)).quantize(Decimal('0.00'))
                tax = (subtotal * Decimal('0.16')).quantize(Decimal('0.00'))
                
                sale = Sale.objects.create(
                    remission=remission,
                    subtotal=subtotal,
                    tax=tax
                )
                
                sale.created_at = current_date
                sale.save()
                
                total_sales_amount += (subtotal + tax)
                
            if random.random() > 0.5:
                amount = Decimal(random.uniform(5.0, float(total_sales_amount) * 1.2)).quantize(Decimal('0.00'))
                CreditAssignment.objects.create(
                    remission=remission,
                    amount=amount,
                    reason=fake.sentence()
                )
   
        self.stdout.write(self.style.SUCCESS(f'Database seeding completed successfully.'))