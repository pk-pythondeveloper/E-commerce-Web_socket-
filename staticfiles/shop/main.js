const productsEl = document.getElementById('products');
const messagesEl = document.getElementById('messages');

function addMessage(t){
  const d = document.createElement('div');
  d.textContent = t;
  messagesEl.appendChild(d);
}

fetch('/api/products/').then(r=>r.json()).then(data=>{
  productsEl.innerHTML = '';
  data.forEach(p=>{
    const el = document.createElement('div');
    el.textContent = `${p.id} - ${p.name} - $${p.price} - stock:${p.stock}`;
    productsEl.appendChild(el);
  })
});

const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws/shop/');
ws.onmessage = (ev)=>{
  const data = JSON.parse(ev.data);
  if(data.type === 'order_update') addMessage(`Order ${data.order_id} status: ${data.status}`);
  if(data.type === 'chat') addMessage(`Chat: ${data.message}`);
  if(data.joined) addMessage(`Joined order ${data.joined}`);
};

document.getElementById('buyBtn').addEventListener('click', ()=>{
  const pid = document.getElementById('productId').value;
  const qty = document.getElementById('quantity').value || 1;
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return decodeURIComponent(match[2]);
    return null;
  }
  const csrftoken = getCookie('csrftoken');
  fetch('/api/orders/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken || ''
    },
    credentials: 'same-origin',
    body: JSON.stringify({product: pid, quantity: qty})
  }).then(r => {
    if (!r.ok) return r.json().then(j=>Promise.reject(j));
    return r.json();
  }).then(order => {
    addMessage(`Created order ${order.id}`);
    ws.send(JSON.stringify({action:'join_order', order_id: order.id}));
  }).catch(err => {
    const msg = err && err.detail ? err.detail : 'order failed';
    addMessage(msg);
  });
});

document.getElementById('chatBtn').addEventListener('click', ()=>{
  const txt = document.getElementById('chatInput').value;
  ws.send(JSON.stringify({action:'chat', message: txt}));
});
