from django.db import models
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_COMPLETED = 'Completed'
    STATUS_FAILED = 'Failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old = Order.objects.filter(pk=self.pk).first()
            if old:
                old_status = old.status

        super().save(*args, **kwargs)

        if old_status != self.status:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'order_{self.pk}',
                {'type': 'order.update', 'order_id': self.pk, 'status': self.status},
            )

    def __str__(self):
        return f'Order {self.pk} - {self.product.name}'


class Payment(models.Model):
    STATUS_INIT = 'Initiated'
    STATUS_SUCCESS = 'Success'
    STATUS_FAIL = 'Failure'
    STATUS_CHOICES = [
        (STATUS_INIT, 'Initiated'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAIL, 'Failure'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INIT)
    payment_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == self.STATUS_SUCCESS:
            order = self.order
            order.status = Order.STATUS_COMPLETED
            order.save()

    def __str__(self):
        return f'Payment {self.payment_id} - {self.status}'
