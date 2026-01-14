from django.urls import re_path
from shop import consumers

# accept ws/shop and ws/shop/ (trailing slash optional)
websocket_urlpatterns = [
    re_path(r'ws/shop/?$', consumers.ShopConsumer.as_asgi()),
]
