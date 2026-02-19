# Sprint 5.1: WatermarkedRendition for secure download

from django.db import migrations, models
import django.db.models.deletion
import mayan.apps.storage.classes


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0087_add_documentfile_width_height'),
        ('distribution', '0016_publication_organization'),
        ('organizations', '0008_organizationwatermarksettings_apply_on_download'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatermarkedRendition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(
                    blank=True,
                    help_text='Watermarked file',
                    null=True,
                    storage=mayan.apps.storage.classes.DefinedStorageLazy(name='distribution__renditions'),
                    upload_to='renditions/watermarked/'
                )),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')],
                    default='pending',
                    help_text='Generation status',
                    max_length=16
                )),
                ('error_message', models.TextField(blank=True, help_text='Error message if generation failed')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('document_file', models.ForeignKey(
                    help_text='Source document file',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='watermarked_renditions',
                    to='documents.DocumentFile'
                )),
                ('organization', models.ForeignKey(
                    help_text='Organization (tenant) for watermark settings',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='watermarked_renditions',
                    to='organizations.Organization'
                )),
            ],
            options={
                'ordering': ['-modified'],
                'verbose_name': 'Watermarked rendition',
                'verbose_name_plural': 'Watermarked renditions',
                'unique_together': {('document_file', 'organization')},
            },
        ),
    ]
