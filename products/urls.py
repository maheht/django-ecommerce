
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "products/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),

    # API نمایش و ثبت نظرات برای اپلیکیشن اندروید
    path(
        "api/products/<int:product_id>/reviews/",
        views.ProductReviewListCreateView.as_view(),
        name="product-reviews"
    ),

    # ثبت نظر از طریق سایت
    path(
        "products/<int:product_id>/review/",
        views.submit_product_review,
        name="submit_product_review"
    ),
]
