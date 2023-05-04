from django.urls import path
from . import views

urlpatterns = [
    path("", views.store, name="store"),
    path("category/<slug:slug>/", views.category, name="category"),
    path("search", views.search, name="store_search"),
    # path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment_handler/", views.payment_handler, name="payment_handler"),
    path("add_to_wishlist/", views.add_to_wishlist, name="add_to_wishlist"),
    path("update_item/", views.update_item, name="update_item"),
    path("process_order/", views.process_order, name="process_order"),
    path("user/profile/", views.profile, name="profile"),
    path("user/save/", views.save_profile, name="saveprofile"),
    path("user/add_address/", views.add_address, name="add_address"),
    path("user/add_product/", views.add_product, name="add_product"),
    path("manage_store/", views.manage_store, name="manage_store"),
    path("delete_address/", views.delete_address, name="deleteaddress"),
    path("get_product_data/", views.get_product_data, name="get_product_data"),
    path("submit_review/", views.submit_review, name="submit_review"),
    path("filter/", views.filter_results, name="filter_results"),
    path("p/<slug:slug>/", views.product_detail, name="product_detail"),
    path("<int:id>/", views.personal_store, name="personal_store"),
    path("productwishlist", views.productwishlist, name="productwishlist"),
    path("product_filter", views.product_filter, name="product_filter"),
]
