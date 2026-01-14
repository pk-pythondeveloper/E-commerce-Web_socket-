from django.test import TestCase
from rest_framework.test import APIClient
from shop.models import Product, Order, Payment


class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.prod = Product.objects.create(name='Widget', description='Simple widget', price='9.99', stock=10)

    def test_product_list(self):
        res = self.client.get('/api/products/')
        self.assertEqual(res.status_code, 200)
        items = res.json()
        self.assertTrue(any(i['id'] == self.prod.id for i in items))

    def test_product_detail(self):
        res = self.client.get(f'/api/products/{self.prod.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get('name'), 'Widget')

    def test_create_order_success(self):
        res = self.client.post('/api/orders/', {'product': self.prod.id, 'quantity': 2}, format='json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        order = Order.objects.get(pk=data['id'])
        self.assertEqual(float(order.total_price), float(self.prod.price) * 2)
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.stock, 8)

    def test_create_order_insufficient_stock(self):
        res = self.client.post('/api/orders/', {'product': self.prod.id, 'quantity': 999}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_payment_success_updates_order(self):
        res = self.client.post('/api/orders/', {'product': self.prod.id, 'quantity': 1}, format='json')
        self.assertEqual(res.status_code, 201)
        order_id = res.json()['id']
        order = Order.objects.get(pk=order_id)
        Payment.objects.create(order=order, payment_id='pay_123', status=Payment.STATUS_SUCCESS)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_COMPLETED)
