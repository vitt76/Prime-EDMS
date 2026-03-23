from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView

from .models import FAQ, Lead, Page, Plan, Post, EmailVerificationToken
from .serializers import (
    FAQSerializer,
    LeadSerializer,
    LoginSerializer,
    NewsletterSubscriptionSerializer,
    PageSerializer,
    PlanSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PublicAnalyticsEventSerializer,
    RegisterSerializer
)


def get_lang(request):
    return request.query_params.get('lang', 'ru')


class PublicPageDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PageSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Page.objects.filter(status='published')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = get_lang(self.request)
        return context


class PublicPostListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        lang = get_lang(request)
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        search = request.query_params.get('search') or request.query_params.get('q')
        category = request.query_params.get('category')

        queryset = Post.objects.filter(status='published')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search) | Q(excerpt__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__iexact=category)

        total = queryset.count()
        start = max(page - 1, 0) * limit
        end = start + limit
        results = queryset.order_by('-published_at')[start:end]

        serializer = PostListSerializer(results, many=True, context={'lang': lang})
        base_url = request.build_absolute_uri(request.path)
        next_url = None
        prev_url = None
        if end < total:
            next_url = f"{base_url}?{urlencode({'page': page + 1, 'limit': limit, 'lang': lang})}"
        if page > 1:
            prev_url = f"{base_url}?{urlencode({'page': page - 1, 'limit': limit, 'lang': lang})}"

        return Response(
            {
                'count': total,
                'next': next_url,
                'previous': prev_url,
                'results': serializer.data
            }
        )


class PublicPostDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Post.objects.filter(status='published')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = get_lang(self.request)
        return context


class PublicPlanListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PlanSerializer

    def get_queryset(self):
        queryset = Plan.objects.all()
        plan_type = self.request.query_params.get('type')
        if plan_type:
            queryset = queryset.filter(type=plan_type)
        return queryset.order_by('order')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = get_lang(self.request)
        return context


class PublicFAQListView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FAQSerializer

    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)
        section = self.request.query_params.get('section')
        if section:
            queryset = queryset.filter(section=section)
        return queryset.order_by('order')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['lang'] = get_lang(self.request)
        return context


class PublicLeadCreateView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LeadSerializer
    queryset = Lead.objects.all()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                'id': response.data.get('id'),
                'status': 'new',
                'created_at': response.data.get('created_at'),
                'message': 'Спасибо! Мы получили ваше сообщение и свяжемся в течение 24 часов.'
            },
            status=status.HTTP_201_CREATED
        )


class PublicNewsletterSubscribeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = NewsletterSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        lead = Lead.objects.create(
            name=email,
            email=email,
            source='newsletter',
            metadata={
                'lang': get_lang(request),
                'path': request.path,
            }
        )

        return Response(
            {
                'id': lead.pk,
                'status': 'subscribed',
                'email': email,
                'message': 'Спасибо! Вы подписаны на обновления.'
            },
            status=status.HTTP_201_CREATED
        )


class PublicRegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        return Response(
            {
                'id': str(user.id),
                'email': user.email,
                'organization': {
                    'id': None,
                    'name': serializer.validated_data.get('organization_name'),
                    'slug': None,
                    'created_at': None
                },
                'verification_required': True,
                'verification_email_sent': False,
                'next_step': 'verify_email',
                'message': 'На email отправлено письмо с ссылкой активации. Перейдите по ссылке для подтверждения адреса.',
                'token': token.token
            },
            status=status.HTTP_201_CREATED
        )


class PublicLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request=request, username=email, password=password)
        if user is None:
            return Response(
                {'message': 'Неверный email или пароль.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {
                    'message': 'Аккаунт не активирован. Подтвердите email перед входом.',
                    'error': 'account_inactive'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        token, _ = Token.objects.get_or_create(user=user)
        try:
            update_last_login(sender=None, user=user)
        except Exception:
            pass

        redirect_url = (
            getattr(settings, 'FRONTEND_URL', None) or
            getattr(settings, 'SPA_URL', '') or
            'http://localhost:5173'
        )

        return Response(
            {
                'token': token.key,
                'user': {
                    'id': str(user.pk),
                    'email': user.email,
                    'username': user.get_username(),
                },
                'redirect_url': redirect_url,
            },
            status=status.HTTP_200_OK
        )


class PublicVerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        token_value = request.data.get('token')
        if not token_value:
            return Response(
                {'error': 'token_missing', 'message': 'Token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = EmailVerificationToken.objects.select_related('user').get(token=token_value)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'error': 'token_invalid', 'message': 'Token is invalid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not token.is_valid():
            return Response(
                {
                    'error': 'token_expired',
                    'message': 'Ссылка активации истекла. Отправьте письмо снова.',
                    'retry_url': '/auth/register/send-verification'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        token.used_at = timezone.now()
        token.save(update_fields=['used_at'])
        user = token.user
        user.is_active = True
        user.save(update_fields=['is_active'])
        frontend_base = (
            getattr(settings, 'FRONTEND_URL', None) or
            getattr(settings, 'SPA_URL', '') or
            ''
        ).strip()
        redirect_base = frontend_base.rstrip('/') if frontend_base else 'http://localhost:5173'
        redirect_url = f'{redirect_base}/login?verified=true'
        return Response(
            {
                'success': True,
                'message': 'Email успешно подтвержден. Вы можете войти в систему.',
                'redirect_url': redirect_url,
            },
            status=status.HTTP_200_OK
        )


class PublicAnalyticsEventView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = PublicAnalyticsEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data.copy()
        payload.setdefault('timestamp', timezone.now())
        payload['timestamp'] = payload['timestamp'].isoformat()
        payload['path'] = request.path
        payload['ip_address'] = (request.META.get('REMOTE_ADDR') or '')[:45]
        payload['user_agent'] = (request.META.get('HTTP_USER_AGENT') or '')[:500]

        try:
            from mayan.apps.analytics.event_stream import publish_event
            from mayan.apps.analytics.operational import increment_counter, record_marker

            publish_event(
                payload={
                    'kind': 'public_event',
                    **payload,
                }
            )
            increment_counter('public_events_total')
            record_marker(
                'public_ingest',
                payload={
                    'event': payload.get('event', ''),
                    'path': payload.get('path', ''),
                }
            )
        except Exception:
            pass

        return Response({'status': 'accepted'}, status=status.HTTP_202_ACCEPTED)
