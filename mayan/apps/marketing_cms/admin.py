from django.contrib import admin

from .models import FAQ, Lead, Page, Plan, Post, EmailVerificationToken


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'status', 'published_at', 'updated_at')
    search_fields = ('slug',)
    list_filter = ('status',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('slug', 'status', 'category', 'published_at', 'updated_at')
    search_fields = ('slug', 'category')
    list_filter = ('status', 'category')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price_monthly', 'recommended', 'order')
    list_filter = ('type', 'recommended')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('section', 'order', 'is_active')
    list_filter = ('section', 'is_active')


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('email', 'company', 'source', 'created_at')
    search_fields = ('email', 'company')
    list_filter = ('source',)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expires_at', 'used_at')
    search_fields = ('user__email', 'token')
