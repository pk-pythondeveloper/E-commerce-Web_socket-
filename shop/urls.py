from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/products/', views.ProductList.as_view(), name='product-list'),
    path('api/products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('api/orders/', views.CreateOrder.as_view(), name='create-order'),
    path('api/orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
]
