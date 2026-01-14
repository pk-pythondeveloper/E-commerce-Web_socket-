# E-commerce Demo 

Short guide to run and test the project locally.

Prerequisites
- Python 3.10+ installed
- Git (optional)

Quick setup (Windows, PowerShell)
1. Create virtual env and install dependencies
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Database + static
```powershell
python manage.py migrate
python manage.py createsuperuser   # For admin
python manage.py collectstatic --noinput
```
3. Start ASGI server
```powershell
uvicorn storeproj.asgi:application --host 127.0.0.1 --port 8000 --reload

```

What to test
- Open the app: http://127.0.0.1:8000/ — product list and simple UI.
- Admin: http://127.0.0.1:8000/admin/ (login with superuser).

REST API
- GET /api/products/ — list products
- GET /api/products/<id>/ — product detail
- POST /api/orders/ — create order (JSON body: {"product":id,"quantity":n})
  - Include `X-CSRFToken` header or use browser-based UI which handles CSRF.
- GET /api/orders/<id>/ — order detail

WebSocket (real-time)
- Connect to ws://127.0.0.1:8000/ws/shop/
- Send JSON frames:
  - Join order: {"action":"join_order","order_id":1}
  - Chat: {"action":"chat","message":"hello"}
- Incoming frames:
  - Order update: {"type":"order_update","order_id":1,"status":"Completed"}
  - Chat: {"type":"chat","message":"..."}

Files of interest
- `shop/models.py` — Product, Order, Payment and order status notification logic.
- `shop/views.py` — API endpoints and order creation.
- `shop/consumers.py` — Channels consumer handling WS chat and order updates.
- `shop/static/shop/main.js` — Frontend JS: opens WS, posts orders, shows messages.
- `storeproj/asgi.py` & `storeproj/routing.py` — ASGI and 

Packaging for reviewer

```powershell
# from project root
Remove-Item -Recurse -Force .venv
Compress-Archive -Path * -DestinationPath ..\ecommerce_website_package.zip
```

Notes
- Use Uvicorn/Daphne (ASGI) — the built-in WSGI server does not support WebSockets.
- In-memory channel layer is for dev only. Use Redis for multi-worker setups.

Run & Test (WebSocket)
- Start the ASGI server (from project root):
```powershell
uvicorn storeproj.asgi:application --host 127.0.0.1 --port 8000 --reload
```
- Browser (quick): open `http://127.0.0.1:8000/`, open DevTools → Console and run:
```javascript
const sock = new WebSocket('ws://127.0.0.1:8000/ws/shop/');
sock.onopen = ()=>console.log('open');
sock.onmessage = e=>console.log('msg', e.data);
sock.onerror = e=>console.error(e);
// join an order (replace id) and receive updates
sock.send(JSON.stringify({action:'join_order', order_id: 1}));
// chat
sock.send(JSON.stringify({action:'chat', message:'hello'}));
```
- Postman WebSocket: New → WebSocket request → connect to `ws://127.0.0.1:8000/ws/shop/` and send the same JSON frames.
- wscat (node):
```bash

wscat -c ws://127.0.0.1:8000/ws/shop/
# then type: {"action":"join_order","order_id":1}
```
- End-to-end notification test:
  1. Open two browser tabs to `/` (A and B).
  2. In A create an order using the Buy form (A will auto-join created order).
  3. In B join same order via console or Postman.
  4. In Django admin change that Order's `Status` to `Completed` and save — both tabs should receive an `order_update` message.
