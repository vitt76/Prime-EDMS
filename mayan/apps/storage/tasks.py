import logging

from django.apps import apps

from mayan.celery import app

logger = logging.getLogger(name=__name__)


@app.task(ignore_result=True)
def task_download_files_stale_delete():
    logger.debug('Executing')

    DownloadFile = apps.get_model(
        app_label='storage', model_name='DownloadFile'
    )

    queryset = DownloadFile.objects.stale()

    logger.debug('Queryset count: %d', queryset.count())

    for expired_download in queryset.all():
        expired_download.delete()

    logger.debug('Finished')


@app.task(ignore_result=True)
def task_shared_upload_stale_delete():
    logger.debug('Executing')

    SharedUploadedFile = apps.get_model(
        app_label='storage', model_name='SharedUploadedFile'
    )

    queryset = SharedUploadedFile.objects.stale()

    logger.debug('Queryset count: %d', queryset.count())

    for expired_upload in queryset.all():
        expired_upload.delete()

    logger.debug('Finished')


@app.task(ignore_result=True)
def task_chunked_upload_cleanup():
    """
    Cleanup expired chunked uploads.
    Phase B3.2 - Cleans up incomplete multipart uploads.
    """
    logger.debug('Executing chunked upload cleanup')

    try:
        from .models_chunked_upload import ChunkedUpload
        from .settings import setting_chunked_upload_expiration_hours

        expiration_hours = setting_chunked_upload_expiration_hours.value
        count = ChunkedUpload.objects.cleanup_expired(hours=expiration_hours)

        logger.info(f'Cleaned up {count} expired chunked uploads')
    except ImportError as e:
        logger.warning(f'ChunkedUpload model not available: {e}')
    except Exception as e:
        logger.error(f'Error during chunked upload cleanup: {e}')

    logger.debug('Finished chunked upload cleanup')