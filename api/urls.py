from django.urls import path, include  # add this
from api import views
urlpatterns = [
    path("lab_list", views.LabList.as_view(), name="api_lab_list"),
    path("inventory_list/<int:lab_pk>", views.InventoryList.as_view(), name="api_inv_list"),
    path("item_list/<int:inv_pk>", views.ItemList.as_view(), name="api_item_list"),
    path("item_detail/<int:pk>", views.ItemDetail.as_view(), name="api_item_detail"),
    path("item_change_log/<int:item_pk>", views.ItemLogList.as_view(), name="api_item_change_log"),
    path("item_order/<int:lab_pk>", views.ItemOrder.as_view(), name="api_item_order"),

                 # UI Kits Html files
]
urlpatterns += [
    path('api-auth', include('rest_framework.urls'))
]