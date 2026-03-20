import re

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .models import FAQ, Lead, Page, Plan, Post, EmailVerificationToken


def localize_value(value, lang: str, fallback: str = 'ru'):
    if isinstance(value, dict):
        if lang in value:
            return value.get(lang)
        if fallback in value:
            return value.get(fallback)
        if value:
            return next(iter(value.values()))
        return ''
    return value


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            'id',
            'slug',
            'title',
            'meta_title',
            'meta_description',
            'og_image',
            'canonical_url',
            'status',
            'published_at',
            'updated_at',
            'sections'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = self.context.get('lang', 'ru')
        data['title'] = localize_value(data['title'], lang)
        data['meta_title'] = localize_value(data['meta_title'], lang)
        data['meta_description'] = localize_value(data['meta_description'], lang)
        data['lang'] = lang
        return data


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id',
            'slug',
            'title',
            'excerpt',
            'featured_image',
            'category',
            'author_name',
            'author_avatar',
            'published_at',
            'updated_at',
            'reading_time_minutes',
            'tags'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = self.context.get('lang', 'ru')
        data['title'] = localize_value(data['title'], lang)
        data['excerpt'] = localize_value(data['excerpt'], lang)
        return data


class PostDetailSerializer(serializers.ModelSerializer):
    related_posts = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id',
            'slug',
            'title',
            'content',
            'content_html',
            'featured_image',
            'author_name',
            'author_avatar',
            'category',
            'tags',
            'published_at',
            'updated_at',
            'reading_time_minutes',
            'seo_title',
            'seo_description',
            'og_image',
            'related_posts'
        )

    def get_related_posts(self, obj):
        queryset = Post.objects.filter(
            status='published'
        ).exclude(id=obj.id).order_by('-published_at')[:3]
        lang = self.context.get('lang', 'ru')
        return [
            {
                'slug': post.slug,
                'title': localize_value(post.title, lang),
                'featured_image': post.featured_image
            }
            for post in queryset
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = self.context.get('lang', 'ru')
        data['title'] = localize_value(data['title'], lang)
        data['seo_title'] = localize_value(data['seo_title'], lang)
        data['seo_description'] = localize_value(data['seo_description'], lang)
        return data


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            'id',
            'name',
            'description',
            'price_monthly',
            'price_yearly',
            'currency',
            'billing_period',
            'storage_gb',
            'max_users',
            'max_api_calls_monthly',
            'features',
            'recommended',
            'type',
            'cta_text',
            'cta_url'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = self.context.get('lang', 'ru')
        data['description'] = localize_value(data['description'], lang)
        return data


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ('id', 'section', 'question', 'answer', 'order')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = self.context.get('lang', 'ru')
        data['question'] = localize_value(data['question'], lang)
        data['answer'] = localize_value(data['answer'], lang)
        return data


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            'id',
            'name',
            'email',
            'company',
            'message',
            'phone',
            'subject',
            'source',
            'metadata',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    organization_name = serializers.CharField(min_length=2)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    company_size = serializers.CharField(required=False, allow_blank=True)
    lang = serializers.CharField(required=False, default='ru')
    agree_terms = serializers.BooleanField()

    def validate_password(self, value):
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError(_('Password must include a number.'))
        if not re.search(r'[!@#$%^&*]', value):
            raise serializers.ValidationError(_('Password must include a special character.'))
        return value

    def validate_agree_terms(self, value):
        if value is not True:
            raise serializers.ValidationError(_('You must agree to the terms.'))
        return value

    def validate_email(self, value):
        user_model = get_user_model()
        if user_model.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Email already registered.'))
        return value

    def create(self, validated_data):
        user_model = get_user_model()
        password = validated_data['password']
        email = validated_data['email']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        user = user_model.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False
        )
        token = EmailVerificationToken.create_for_user(user=user)
        return user, token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember = serializers.BooleanField(required=False, default=False)


class PublicAnalyticsEventSerializer(serializers.Serializer):
    event = serializers.CharField(max_length=100)
    category = serializers.CharField(required=False, allow_blank=True, max_length=100)
    label = serializers.CharField(required=False, allow_blank=True, max_length=255)
    page = serializers.CharField(required=False, allow_blank=True, max_length=255)
    url = serializers.URLField(required=False, allow_blank=True)
    referrer = serializers.CharField(required=False, allow_blank=True, max_length=500)
    timestamp = serializers.DateTimeField(required=False)
    metadata = serializers.JSONField(required=False)
