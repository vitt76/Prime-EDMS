## Image Editor → Mayan Versioning: Архитектурный аудит и план интеграции

### 1. Что есть сейчас (side-car)
- Backend: `mayan/apps/image_editor/views.py`
  - `ImageEditorView` рендерит шаблон `image_editor/editor.html`.
  - `ImageEditorSaveView` принимает `FormData` (`image_content`, `format`, `comment`, optional `action_id`), конвертирует через `Pillow` и вызывает `document_file.document.file_new(...)` c `DocumentFileActionUseNewPages.backend_id`.
  - Сохранение происходит в Django-вью без DRF/headless, без явных ACL-check (только `permission_document_file_edit`), нет REST-версии, нет audit/trace в headless.
  - Сигналы Mayan для превью/ OCR сработают, но вызов вне headless-слоя и без явной интеграции в новую архитектуру.
- Frontend (Classic template): `image_editor/editor.html` — vanilla JS, `canvas.toBlob → fetch(saveUrl)` с CSRF; после успеха редиректит на `/documents/documents/files/{id}/preview/`.
- DAM Frontend (Vue): отдельного headless API для редактора нет; в `AssetDetailPage` предусмотрен хендлер `handleSaveAsVersion`, но он не подключён к API.

### 2. Проблемы текущего подхода
1) Нет headless/REST точки: невозможно дергать редактор из нового фронта без cookie/CSRF.  
2) Логика конвертации смешана с вью (Pillow в контроллере).  
3) Нет явной поддержки форматов/параметров (dpi/quality/watermark) в API; формат задаётся строкой.  
4) Нет декларативного комментария и атрибуции пользователя в версии на уровне headless API.  
5) Нет проверки/валидации размера/типа перед сохранением (кроме Pillow open).  
6) Нет отката/линейки версий в UI — создаётся новая `DocumentFile`, но фронт не обновляет версионную историю.  
7) Сохранение работает как side-car: URL `/documents/...` вне `/api/v4/headless/...`, нет токенной аутентификации.

### 3. Цель (non-destructive, versioned)
- Любое сохранение → новая `DocumentVersion`/`DocumentFile` (через стандартный pipeline Mayan).  
- Версионирование прозрачно: можно откатиться к v1.  
- API-first: фронт шлёт бинарь в headless endpoint с токеном.  
- Совместимость с любыми storage backends (S3/local) — использовать `file_new`/`Document.new_version` и не писать напрямую в FS.

### 4. Предлагаемый headless endpoint
- URL: `POST /api/v4/headless/documents/{id}/versions/new_from_edit/`
- Auth: Token / Session; ACL: `permission_document_file_edit` + `permission_document_view`.
- Payload (multipart/form-data):
  - `file` — бинарь (обязателен).
  - `format` — `jpeg|png|webp|tiff` (опц, default `jpeg`).
  - `comment` — строка (опц, default `"Edited in DAM Image Editor"`).
  - `action_id` — опц, default `DocumentFileActionUseNewPages.backend_id`.
- Response: `{ "version_id": int, "file_id": int, "document_id": int, "preview_url": "...", "thumbnail_url": "...", "comment": "..." }`
- Side effects:
  - Триггерить стандартные signals (`document_file_created`, `document_version_created`) чтобы OCR/preview работали.
  - Возвращать абсолютные URL (использовать serializer с `request.build_absolute_uri`).

### 5. Псевдокод `HeadlessEditView`
```python
class HeadlessEditView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        doc = get_object_or_404(Document.valid, pk=document_id)
        AccessControlList.objects.check_access(
            permission=permission_document_file_edit,
            user=request.user,
            obj=doc
        )

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'file_required'}, status=400)

        target_format = request.data.get('format', 'jpeg').lower()
        comment = request.data.get('comment') or 'Edited in DAM Image Editor'
        action_id = request.data.get('action_id') or DocumentFileActionUseNewPages.backend_id

        # Нормализуем/конвертируем формат
        converted_file, new_name, content_type = convert_image(
            file_obj,
            target_format=target_format,
            original_name=file_obj.name
        )

        new_file = doc.file_new(
            file_object=converted_file,
            filename=new_name,
            action=action_id,
            comment=comment,
            _user=request.user
        )

        serializer = OptimizedDocumentListSerializer(
            new_file.document,
            context={'request': request}
        )
        return Response({
            'success': True,
            'document_id': doc.pk,
            'file_id': new_file.pk,
            'version_id': getattr(new_file, 'document_version_id', None),
            'comment': comment,
            'document': serializer.data,
        })
```
`convert_image` выносим в сервис/utility (использовать Pillow или уже имеющийся `PresetImageConverter` в `converter_pipeline_extension`).

### 6. План миграции (frontend ↔ headless)
1) Backend
   - Добавить `HeadlessEditView` в `mayan/apps/headless_api/views/` + URL `headless/documents/<int:document_id>/versions/new_from_edit/`.
   - Использовать существующий конвертер (`PresetImageConverter`) вместо ручного Pillow вью.
   - Serializer: `OptimizedDocumentListSerializer` для возврата абсолютных preview/thumbnail.
   - Переместить `ImageEditorSaveView` логику в сервис/utility, оставить старую страницу для совместимости, но пометить deprecated.
2) Frontend (Vue DAM)
   - В модуле редактора: при сохранении отправлять `FormData(file, format, comment)` на новый headless endpoint с токеном.
   - После успеха: обновить стор версий/деталку (`handleSaveAsVersion` → refetch asset).
   - Не менять UI: только заменить URL и обработку ответа.
3) Отключение side-car
   - Перенаправить старый шаблонный `saveUrl` на headless endpoint (или показать warning), чтобы не плодить две системы.

### 7. Формат/конверсия и watermark
- Поддержка `jpeg|png|webp|tiff`; дополнительно можно проксировать в `PresetImageConverter` параметры `quality`, `dpi`, `width/height`, `watermark`.
- Для совместимости: если `format` не передан — сохраняем оригинальный формат, иначе конвертируем.

### 8. Проверки и ограничения
- Валидация размера (e.g. ≤ 50MB) до конвертации.
- MIME whitelist: только image/* вход.
- Лимитируем длительность обработки (Pillow safety), обрабатываем OOM.
- Аудит: писать в лог кто создал новую версию (`_event_actor` через `_user`).

### 9. Что даёт новая схема
- Нестр destructive: каждая правка = новая версия, можно откатить.
- Сигналы Mayan обеспечивают генерацию превью/тумбов и OCR без доп. кода.
- API-first: работает с токеном, без CSRF и шаблонов.
- Хранение через стандартный storage backend (S3/local) — без прямой записи в FS.

