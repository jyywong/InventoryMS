from django.urls import path
from inventory import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.Home.as_view(), name="homepage"),
    path('test_view', views.Home.as_view(), name="homepage"),

    # Lab urls
    path('create_lab', views.Lab_Create.as_view(), name="create_lab"),
    path('my_labs', views.LabList.as_view(), name="lab_list"),
    path('lab_detail/<int:pk>', views.LabView.as_view(), name="lab_view" ),
    path('lab_add/<int:pk>', views.LabAdd.as_view(), name="lab_add_member" ),
    path('lab_detail/orders/<int:pk>', views.LabOrderList.as_view(), name="lab_orders" ),
    path('lab_detail/orders/order_detail/<int:pk>', views.OrderDetail, name="order_detail" ),
    path('remove_member/<int:lab_pk>/<int:user_pk>', views.RemoveMember, name="remove_member" ),
    path('invite_member/<int:pk>', views.InviteMember.as_view(), name="invite_member" ),

    # Inventory urls
    path('inventory_create/<int:pk>', views.Inventory_Create.as_view(), name="create_inventory"),
    path('inventory_update', views.Inventory_Update.as_view(), name="update_inventory"),
    path('inventory/<int:pk>', views.InvList.as_view(), name="inv_list" ),
    path('inventory_detail/<int:pk>', views.InvView.as_view(), name="inventory_view" ),
    path('inventory_orders/<int:pk>', views.InventoryOrderList.as_view(), name="inv_order_list" ),
    path('inventory_delete/<int:pk>', views.InventoryDelete.as_view(), name="inventory_delete" ),

    # Item urls
    path('item_create/<int:pk>', views.Item_Create.as_view(), name="item_create"),
    path('item_delete/<int:pk>', views.Item_Delete.as_view(), name="item_delete"),
    path('items/<int:pk>', views.ItemList.as_view(), name="item_list" ),
    path('item_detail/<int:pk>', views.ItemView.as_view(), name="item_view" ),
    path('item_detail/add/<int:pk>', views.ItemAdd.as_view(), name="item_add" ),
    path('item_detail/remove/<int:pk>', views.ItemRemove.as_view(), name="item_remove" ),
    path('item_detail/order/<int:pk>', views.ItemOrderCreate.as_view(), name="order_create" ),

    # Other urls
    path('orders', views.OrderList.as_view(), name="order_lists" ),
    path('invites', views.InviteList.as_view(), name="invite_list" ),
    path('invite_detail/<int:pk>', views.InviteDetail, name="invite_detail" ),

    
]
