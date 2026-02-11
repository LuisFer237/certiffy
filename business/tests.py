from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from business.models import Customer, Order, Remission, Sale, CreditAssignment

class BusinessLogicTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Client", is_active=True)
        self.order = Order.objects.create(customer=self.customer, folio="ORD-001")
        self.remission = Remission.objects.create(order=self.order, folio="REM-001", status='open')

    def test_close_fails_without_sales(self):
        with self.assertRaises(ValidationError) as cm:
            self.remission.close()
        self.assertIn("al menos 1 Sale", str(cm.exception))

    def test_close_fails_if_credits_exceed_sales(self):
        Sale.objects.create(remission=self.remission, subtotal=Decimal('100.00'), tax=Decimal('16.00'))
        CreditAssignment.objects.create(remission=self.remission, amount=Decimal('120.00'), reason="Over credit")
        
        with self.assertRaises(ValidationError) as cm:
            self.remission.close()
        self.assertIn("excede", str(cm.exception))

    def test_daily_report_grouping(self):

        Sale.objects.create(remission=self.remission, subtotal=Decimal('100.00'), tax=Decimal('16.00'))
        
        yesterday = timezone.now() - timedelta(days=1)
        sale_old = Sale.objects.create(remission=self.remission, subtotal=Decimal('200.00'), tax=Decimal('32.00'))
        sale_old.created_at = yesterday
        sale_old.save()

        from django.urls import reverse
        url = reverse('daily-sales-list')
        response = self.client.get(url, {'from': yesterday.date(), 'to': timezone.now().date()})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2) 