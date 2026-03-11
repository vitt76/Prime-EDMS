from django.db import migrations, models
import django.db.models.deletion


def populate_distributioncampaign_organization(apps, schema_editor):
    DistributionCampaign = apps.get_model('distribution', 'DistributionCampaign')
    CampaignPublication = apps.get_model('distribution', 'CampaignPublication')
    Organization = apps.get_model('organizations', 'Organization')

    campaign_publications = CampaignPublication.objects.select_related(
        'publication'
    )

    for campaign in DistributionCampaign.objects.all():
        organization = None
        metadata = campaign.metadata or {}
        organization_id = metadata.get('organization_id')

        if organization_id:
            organization = Organization.objects.filter(
                pk=organization_id
            ).first()

        if organization is None:
            campaign_publication = campaign_publications.filter(
                campaign_id=campaign.pk,
                publication__organization__isnull=False
            ).first()
            if campaign_publication:
                organization = campaign_publication.publication.organization

        if organization is not None:
            DistributionCampaign.objects.filter(pk=campaign.pk).update(
                organization=organization
            )


class Migration(migrations.Migration):

    dependencies = [
        ('distribution', '0017_watermarkedrendition'),
        ('organizations', '0008_organizationwatermarksettings_apply_on_download'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributioncampaign',
            name='organization',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='Organization this record belongs to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='distribution_distributioncampaign_set',
                to='organizations.organization',
                verbose_name='Organization',
            ),
        ),
        migrations.RunPython(
            populate_distributioncampaign_organization,
            migrations.RunPython.noop
        ),
        migrations.AddIndex(
            model_name='distributioncampaign',
            index=models.Index(
                fields=['organization'],
                name='distribution_dcamp_org_idx',
            ),
        ),
    ]
