from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, OrderViewSet, RemissionViewSet

router = DefaultRouter()

router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'remissions', RemissionViewSet)
router.register(r'reports/daily-sales', DailySalesReportViewSet, basename='daily-sales')

urlpatterns = [
    path('', include(router.urls)),
]