from django.conf.urls import url

from .views import (
    PublicFAQListView,
    PublicLeadCreateView,
    PublicPageDetailView,
    PublicPlanListView,
    PublicPostDetailView,
    PublicPostListView,
    PublicRegisterView,
    PublicVerifyEmailView
)

app_name = 'marketing_cms'

api_urls = [
    url(
        regex=r'^public/pages/(?P<slug>[-\w]+)/$',
        view=PublicPageDetailView.as_view(),
        name='public-pages-detail'
    ),
    url(
        regex=r'^public/posts/$',
        view=PublicPostListView.as_view(),
        name='public-posts-list'
    ),
    url(
        regex=r'^public/posts/(?P<slug>[-\w]+)/$',
        view=PublicPostDetailView.as_view(),
        name='public-posts-detail'
    ),
    url(
        regex=r'^public/plans/$',
        view=PublicPlanListView.as_view(),
        name='public-plans-list'
    ),
    url(
        regex=r'^public/faq/$',
        view=PublicFAQListView.as_view(),
        name='public-faq-list'
    ),
    url(
        regex=r'^public/leads/$',
        view=PublicLeadCreateView.as_view(),
        name='public-leads-create'
    ),
    url(
        regex=r'^public/auth/register/$',
        view=PublicRegisterView.as_view(),
        name='public-auth-register'
    ),
    url(
        regex=r'^public/auth/verify-email/$',
        view=PublicVerifyEmailView.as_view(),
        name='public-auth-verify-email'
    )
]

urlpatterns = []
