import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.development')
django.setup()

from mayan.apps.organizations.models import Organization
from mayan.apps.saved_searches.models import SavedSearch
from mayan.apps.events.models import Action
from mayan.apps.documents.models import Document
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

User = get_user_model()
user = User.objects.filter(is_superuser=True).first()
org = Organization.objects.first()

if user and org:
    # 1. Create Saved Searches
    if not SavedSearch.objects.filter(user=user, name="Маркетинг Q3").exists():
        SavedSearch.objects.create(
            user=user,
            organization=org,
            name="Маркетинг Q3",
            query="promo",
            filters={"orientation": "portrait", "tags": "Promo"}
        )
    if not SavedSearch.objects.filter(user=user, name="Без тегов").exists():
        SavedSearch.objects.create(
            user=user,
            organization=org,
            name="Без тегов",
            query="",
            filters={"status": "untagged"}
        )
    print("Saved searches seeded.")

    # 2. Activity Feed
    doc = Document.objects.filter(organization=org).first()
    if doc:
        doc_ct = ContentType.objects.get_for_model(Document)
        user_ct = ContentType.objects.get_for_model(User)
        
        # document viewed
        Action.objects.create(
            actor_content_type=user_ct,
            actor_object_id=user.pk,
            verb='documents.document_view',
            target_content_type=doc_ct,
            target_object_id=doc.pk,
            timestamp=timezone.now() - datetime.timedelta(minutes=5)
        )
        # document updated
        Action.objects.create(
            actor_content_type=user_ct,
            actor_object_id=user.pk,
            verb='documents.document_properties_edit',
            target_content_type=doc_ct,
            target_object_id=doc.pk,
            timestamp=timezone.now() - datetime.timedelta(minutes=15)
        )
        print("Activity seeded.")
    else:
        print("No document found to create activity for.")
else:
    print("User or org not found.")
