<!-- 301f8a9e-ba69-4236-b6bc-7b26e1853056 7c7e585a-b63b-4c00-a115-2d905880947c -->
# DAM Distribution/Publishing: детальный план внедрения

**Технические детали выполнения:**
- Все команды терминала выполняются через `wsl bash -c` (среда WSL).
- Рабочая директория: корень проекта `Prime-EDMS`.
- Тестирование: через Docker Compose (`docker-compose up -d`).

## Область и результат

- Модуль публикации материалов с управлением получателями, пресетами рендишенов, токен‑порталом скачивания и базовой аналитикой. Совместим с текущим `converter_pipeline_extension` и инфраструктурой Mayan.

## Данные/модели (MVP)

- Recipient(email, name, organization, locale?)
- RecipientList(name, recipients M2M, internal_users M2M)
- RenditionPreset(resource_type: image|video|document, format, width, height, quality, watermark JSON)
- Publication(owner, title, description, access_policy: public|login|both, expires_at, max_downloads?, presets M2M, recipient_lists M2M)
- PublicationItem(publication FK, document_file FK)
- ShareLink(publication FK, token, recipient FK null, expires_at, max_downloads, downloads_count)
- GeneratedRendition(publication_item FK, preset FK, file/path, status, size, checksum)
- AccessLog(share_link, event: view|download, ip, ua, timestamp)

## Backend/API/URL

- DRF CRUD: recipients, lists, presets, publications, items
- Portal: `GET /publish/<token>/` (список материалов и рендишенов), `GET /publish/<token>/download/<item_id>/<preset>/`
- Admin views: мастер публикации (3 шага: получатели → пресеты → доступ)
- Swagger описания, версии API в `rest_api`

## Конвертация/рендишены

- Использовать `converter_pipeline_extension` как движок; маппинг пресета → параметры конвертации.
- Асинхронно (Celery). Таск: GenerateRenditions(publication_id) → на каждый `PublicationItem × Preset` создаёт `GeneratedRendition`.
- Кеширование превью; повторная генерация по изменению пресета.

## Доставка/доступ

- Токены: UUIDv4 + БД, проверка срока/лимитов; персональные или общий.
- Stronghold: whitelist `^/publish/.*$`; сами файлы отдавать через вью с проверкой.
- Email рассылка: персональная ссылка, шаблон письма.

## Настройки

- `DISTRIBUTION_RENDITION_PRESETS` (дефолты)
- `DISTRIBUTION_DEFAULT_EXPIRATION_DAYS`, `DISTRIBUTION_MAX_DOWNLOADS`
- `DISTRIBUTION_FFMPEG_PATH`, `DISTRIBUTION_CONVERT_TIMEOUT`
- `DISTRIBUTION_STORAGE` (локально/S3), `DISTRIBUTION_WATERMARK_DEFAULTS`

## Безопасность

- Проверка прав на исходные `DocumentFile` при включении в публикацию.
- Подпись токенов хранением в БД; водяные знаки по e‑mail (опционально).
- Rate‑limit на `download`, логирование `AccessLog`.

## Изменяемые/добавляемые файлы

- `config.yml`: `common.extra_apps: - mayan.apps.distribution`
- `mayan/settings/base.py`: добавить `/publish/` в `STRONGHOLD_PUBLIC_URLS`, блок `DISTRIBUTION_*`
- `mayan/apps/distribution/`:
- `apps.py`, `models.py`, `serializers.py`, `permissions.py`
- `views/portal.py`, `views/admin.py`, `urls.py`
- `tasks.py`, `emails.py`, `admin.py`, `links.py`, `templates/distribution/*`
- Интеграция меню: bind ссылки "Publish/Share" в списке документов
- Документация: `docs/prime/publishing.md`

## Разработка с учётом docs/prime

При разработке учитывать документы из `docs/prime`:
- `development_guide.md`: следовать архитектуре расширений (наследование от `MayanAppConfig`, структура файлов, интеграция с Mayan UI/API).
- `quick_start.md`: адаптировать под новое расширение (шаги создания, подключения, шаблоны файлов).
- `actions_menu_guide.md`: интеграция меню "Publish/Share" в раздел файлов/документов.
- `troubleshooting.md`: решения типичных проблем (ошибки миграций, URL, права).

## Детальные этапы внедрения (последовательно)

Разбито на 6 фаз для минимизации рисков поломки текущей реализации. Каждый этап включает зависимости, файлы, время, критерии и риски.

### Фаза 1: Foundation (База — независимые настройки и модели)
1. **Создание скелета приложения и базовые настройки**  
   - Зависимости: Нет.  
   - Файлы: `config.yml` (добавить `mayan.apps.distribution`), `mayan/settings/base.py` (блок `DISTRIBUTION_*` + `/publish/` в `STRONGHOLD_PUBLIC_URLS`), создать `mayan/apps/distribution/__init__.py`, `apps.py`, `permissions.py`.  
   - Время: 2–4 часа.  
   - Критерии: Система запускается без ошибок, приложение регистрируется.  
   - Риски: Конфликт с `STRONGHOLD_PUBLIC_URLS` — протестировать публичные URL. Mitigation: Минимальные изменения, бэкап настроек.

2. **Модели и миграции**  
   - Зависимости: Этап 1.  
   - Файлы: `mayan/apps/distribution/models.py` (все 8 моделей), `admin.py` (базовый админ), миграции.  
   - Время: 4–6 часов.  
   - Критерии: Миграции применяются, модели видны в админке, нет ошибок импортов.  
   - Риски: Конфликт полей с Mayan-моделями — проверить уникальность имён. Mitigation: Использовать префикс `distribution_` в именах полей.

### Фаза 2: Core (Ядро — API и логика)
3. **Права доступа и сериализаторы DRF**  
   - Зависимости: Этапы 1–2.  
   - Файлы: `mayan/apps/distribution/serializers.py`, `permissions.py` (расширить), базовый `urls.py`.  
   - Время: 4–6 часов.  
   - Критерии: DRF API отвечает, права работают.  
   - Риски: Конфликт с Mayan-правами — использовать namespace `distribution.`. Mitigation: Тестировать с существующими ролями.

4. **CRUD и Swagger для recipients/lists/presets/publications/items**  
   - Зависимости: Этап 3.  
   - Файлы: `mayan/apps/distribution/views/admin.py`, `urls.py` (расширить), интеграция с `rest_api`.  
   - Время: 6–8 часов.  
   - Критерии: CRUD работает через API/Swagger.  
   - Риски: Перегрузка БД — тестировать с небольшими данными. Mitigation: Использовать индексы на FK.

### Фаза 3: UI/Portal (Интерфейс и портал)
5. **Мастер публикации и меню Publish/Share**  
   - Зависимости: Этапы 1–4.  
   - Файлы: `mayan/apps/distribution/links.py`, `views/admin.py` (мастер вью), `templates/distribution/wizard.html`, bind в `apps.py`.  
   - Время: 6–8 часов.  
   - Критерии: Пункт меню появляется, мастер работает.  
   - Риски: Конфликт с Mayan-шаблонами — использовать inheritance от `appearance/base.html`. Mitigation: Тестировать на разных страницах.

6. **Генерация ShareLink и email-рассылка**  
   - Зависимости: Этап 5.  
   - Файлы: `mayan/apps/distribution/emails.py`, `tasks.py` (базовая задача), интеграция с `mayan.apps.mailer`.  
   - Время: 4–6 часов.  
   - Критерии: Ссылки генерируются, email отправляются.  
   - Риски: SMTP-ошибки — использовать локальный email. Mitigation: Mock-тесты для email.

7. **Портал publish/<token>/ и скачивание**  
   - Зависимости: Этапы 5–6.  
   - Файлы: `mayan/apps/distribution/views/portal.py`, `templates/distribution/portal.html`, `urls.py` (добавить portal).  
   - Время: 6–8 часов.  
   - Критерии: Портал открывается, скачивание работает.  
   - Риски: Stronghold блокирует — whitelist только `/publish/`. Mitigation: Тестировать анонимно и залогинено.

### Фаза 4: Async/Integration (Асинхронные задачи и интеграция)
8. **Celery-таски генерации рендишенов**  
   - Зависимости: Этапы 1–7.  
   - Файлы: `mayan/apps/distribution/tasks.py` (GenerateRenditions), интеграция с Celery.  
   - Время: 4–6 часов.  
   - Критерии: Таски запускаются, статусы обновляются.  
   - Риски: Celery не работает — проверить конфиг. Mitigation: Локальный запуск задач.

9. **Интеграция с converter_pipeline_extension**  
   - Зависимости: Этап 8.  
   - Файлы: Маппинг пресетов в `tasks.py`, вызов методов из существующего конвертера.  
   - Время: 6–8 часов.  
   - Критерии: Рендишены генерируются асинхронно.  
   - Риски: Конфликт с существующим кодом — изолировать в отдельном таске. Mitigation: Тестировать на копии конвертера.

10. **Логирование доступа и счётчики**  
    - Зависимости: Этап 7.  
    - Файлы: `mayan/apps/distribution/models.py` (расширить AccessLog), логика в portal views.  
    - Время: 2–4 часа.  
    - Критерии: Скачивания логируются.  
    - Риски: Перегрузка логов — ограничить объём. Mitigation: Индексы на AccessLog.

### Фаза 5: Enhancements (Улучшения)
11. **Watermark и видео-пресеты**  
    - Зависимости: Этап 9.  
    - Файлы: Расширить `tasks.py` и `converter_pipeline_extension`.  
    - Время: 4–6 часов.  
    - Критерии: Рендишены с watermark.  
    - Риски: FFmpeg ошибки — fallback на оригинал. Mitigation: Тестировать с разными форматами.

12. **Rate-limit и базовая аналитика**  
    - Зависимости: Этап 10.  
    - Файлы: Rate-limit в portal views, отчёты в admin.  
    - Время: 2–4 часа.  
    - Критерии: Скачивания ограничиваются.  
    - Риски: Перегрузка — кеширование. Mitigation: Настроить лимиты.

### Фаза 6: Финализация (Документация и тесты)
13. **Документация и Swagger**  
    - Зависимости: Все этапы.  
    - Файлы: `docs/prime/publishing.md`, обновить Swagger.  
    - Время: 2–4 часа.  
    - Критерии: Документация готова.  
    - Риски: Нет.

14. **Тесты и финальная проверка**  
    - Зависимости: Все этапы.  
    - Файлы: `mayan/apps/distribution/tests/`, unit/functional тесты.  
    - Время: 4–6 часов.  
    - Критерии: Тесты проходят, end-to-end работает.  
    - Риски: Ложные срабатывания — интеграционные тесты. Mitigation: Покрыть 80% кода.

## Этапы (инкрементально)

1) Скелет приложения и модели (миграции, админ): Recipient, RecipientList, RenditionPreset, Publication, PublicationItem, ShareLink, GeneratedRendition, AccessLog.
2) CRUD + DRF + Swagger для recipients/lists/presets/publications/items; права доступа.
3) Мастер публикации в UI и генерация ShareLink(ов), email отправка.
4) Портал `publish/<token>/`, скачивание с проверками, логирование доступа.
5) Celery генерация рендишенов, интеграция с конвертером, отображение статусов.
6) Улучшения: watermark, видео‑пресеты, rate‑limit, базовая аналитика и отчёты.

## Критерии готовности MVP

- Публикация создаётся из выбранных `DocumentFile`, выдаются токен‑ссылки, изображения/PDF рендерятся асинхронно; скачивания учитываются; права и сроки соблюдаются; минимальная документация и Swagger готовы.

### To-dos

- [ ] Исправить скрипт в docs: start_app.sh → add_app.sh
- [ ] Добавить проверку прав в MediaConversionView
- [ ] Вынести таймаут/форматы/FFmpeg путь в настройки
- [ ] Перевести конвертацию в Celery задачу
- [ ] Сделать конвертацию приватной, редирект — публичным
- [ ] Написать тесты для converter_pipeline_extension
- [ ] Добавить структурное логирование и обработку ошибок
- [ ] Обновить quick_start и README под новые настройки/потоки
- [ ] Создать шаблон/скрипт генерации расширений


