
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from cart.models import CartItem
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required(login_url="login")
def checkout(request):

    cart_items = CartItem.objects.filter(
        user=request.user,
        product__is_active=True
    ).select_related("product")

    if not cart_items.exists():
        messages.error(request, "Your shopping cart is empty.")
        return redirect("cart_detail")

    total_price = Decimal("0.00")

    for item in cart_items:
        discount = min(item.product.discount, 100)

        unit_price = (
            item.product.price
            * Decimal(100 - discount)
            / Decimal(100)
        ).quantize(Decimal("0.01"))

        item.unit_price = unit_price
        item.line_total = unit_price * item.quantity

        total_price += item.line_total

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                order = form.save(commit=False)

                order.user = request.user
                order.total_price = total_price

                order.save()

                for item in cart_items:

                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.unit_price
                    )

            messages.success(
                request,
                "Your order has been created successfully."
            )

            return redirect("cart_detail")

    else:
        form = CheckoutForm()

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "total_price": total_price,
        }
    )
