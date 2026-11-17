
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from .models import Product, Review, Category
from .serializers import ReviewSerializer
from orders.models import OrderItem


# صفحه اصلی فروشگاه و فیلتر محصولات بر اساس دسته‌بندی
def home(request):

    # دریافت نام دسته‌بندی انتخاب‌شده از آدرس
    category_name = request.GET.get("category")

    # دریافت دسته‌بندی‌های فعال
    categories = Category.objects.filter(
        is_active=True
    ).order_by("name")

    # دریافت تمام محصولات فعال
    products = Product.objects.filter(
        is_active=True
    ).select_related(
        "category"
    ).prefetch_related(
        "images"
    ).order_by("-created_at")

    # در ابتدا هیچ دسته‌ای انتخاب نشده است
    selected_category = None

    # اگر کاربر دسته‌بندی انتخاب کرده باشد
    if category_name:

        selected_category = get_object_or_404(
            Category,
            name=category_name,
            is_active=True
        )

        # فقط محصولات همان دسته‌بندی نمایش داده می‌شوند
        products = products.filter(
            category=selected_category
        )

    return render(request, "products/home.html", {
        "products": products,
        "categories": categories,
        "selected_category": selected_category,
    })


# صفحه جزئیات محصول
def product_detail(request, product_id):

    product = get_object_or_404(
        Product.objects.filter(
            is_active=True
        ).prefetch_related("images", "category"),
        id=product_id
    )

    main_image = (
        product.images.filter(is_main=True).first()
        or product.images.first()
    )

    # دریافت نظرات تأییدشده محصول
    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    ).select_related("user").order_by("-created_at")

    return render(request, "products/product_detail.html", {
        "product": product,
        "main_image": main_image,
        "reviews": reviews,
    })


# ثبت نظر از طریق فرم HTML سایت
@login_required
@require_POST
def submit_product_review(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    # دریافت اطلاعات فرم
    comment = request.POST.get("comment", "").strip()
    rating = request.POST.get("rating")

    # بررسی متن نظر
    if not comment:
        messages.error(request, "Please write your comment.")
        return redirect("product_detail", product_id=product.id)

    # بررسی امتیاز
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        messages.error(request, "Invalid rating.")
        return redirect("product_detail", product_id=product.id)

    if rating < 1 or rating > 5:
        messages.error(request, "Rating must be between 1 and 5.")
        return redirect("product_detail", product_id=product.id)

    # بررسی خرید محصول توسط کاربر
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status__in=["paid", "shipped", "delivered"],
        product=product
    ).exists()

    if not has_purchased:
        messages.error(
            request,
            "You must purchase this product before reviewing it."
        )
        return redirect("product_detail", product_id=product.id)

    # جلوگیری از ثبت نظر تکراری
    if Review.objects.filter(
        user=request.user,
        product=product
    ).exists():
        messages.error(
            request,
            "You have already reviewed this product."
        )
        return redirect("product_detail", product_id=product.id)

    # ذخیره نظر در دیتابیس
    Review.objects.create(
        user=request.user,
        product=product,
        comment=comment,
        rating=rating,
        is_approved=False
    )

    messages.success(
        request,
        "Your review was submitted and is waiting for approval."
    )

    return redirect("product_detail", product_id=product.id)


# API نمایش و ثبت نظرات برای اپلیکیشن اندروید
class ProductReviewListCreateView(generics.ListCreateAPIView):

    serializer_class = ReviewSerializer

    # تعیین سطح دسترسی
    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    # دریافت نظرات تأییدشده یک محصول
    def get_queryset(self):
        return Review.objects.filter(
            product_id=self.kwargs["product_id"],
            is_approved=True
        ).select_related(
            "user", "product"
        ).order_by("-created_at")

    # بررسی شرایط ثبت نظر
    def perform_create(self, serializer):

        # پیدا کردن محصول
        product = get_object_or_404(
            Product,
            id=self.kwargs["product_id"],
            is_active=True
        )

        # بررسی خرید محصول توسط کاربر
        has_purchased = OrderItem.objects.filter(
            order__user=self.request.user,
            order__status__in=["paid", "shipped", "delivered"],
            product=product
        ).exists()

        if not has_purchased:
            raise ValidationError(
                "You must purchase this product before reviewing it."
            )

        # جلوگیری از ثبت نظر تکراری
        if Review.objects.filter(
            user=self.request.user,
            product=product
        ).exists():
            raise ValidationError(
                "You have already reviewed this product."
            )

        # ذخیره نظر با کاربر و محصول مشخص
        serializer.save(
            user=self.request.user,
            product=product
        )
