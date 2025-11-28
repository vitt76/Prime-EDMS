# Функции редактирования и конвертации изображений

## Обзор

В системе Prime-EDMS реализованы мощные возможности для обработки, редактирования и конвертации изображений. Функциональность разделена на несколько модулей:

- **Converter** - базовые трансформации изображений
- **Image Editor** - веб-интерфейс для ручного редактирования
- **DAM (Digital Asset Management)** - AI-анализ и автоматизированная обработка

## 1. Модуль Converter - Базовые трансформации

### Архитектура
Модуль использует библиотеку PIL (Pillow) для обработки изображений и реализует паттерн трансформаций с поддержкой слоев.

### Классы трансформаций

#### BaseTransformation
Базовый класс для всех трансформаций изображений.

```python
class BaseTransformation(metaclass=BaseTransformationType):
    arguments = ()  # Аргументы трансформации
    name = 'base_transformation'  # Уникальное имя
    label = 'Base Transformation'  # Человекочитаемая метка
```

#### Методы управления трансформациями
- `combine(transformations)` - комбинирует хеши нескольких трансформаций
- `list_as_query_string()` - сериализует трансформации в URL параметры
- `register(layer, transformation)` - регистрирует трансформацию в слое

### Реализованные трансформации

#### 1. TransformationCrop
Обрезка изображения с указанием границ.

```python
class TransformationCrop(BaseTransformation):
    arguments = ('left', 'top', 'right', 'bottom')
    label = _('Crop')
    name = 'crop'
```

**Параметры:**
- `left` - пикселей слева
- `top` - пикселей сверху
- `right` - пикселей справа
- `bottom` - пикселей снизу

#### 2. TransformationDrawRectangle
Рисование прямоугольника на изображении.

```python
class TransformationDrawRectangle(TransformationDrawRectangleMixin, BaseTransformation):
    arguments = ('left', 'top', 'right', 'bottom', 'fillcolor', 'fill_transparency',
                 'outlinecolor', 'outlinewidth')
    label = _('Draw rectangle')
    name = 'draw_rectangle'
```

**Параметры:**
- `left`, `top`, `right`, `bottom` - координаты
- `fillcolor` - цвет заливки
- `fill_transparency` - прозрачность заливки
- `outlinecolor` - цвет контура
- `outlinewidth` - толщина контура

#### 3. TransformationDrawRectanglePercent
Рисование прямоугольника с координатами в процентах.

```python
class TransformationDrawRectanglePercent(TransformationDrawRectangleMixin, BaseTransformation):
    arguments = ('left', 'top', 'right', 'bottom', 'fillcolor', 'fill_transparency',
                 'outlinecolor', 'outlinewidth')
    label = _('Draw rectangle (percents coordinates)')
    name = 'draw_rectangle_percent'
```

#### 4. TransformationFlip
Отражение изображения по вертикали.

```python
class TransformationFlip(BaseTransformation):
    arguments = ()
    label = _('Flip')
    name = 'flip'
```

#### 5. TransformationMirror
Отражение изображения по горизонтали.

```python
class TransformationMirror(BaseTransformation):
    arguments = ()
    label = _('Mirror')
    name = 'mirror'
```

#### 6. TransformationResize
Изменение размера изображения.

```python
class TransformationResize(BaseTransformation):
    arguments = ('width', 'height')
    label = _('Resize')
    name = 'resize'
```

**Параметры:**
- `width` - новая ширина в пикселях
- `height` - новая высота в пикселях (опционально)

#### 7. TransformationRotate
Поворот изображения.

```python
class TransformationRotate(BaseTransformation):
    arguments = ('degrees', 'fillcolor')
    label = _('Rotate')
    name = 'rotate'
```

**Параметры:**
- `degrees` - угол поворота против часовой стрелки
- `fillcolor` - цвет для областей вне повернутого изображения

#### 8. TransformationRotate90, TransformationRotate180, TransformationRotate270
Предустановленные повороты на фиксированные углы.

#### 9. TransformationZoom
Масштабирование изображения в процентах.

```python
class TransformationZoom(BaseTransformation):
    arguments = ('percent',)
    label = _('Zoom')
    name = 'zoom'
```

#### 10. TransformationGaussianBlur
Гауссово размытие.

```python
class TransformationGaussianBlur(BaseTransformation):
    arguments = ('radius',)
    label = _('Gaussian blur')
    name = 'gaussianblur'
```

#### 11. TransformationLineArt
Преобразование в линейную графику.

```python
class TransformationLineArt(BaseTransformation):
    label = _('Line art')
    name = 'lineart'
```

#### 12. TransformationUnsharpMask
Повышение резкости с помощью Unsharp Mask.

```python
class TransformationUnsharpMask(BaseTransformation):
    arguments = ('radius', 'percent', 'threshold')
    label = _('Unsharp masking')
    name = 'unsharpmask'
```

#### 13. TransformationAssetPaste
Вставка другого изображения (абсолютные координаты).

```python
class TransformationAssetPaste(ImagePasteCoordinatesAbsoluteTransformationMixin,
                              AssetTransformationMixin, BaseTransformation):
    label = _('Paste an asset (absolute coordinates)')
    name = 'paste_asset'
```

#### 14. TransformationAssetPastePercent
Вставка другого изображения (процентные координаты).

```python
class TransformationAssetPastePercent(ImagePasteCoordinatesPercentTransformationMixin,
                                     AssetTransformationMixin, BaseTransformation):
    label = _('Paste an asset (percents coordinates)')
    name = 'paste_asset_percent'
```

#### 15. TransformationAssetWatermark
Вставка изображения как водяного знака.

```python
class TransformationAssetWatermark(ImageWatermarkPercentTransformationMixin,
                                  AssetTransformationMixin, BaseTransformation):
    label = _('Paste an asset as watermark')
    name = 'paste_asset_watermark'
```

### Слои трансформаций

Трансформации организованы в слои:
- `layer_decorations` - декоративные трансформации (вставка, рисование)
- `layer_saved_transformations` - сохраняемые трансформации (обрезка, поворот, изменение размера)

### Асинхронные задачи

#### task_content_object_image_generate
Генерирует изображение с примененными трансформациями.

```python
@app.task(bind=True, max_retries=setting_image_generation_max_retries.value,
          retry_backoff=True)
def task_content_object_image_generate(
    self, content_type_id, object_id, maximum_layer_order=None,
    transformation_dictionary_list=None, user_id=None
):
```

**Параметры:**
- `content_type_id` - ID типа контента
- `object_id` - ID объекта
- `maximum_layer_order` - максимальный порядок слоя
- `transformation_dictionary_list` - список трансформаций
- `user_id` - ID пользователя

## 2. Модуль Image Editor - Веб-интерфейс редактирования

### Модели

#### ImageEditSession
Представляет сессию редактирования изображения.

```python
class ImageEditSession(models.Model):
    STATUS_CHOICES = (
        ('editing', _('Редактируется')),
        ('saved', _('Сохранено')),
        ('cancelled', _('Отменено')),
    )

    document_file = models.ForeignKey('documents.DocumentFile', ...)
    user = models.ForeignKey('auth.User', ...)
    original_checksum = models.CharField(max_length=64)
    edited_checksum = models.CharField(max_length=64)
    status = models.CharField(choices=STATUS_CHOICES, default='editing')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
```

#### ImageEditOperation
Отдельная операция редактирования в рамках сессии.

```python
class ImageEditOperation(models.Model):
    OPERATION_TYPE_CHOICES = (
        ('crop', _('Обрезка')),
        ('rotate', _('Поворот')),
        ('flip', _('Отражение')),
        ('brightness', _('Яркость')),
        ('contrast', _('Контраст')),
        ('draw', _('Рисование')),
        ('text', _('Текст')),
        ('filter', _('Фильтр')),
    )

    session = models.ForeignKey(ImageEditSession, ...)
    operation_type = models.CharField(choices=OPERATION_TYPE_CHOICES, ...)
    parameters = models.JSONField()
    order = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
```

### Веб-интерфейс

#### ImageEditorView
Отображение редактора изображений.

```python
class ImageEditorView(SingleObjectDetailView):
    model = DocumentFile
    object_permission = permission_image_edit
    template_name = 'image_editor/editor.html'
```

#### ImageEditorSaveView
Сохранение отредактированного изображения.

```python
class ImageEditorSaveView(ExternalObjectViewMixin, View):
    def post(self, request, *args, **kwargs):
        # Конвертация в выбранный формат (JPEG, PNG, WebP, TIFF)
        # Создание новой версии документа
```

**Поддерживаемые форматы экспорта:**
- JPEG
- PNG
- WebP
- TIFF

### JavaScript функциональность

#### Основные функции редактора
- Инициализация canvas
- Обработка инструментов (поворот, отражение, обрезка)
- Управление яркостью/контрастом
- Сохранение через AJAX с CSRF защитой

```javascript
function handleToolClick(event) {
    const button = event.currentTarget;
    currentTool = button.getAttribute('data-tool');

    switch (currentTool) {
        case 'rotate-left':
        case 'rotate-right':
        case 'flip-horizontal':
        case 'flip-vertical':
        case 'crop':
            // Обработка инструментов
    }
}

function handleSave() {
    canvas.toBlob(function(blob) {
        // Отправка на сервер для сохранения
    }, 'image/png');
}
```

## 3. Модуль DAM - AI-анализ и автоматизированная обработка

### AI-провайдеры

Система поддерживает несколько AI-провайдеров для анализа изображений:

#### Локальная модель Qwen
```python
class LocalQwenVisionProvider(BaseAIProvider):
    def analyze_image(self, image_data, mime_type):
        # Анализ через локальную модель
```

#### GigaChat
```python
class GigaChatProvider(BaseAIProvider):
    def analyze_image(self, image_data, mime_type):
        # Анализ через GigaChat API
```

#### OpenAI
```python
class OpenAIProvider(BaseAIProvider):
    def analyze_image(self, image_data, mime_type):
        # Анализ через GPT-4 Vision
```

#### Claude (Anthropic)
```python
class ClaudeProvider(BaseAIProvider):
    def analyze_image(self, image_data, mime_type):
        # Анализ через Claude
```

#### Gemini (Google)
```python
class GeminiProvider(BaseAIProvider):
    def analyze_image(self, image_data, mime_type):
        # Анализ через Gemini
```

#### YandexGPT
```python
class YandexGPTProvider(BaseAIProvider):
    def analyze_image(self, image_data, mime_type):
        # Анализ через YandexGPT
```

#### Kie.ai
```python
class KieAIProvider(BaseAIProvider):
    def analyze_image(self, image_data, mime_type):
        # Анализ через Kie.ai API
```

### Основные функции обработки изображений

#### get_document_image_data
Получение данных изображения документа.

```python
def get_document_image_data(document_file: DocumentFile) -> bytes:
    """
    Get document image data. For image files, read directly.
    For documents, use internal generation.
    """
```

#### _shrink_image_bytes
Уменьшение размера изображения для оптимизации.

```python
def _shrink_image_bytes(image_data: bytes, max_width: int = 1600) -> bytes:
    """
    Downscale raw image bytes to a JPEG preview to reduce payload size.
    """
```

#### perform_ai_analysis
Основная функция AI-анализа изображений.

```python
def perform_ai_analysis(document_file: DocumentFile) -> Dict[str, Any]:
    """
    Perform AI analysis using available providers.
    """
```

**Возвращаемые данные:**
- `description` - AI-generated описание
- `tags` - AI-generated теги
- `colors` - доминирующие цвета
- `alt_text` - альтернативный текст
- `categories` - категории
- `language` - язык
- `people` - распознанные люди
- `locations` - распознанные локации
- `copyright` - информация об авторских правах
- `usage_rights` - права использования
- `provider` - использованный AI-провайдер

#### analyze_document_with_ai (Celery task)
Асинхронный анализ документа с AI.

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60, queue='documents')
def analyze_document_with_ai(self, document_id: int):
    """
    Analyze document with AI and update metadata.
    """
```

### Вспомогательные сервисы

#### YandexDiskClient
Клиент для работы с Yandex Disk API.

```python
class YandexDiskClient:
    def list_directory(self, path: str) -> List[Dict]:
    def iter_file(self, path: str, chunk_size: int = 1024 * 1024) -> Iterable[bytes]:
    def ping(self) -> Dict:
```

#### YandexDiskImporter
Импорт файлов из Yandex Disk в систему.

```python
class YandexDiskImporter:
    def run(self) -> int:
    def _import_directory(self, path: str, parent_cabinet: Cabinet) -> None:
    def _import_file(self, item: Dict, cabinet: Cabinet) -> None:
```

#### KieAIClient
Клиент для работы с Kie.ai API.

```python
class KieAIClient:
    def upload_file(self, file_name, file_bytes, upload_path) -> Dict[str, Any]:
    def recognize_image(self, download_url, target_language=None, prompt=None) -> Dict[str, Any]:
    def extract_text(self, file_name, file_bytes, upload_path=None, target_language=None) -> Dict[str, Any]:
```

### Конфигурация

#### Настройки AI-анализа
- `DAM_AI_ANALYSIS_ENABLED` - включение AI анализа
- `DAM_AI_ANALYSIS_AUTO_TRIGGER` - автоматический запуск
- `DAM_AI_ANALYSIS_TIMEOUT` - таймаут анализа
- `DAM_AI_PROVIDERS_ACTIVE` - активные провайдеры
- `DAM_AI_PROVIDER_FALLBACK` - fallback на другие провайдеры

#### Настройки производительности
- `DAM_ANALYSIS_QUEUE` - очередь Celery
- `DAM_ANALYSIS_PRIORITY` - приоритет задач
- `DAM_ANALYSIS_CONCURRENT_LIMIT` - лимит одновременных задач

#### Настройки изображений
- `DAM_ANALYSIS_TEXT_MAX_LENGTH` - максимальная длина текста
- `DAM_ANALYSIS_IMAGE_MAX_SIZE` - максимальный размер файла
- `DAM_ANALYSIS_METADATA_FORMAT` - формат метаданных

## 4. Интеграции с внешними сервисами

### Yandex Disk
- Импорт файлов из облачного хранилища
- Синхронизация с кабинетами документов
- Отслеживание импортированных файлов

### Kie.ai
- OCR и анализ изображений
- Загрузка файлов в облачное хранилище
- Получение структурированного текста

## 5. Архитектурные особенности

### Асинхронная обработка
- Все тяжелые операции выполняются через Celery
- Поддержка повторных попыток при сбоях
- Управление очередями и приоритетами

### Кеширование
- Автоматическое кеширование результатов трансформаций
- Оптимизация повторных операций

### Масштабируемость
- Поддержка распределенной обработки
- Оптимизация для больших файлов
- Graceful degradation при недоступности сервисов

### Безопасность
- Валидация входных данных
- Ограничения на размер файлов
- Защита от злоупотреблений API

## 6. Мониторинг и логирование

### Логирование операций
- Детальное логирование всех операций
- Отслеживание ошибок и исключений
- Метрики производительности

### Отслеживание прогресса
- Статусы операций анализа
- Прогресс-бары в интерфейсе
- Уведомления о завершении

---

*Документация создана на основе анализа кода Prime-EDMS. Актуально на текущую дату разработки системы.*
