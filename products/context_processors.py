
from .models import Category


def product_categories(request):
    categories = Category.objects.filter(
        is_active=True
    ).order_by("name")

    return {
        "categories": categories
    }
