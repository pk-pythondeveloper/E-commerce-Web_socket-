from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CreateOrder(APIView):
    def post(self, request):
        pid = request.data.get('product')
        qty = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, pk=pid)
        if product.stock < qty:
            return Response({'message': 'insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        total = product.price * qty
        order = Order.objects.create(product=product, quantity=qty, total_price=total)
        product.stock = product.stock - qty
        product.save()
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('chat', {
                'type': 'chat.message',
                'message': f'Order created: {order.id} status={order.status}'
            })
        except Exception:
            pass
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetail(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


def index(request):
    return render(request, 'shop/index.html')
