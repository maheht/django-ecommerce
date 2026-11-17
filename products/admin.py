
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage,Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_preview',)
    fields = ('image_url', 'image_preview', 'is_main')

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        if obj and obj.image_url:
            return format_html(
                '<img src="{}" width="100" height="100" '
                'style="object-fit: contain;" />',
                obj.image_url
            )
        return "No image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'name',
        'category',
        'price',
        'discount',
        'stock',
        'is_active',
    )

    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    inlines = [ProductImageInline]

    @admin.display(description='Product Image')
    def image_thumbnail(self, obj):
        main_image = obj.images.filter(is_main=True).first()

        if not main_image:
            main_image = obj.images.first()

        if main_image and main_image.image_url:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit: contain; border-radius: 6px;" />',
                main_image.image_url
            )

        return 'No Image'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_url', 'is_main')
    list_filter = ('is_main',)
admin.site.register(Review)