import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import shop.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storeproj.settings')
django.setup()

django_asgi = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi,
    'websocket': AuthMiddlewareStack(URLRouter(shop.routing.websocket_urlpatterns)),
})
