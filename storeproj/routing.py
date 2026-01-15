from django.urls import re_path
from shop import consumers

websocket_urlpatterns = [
    re_path(r'ws/shop/$', consumers.ShopConsumer.as_asgi()),
]
#i am adding comment here