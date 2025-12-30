from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0002_phase2_campaign_user_search'),
        ('document_states', '0028_workflowstateescalation'),
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovalWorkflowEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(db_index=True, verbose_name='Submitted at')),
                ('approved_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Approved at')),
                ('rejected_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Rejected at')),
                ('approval_time_days', models.FloatField(blank=True, null=True, verbose_name='Approval time (days)')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], db_index=True, max_length=50, verbose_name='Status')),
                ('rejection_reason', models.TextField(blank=True, default='', verbose_name='Rejection reason')),
                ('attempt_number', models.PositiveIntegerField(default=1, verbose_name='Attempt number')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created at')),
                ('approver', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='analytics_approval_actions', to=settings.AUTH_USER_MODEL, verbose_name='Approver')),
                ('document', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='analytics_approval_events', to='documents.document', verbose_name='Document')),
                ('submitter', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='analytics_approval_submissions', to=settings.AUTH_USER_MODEL, verbose_name='Submitter')),
                ('workflow_instance', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='analytics_approval_events', to='document_states.workflowinstance', verbose_name='Workflow instance')),
            ],
            options={
                'verbose_name': 'Approval workflow event',
                'verbose_name_plural': 'Approval workflow events',
                'db_table': 'analytics_approval_workflow_events',
            },
        ),
        migrations.AddIndex(
            model_name='approvalworkflowevent',
            index=models.Index(fields=['document', '-submitted_at'], name='analytics_ap_document_2f3a1e_idx'),
        ),
        migrations.AddIndex(
            model_name='approvalworkflowevent',
            index=models.Index(fields=['workflow_instance', '-submitted_at'], name='analytics_ap_workflow_00f80e_idx'),
        ),
        migrations.AddIndex(
            model_name='approvalworkflowevent',
            index=models.Index(fields=['status', '-submitted_at'], name='analytics_ap_status_1c03ff_idx'),
        ),
    ]


