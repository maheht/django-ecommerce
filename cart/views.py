
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from products.models import Product
from .models import CartItem


# Add product to cart
@login_required(login_url="login")
@require_POST
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    if product.stock <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect("product_detail", product_id=product.id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 1}
    )

    if not created:

        if cart_item.quantity >= product.stock:
            messages.error(
                request,
                "You cannot add more than the available stock."
            )
            return redirect("cart_detail")

        cart_item.quantity += 1
        cart_item.save()

    messages.success(
        request,
        f"{product.name} added to your cart."
    )

    return redirect("cart_detail")


# Display user's cart
@login_required(login_url="login")
def cart_detail(request):

    cart_items = CartItem.objects.filter(
        user=request.user,
        product__is_active=True
    ).select_related("product").prefetch_related("product__images")

    total_price = Decimal("0.00")

    for item in cart_items:

        discount = min(item.product.discount, 100)

        unit_price = (
            item.product.price *
            Decimal(100 - discount) /
            Decimal(100)
        ).quantize(Decimal("0.01"))

        item.unit_price = unit_price
        item.line_total = unit_price * item.quantity

        total_price += item.line_total

    return render(request, "cart/cart_detail.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


# Update product quantity
@login_required(login_url="login")
@require_POST
def update_cart(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    try:
        quantity = int(request.POST.get("quantity", 0))
    except (ValueError, TypeError):
        quantity = 0

    if quantity < 1:
        messages.error(request, "Invalid quantity.")

    elif quantity > cart_item.product.stock:
        messages.error(
            request,
            "Requested quantity exceeds available stock."
        )

    else:
        cart_item.quantity = quantity
        cart_item.save()

        messages.success(request, "Cart updated successfully.")

    return redirect("cart_detail")


# Remove product from cart
@login_required(login_url="login")
@require_POST
def remove_from_cart(request, item_id):

    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        user=request.user
    )

    cart_item.delete()

    messages.success(request, "Product removed from cart.")

    return redirect("cart_detail")
