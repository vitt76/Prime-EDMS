# ТЗ: Главная страница DAM системы (MADDAM)
**Версия:** 1.0  
**Дата:** Февраль 2026  
**Статус:** План разработки  
**Целевой уровень:** Enterprise DAM (аналоги: Bynder, Brandfolder, AEM Assets, Cloudinary)

---

## Оглавление

1. [Цель и видение](#1-цель-и-видение)
2. [Текущее состояние и боли](#2-текущее-состояние-и-боли)
3. [Архитектура главной страницы](#3-архитектура-главной-страницы)
4. [Детальное описание блоков](#4-детальное-описание-блоков)
5. [Требования по взаимодействию (Interaction Model)](#5-требования-по-взаимодействию)
6. [Приоритеты и фазы разработки](#6-приоритеты-и-фазы-разработки)
7. [Технические требования](#7-технические-требования)
8. [Метрики успеха](#8-метрики-успеха)

---

## 1. Цель и видение

### 1.1 Цель

Переформатировать главную страницу DAM из **статического дашборда состояния** в **динамическое персональное рабочее пространство**, которое:
- Концентрирует внимание на задачах и действиях пользователя.
- Демонстрирует ценность AI в контексте конкретных проблем.
- Встраивает командную коллаборацию в ежедневный workflow.
- Превращает каждую метрику в entry point к действию.

### 1.2 Целевые роли

1. **Маркетолог (Content Manager)** — нужны последние кампании, активы без тегов, готовые к использованию.
2. **Дизайнер (Creative)** — нужны последние брифы, одобренные активы, коллекции от PM.
3. **Brand Manager** — нужен контроль: что скачивают, что нарушает гайды, что устаревает.
4. **Admin** — общие метрики, система здоровья, управление пользователями.

### 1.3 Вдохновение и лучшие практики

Учтены паттерны из:
- **Bynder**: персональный inbox, смарт‑рекомендации, интеграция с коллаборацией.
- **Figma**: "Last Used", "Shared with You", быстрый переключатель контекста.
- **Notion**: "All Databases", сохранённые фильтры, AI‑блоки с action items.
- **Slack**: feed‑модель с группировкой, упоминаниями, priorities.
- **Cloudinary**: метрики → actions (bandwidth → optimize, errors → fix).

---

## 2. Текущее состояние и боли

### 2.1 Что работает сейчас (Strengths)

- ✅ Чистая иерархия: информация > контент > действия.
- ✅ CTA "Загрузить" на видное месте.
- ✅ Блок "Недавние активы" + "Активность" дают контекст.
- ✅ Метрики "Хранилище" ясно коммуницируют состояние.

### 2.2 Что болит (Pain Points)

| Боль | Следствие |
|------|-----------|
| **Нет персонализации по ролям** | Админ видит то же, что маркетолог. Каждый должен искать «своё» на странице. |
| **Метрики без действий** | "Завершённых анализов: 1" — и что дальше? Нет CTA. |
| **Нет inbox'а уведомлений** | Пользователь не видит: комментарии ко мне, запросы одобрения, новые коллекции. |
| **AI вполне невидима на главной** | AI делает анализы, но это скрыто за счётчиком. Нет инсайтов. |
| **Поиск изолирован** | Поиск в хедере, но историей/сохранёнными поисками можно манипулировать только зайдя в «Галерею». |
| **Коллаборация не подана** | Нет «кто со мной поделился», «в чём ждут мой отзыв», «где я упомянут(а)». |
| **Недостаточно quick‑actions** | Если нужно что‑то сделать быстро (загрузить, добавить в коллекцию, поделиться), нужно прыгать по страницам. |

---

## 3. Архитектура главной страницы

### 3.1 Макет (High-Level Layout)

```
┌─────────────────────────────────────────────────────────────────┐
│  ШАПКА (неизменна): Поиск + Загрузить + Уведомления + Профиль  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [HSTACK: 3 приоритетные KPI-карточки + AI-инсайт]              │
│  ├─ Всего активов / Новых за 7 дней + "Обзор"                  │
│  ├─ AI анализы готовы / В очереди + "Запустить недостающие"    │
│  ├─ Мне нужно сделать (Комментарии/Одобрения/Упоминания)      │
│  └─ [AI Smart Card] "10 активов без описания. Генерировать?"    │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  [VSTACK: 2-column layout]                                       │
│                                                                   │
│  LEFT (60%):                                                      │
│  ┌─────────────────────────────────────┐                         │
│  │ "Мой inbox" (Задачи & Уведомления)  │                         │
│  │ ├─ Новые комментарии (3)             │                         │
│  │ ├─ Ожидают одобрения (1)             │                         │
│  │ ├─ Поделились коллекции (2)          │                         │
│  │ └─ [Показать все]                   │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  ┌─────────────────────────────────────┐                         │
│  │ "Последние активы" (Smart Grid)      │                         │
│  │ ├─ [Tab: Недавние / Избранное]       │                         │
│  │ ├─ [Filter: Тип контента]            │                         │
│  │ └─ [Grid 3-4 items + "Показать всё"] │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  ┌─────────────────────────────────────┐                         │
│  │ "Лента активности" (Timeline)        │                         │
│  │ ├─ Group by: Новые загрузки (4)      │                         │
│  │ ├─ Group by: Комментарии (7)         │                         │
│  │ ├─ Group by: Публикации (2)          │                         │
│  │ └─ [Опции фильтрации]                │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  RIGHT (40%):                                                     │
│  ┌─────────────────────────────────────┐                         │
│  │ "Быстрые действия" (Floating Panel)  │                         │
│  │ ├─ [🚀] Запустить AI‑анализ на N    │                         │
│  │ ├─ [🔍] Найти дубликаты              │                         │
│  │ ├─ [🏷️] Завершить тегирование       │                         │
│  │ ├─ [📊] Посмотреть аналитику         │                         │
│  │ └─ [📤] Экспортировать отчёт         │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  ┌─────────────────────────────────────┐                         │
│  │ "Сохранённые поиски & Коллекции"    │                         │
│  │ ├─ 📌 Кампания 'Весна 2026'          │                         │
│  │ ├─ 📌 Одобренные для соцсетей        │                         │
│  │ ├─ ⭐ Брендовые Key Visuals           │                         │
│  │ └─ [Управлять]                      │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
│  ┌─────────────────────────────────────┐                         │
│  │ "Хранилище & Квоты"                 │                         │
│  │ ├─ Используется: 195.8 KB / 500 GB  │                         │
│  │ ├─ [Progress bar 0%)                │                         │
│  │ ├─ Рекомендация: Найти крупные      │                         │
│  │ └─ [→ Открыть управление]            │                         │
│  └─────────────────────────────────────┘                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Компоненты и их позиция

| Компонент | Позиция | Приоритет | Фаза |
|-----------|---------|-----------|------|
| **KPI Bar (Top)** | Над контентом | P0 (MUST) | 1 |
| **My Inbox** | Левая колонка, первый блок | P0 (MUST) | 1 |
| **Recent Assets** | Левая колонка, второй блок | P1 (SHOULD) | 1 |
| **Activity Feed** | Левая колонка, третий блок | P1 (SHOULD) | 2 |
| **Quick Actions Panel** | Правая колонка, fixed | P0 (MUST) | 1 |
| **Saved Searches** | Правая колонка | P2 (NICE) | 2 |
| **Storage & Quotas** | Правая колонка, внизу | P1 (SHOULD) | 1 |

---

## 4. Детальное описание блоков

### 4.1 KPI Bar (Приоритетные метрики с действиями)

**Макет:** Горизонтальный скролл-контейнер (5-6 карточек), каждая 200x120px.

#### 4.1.1 Карточка "Активы: Всего / Новых"

**Данные:**
```
Всего документов
├─ 2 документа
└─ +0 за 7 дней
```

**Компоненты:**
- Заголовок: "Всего документов"
- Лейбел: "2 документа"
- Сабтекст: "+0 за 7 дней" (если отрицательно: серый, если положительно: зелёный)
- CTA кнопка: "→ Обзор"

**Клик на CTA:**
- Переход на `Галерея` с применённым фильтром `created_at > 7 дней назад`

**API endpoint:**
```
GET /api/v4/documents/stats/?organization_id=X&period=7days
→ {total: 2, new_7days: 0, new_30days: 5}
```

---

#### 4.1.2 Карточка "AI анализы"

**Данные:**
```
Завершённых анализов
├─ 1 с AI анализом
└─ 1 в очереди
```

**Компоненты:**
- Заголовок: "Завершённых анализов"
- Прогресс‑бар: 1/2 (зелёный, потом серый)
- Сабтекст: "1 в очереди"
- CTA кнопка: "⚡ Запустить недостающие"

**Клик на CTA:**
- Открыть диалог/сайдбар с фильтром `documents where ai_analysis is null`, предложить "Анализировать все" или выбрать вручную.
- На бэке: POST `/api/v4/ai-analysis/bulk-analyze/` с document IDs.

**API endpoint:**
```
GET /api/v4/documents/ai-stats/?organization_id=X
→ {analyzed: 1, queued: 1, pending: 3, failed: 0}
```

---

#### 4.1.3 Карточка "Мне нужно сделать" (Inbox Count)

**Данные:**
```
Требуется действие
├─ 3 новых комментария
├─ 1 ожидает одобрения
└─ 2 новые коллекции
```

**Компоненты:**
- Заголовок: "Требуется действие"
- Большой номер: "6" (сумма всех)
- Сабтекст: "3 комм. / 1 одобр. / 2 кол."
- CTA кнопка: "📬 Открыть"

**Клик на CTA:**
- Скролл вниз к блоку "My Inbox" (или переход на отдельную страницу `/notifications`).

**API endpoint:**
```
GET /api/v4/user/inbox-stats/?organization_id=X
→ {comments_new: 3, approvals_pending: 1, collections_shared: 2, mentions: 0}
```

---

#### 4.1.4 Карточка "AI Insights & Smart Recommendations"

**Концепция:** Каждый день система генерирует 1-2 actionable инсайта.

**Примеры:**
- "⚠️ 10 активов без описания. Генерировать с AI?"
- "🔄 5 возможных дубликатов найдено. Проверить?"
- "📊 3 архивных актива никогда не скачивали. Удалить?"
- "🏷️ Недостаёт тегов в 7 активах из последней загрузки."

**Данные (Daily Recalc via Celery Task):**
```python
# Celery task, runs daily at 09:00 UTC
@periodic_task(run_every=crontab(hour=9, minute=0))
def generate_daily_insights(organization_id):
    insights = []
    
    # Insight 1: Untagged Assets
    untagged = Document.objects.filter(
        organization=org,
        ai_tags__isnull=True,
        created_at__gte=now() - timedelta(days=7)
    ).count()
    if untagged > 0:
        insights.append({
            'type': 'auto_tag_missing',
            'count': untagged,
            'cta': 'Run AI Tagging',
            'emoji': '🏷️'
        })
    
    # Insight 2: Possible Duplicates
    # (pseudo-code, требует реализации хеш-сравнения)
    duplicates = find_duplicate_hashes(org)
    if len(duplicates) > 0:
        insights.append({...})
    
    # Insight 3: Unused Old Assets
    unused = Document.objects.filter(
        organization=org,
        created_at__lt=now() - timedelta(days=180),
        download_count=0
    ).count()
    if unused > 3:
        insights.append({...})
    
    # Store top 1-2 insights in cache/DB
    cache.set(f'insights_{org.id}', insights[:2], 86400)
```

**Компоненты на UI:**
- Заголовок: "💡 AI Инсайты"
- Основной текст: "10 активов без описания"
- Доп. текст: (умолчание опционально)
- CTA кнопка: "Сгенерировать описания"
- Кнопка dismiss: "✕" (hide на 24 часа)

**Клик на CTA:**
- Открыть диалог "Запустить AI для N активов" с preview.

**API endpoint:**
```
GET /api/v4/user/daily-insights/?organization_id=X
→ [
    {
        'type': 'auto_tag_missing',
        'count': 10,
        'cta_label': 'Generate Descriptions',
        'action_endpoint': '/api/v4/ai-analysis/bulk-analyze/',
        'emoji': '📝'
    }
]
```

---

### 4.2 My Inbox (Задачи и уведомления)

**Макет:** Vertical card stack (как Gmail inbox, но компактнее).

**Заголовок блока:** "📬 Мой inbox"  
**Метрика в заголовке:** Бейдж с числом непрочитанных.

#### 4.2.1 Группы уведомлений (collapsible)

| Группа | Иконка | Примеры | API |
|--------|--------|---------|-----|
| **Комментарии** | 💬 | "Maria in photo_123: 'Check colors'" | `GET .../comments/?mentioned=me&unread=true` |
| **Одобрения/Запросы** | ✋ | "PM: Одобрить выкладку кампании?" | `GET .../approvals/?assigned_to=me&status=pending` |
| **Коллекции** | 📌 | "John: Поделился коллекцией 'Q1 2026'" | `GET .../shares/?shared_with=me&type=collection` |
| **Упоминания** | @ | "@[you]: Проверь этот актив" | `GET .../mentions/?target=me&unread=true` |
| **Системные** | 🔔 | "Квота хранилища 80%", "Миграция завершена" | `GET .../system-alerts/?org=X` |

**Каждый item в группе:**

```
[Иконка профиля] [Имя] [действие]  [Время]
"Maria replied to photo_123.jpg"     "2h ago"

Сабтекст: "Check the colors of the product shot"

[Action buttons]:
├─ [→ Open]   # Ведёт к контексту (актив, коллекция)
├─ [✓ Mark Read]
└─ [...] (menu: Pin, Mute, Archive)
```

**Верх блока (Quick filters):**

```
[All] [Unread] [Mentions] [Approvals] [Collections]
```

**Клик на фильтр:**
- Переквалифицирует inbox, оставляя видимыми только нужные.

**底 блока:**

```
[→ Show All Notifications] (ведёт на `/notifications` или `/user/inbox`)
```

**API endpoints:**
```
GET /api/v4/user/inbox/?organization_id=X&limit=10
→ [
    {
        'id': 'notif_123',
        'type': 'comment',
        'actor': {'id': 1, 'name': 'Maria', 'avatar_url': '...'},
        'object': {'type': 'document', 'id': 'doc_456', 'label': 'photo_123.jpg'},
        'text': 'Check the colors of the product shot',
        'created_at': '2026-02-19T14:30:00Z',
        'is_read': False,
        'action_url': '/dam/assets/doc_456'
    },
    ...
]

GET /api/v4/user/inbox-counts/?organization_id=X
→ {
    'unread_total': 6,
    'comments': 3,
    'approvals': 1,
    'collections': 2,
    'mentions': 0
}
```

---

### 4.3 Recent Assets (Smart Grid)

**Макет:** CSS Grid 3-4 колонки (responsive), показывает 6-8 последних активов.

**Заголовок:** "📷 Последние активы"  
**Tab switcher:**
```
[Недавние] [Избранное] [Доступные мне] [Одобренные]
```

**Filter bar:**
```
[Тип контента: ▼] [Статус: ▼]
```

#### 4.3.1 Каждая карточка актива

```
┌─────────────────────────┐
│   [Thumbnail preview]   │  ← Клик = Open asset detail
│                         │
│ 📄 photo_5408984...jpg  │  ← Label (truncated)
│ ┌────────────────────┐  │
│ │ ⭐ ⬇️ 📌 🔗 ⋯     │  │  ← Quick action buttons
│ └────────────────────┘  │
└─────────────────────────┘

Buttons (на ховер):
├─ ⭐ Add to Favorites
├─ ⬇️ Download
├─ 📌 Add to Collection
├─ 🔗 Copy Link
└─ ⋯ More (menu)
```

**Клик на само изображение:**
- Открыть Asset Detail page / modal.

**API endpoint:**
```
GET /api/v4/documents/?organization_id=X&tab=recent&limit=8&order_by=-created_at
→ [
    {
        'id': 'doc_123',
        'label': 'photo_5408984.jpg',
        'thumbnail_url': '...',
        'file_type': 'image',
        'created_at': '2026-02-19T10:00:00Z',
        'is_favorited_by_me': False,
        'download_count': 5,
        'collection_count': 2
    },
    ...
]
```

---

### 4.4 Activity Feed (Timeline)

**Макет:** Вертикальная лента, сгруппирована по типам событий и дате.

**Заголовок:** "⏱️ Активность (последние 7 дней)"

**Группировка:**
```
┌─────────────────────────────────────┐
│ 📤 Новые загрузки (4)                │
├─────────────────────────────────────┤
│ • Maria uploaded 2 files (Today)     │
│ • John uploaded 1 file (Yesterday)   │
│ • Auto-conversion finished (2 days)  │
│ • System backup completed (3 days)   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 💬 Новые комментарии (7)             │
├─────────────────────────────────────┤
│ • Maria: "Fix colors" (1h ago)       │
│ • PM: "Approved for Q1" (4h ago)    │
│ • Designer: "Need revision" (1d ago) │
│ [Show all 7 comments]                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📊 Публикации & Шаринги (2)          │
├─────────────────────────────────────┤
│ • Collection "Q1 2026" published     │
│ • John shared Cabinet "Social Kit"   │
└─────────────────────────────────────┘
```

**Опции фильтрации (чекбоксы):**
```
☑️ Загрузки
☑️ Комментарии
☑️ Публикации
☑️ AI Анализы
☑️ Системные события
```

**"Show more" button:**
- Развернуть полную ленту или перейти на `/activity`.

**API endpoint:**
```
GET /api/v4/activity-feed/?organization_id=X&limit=20&days=7
→ [
    {
        'id': 'evt_001',
        'timestamp': '2026-02-19T14:30:00Z',
        'type': 'document_uploaded',
        'actor': {'id': 1, 'name': 'Maria', 'avatar': '...'},
        'details': {
            'count': 2,
            'files': ['photo1.jpg', 'photo2.jpg']
        },
        'icon': '📤'
    },
    {
        'id': 'evt_002',
        'timestamp': '2026-02-19T12:15:00Z',
        'type': 'comment_created',
        'actor': {'id': 2, 'name': 'PM User', 'avatar': '...'},
        'details': {
            'document_id': 'doc_123',
            'document_label': 'photo.jpg',
            'text': 'Fix colors please'
        },
        'icon': '💬'
    },
    ...
]
```

---

### 4.5 Quick Actions Panel (Right Sidebar)

**Макет:** Fixed sticky panel, 300px, right-aligned. На мобильном → drawer bottom или hamburger.

**Содержимое (top to bottom):**

#### 4.5.1 "Быстрые действия"

```
┌──────────────────────────────┐
│ ⚡ Быстрые действия           │
├──────────────────────────────┤
│                              │
│ [🚀 Запустить AI-анализ]    │
│  "для 3 активов без тегов"  │
│  → POST /ai-analysis/bulk   │
│                              │
│ [🔍 Найти дубликаты]        │
│  "сэкономить место"         │
│  → GET /documents/duplicates │
│                              │
│ [🏷️ Завершить тегирование]  │
│  "осталось 7 активов"       │
│  → /dam?filter=untagged     │
│                              │
│ [📊 Посмотреть аналитику]    │
│  "за последние 30 дней"     │
│  → /analytics               │
│                              │
│ [📤 Экспортировать отчёт]    │
│  "активность & метрики"     │
│  → /exports                 │
│                              │
└──────────────────────────────┘
```

**Каждый button:**
- Иконка (emoji или SVG)
- Заголовок (bold)
- Сабтекст (secondary, grey, 12px)
- Full-width CTA (padding 12px 16px)

**Клик:**
- Открыть диалог, сайдбар или редирект на соответствующий endpoint.

#### 4.5.2 "Сохранённые поиски и Коллекции"

```
┌──────────────────────────────┐
│ 🔖 Мои закладки               │
├──────────────────────────────┤
│                              │
│ 📌 Кампания 'Весна 2026'      │
│   (45 активов)               │
│   → Click: open filtered     │
│                              │
│ 📌 Одобренные для соцсетей   │
│   (128 активов)              │
│   → Click: open filtered     │
│                              │
│ ⭐ Брендовые Key Visuals      │
│   (32 актива)                │
│   → Click: open collection   │
│                              │
│ [+ Управлять] (→ /collections) │
│                              │
└──────────────────────────────┘
```

**API endpoint:**
```
GET /api/v4/user/saved-searches/?organization_id=X&limit=5
→ [
    {
        'id': 'ss_001',
        'name': 'Кампания Весна 2026',
        'query_params': {'tag': 'spring_2026', 'status': 'approved'},
        'document_count': 45,
        'icon': '📌'
    },
    ...
]

GET /api/v4/user/collections/?organization_id=X&limit=5
→ [
    {
        'id': 'cab_001',
        'label': 'Key Visuals',
        'document_count': 32,
        'is_favorite': True
    },
    ...
]
```

#### 4.5.3 "Хранилище & Квоты"

```
┌──────────────────────────────┐
│ 💾 Хранилище                  │
├──────────────────────────────┤
│                              │
│ Использовано:                │
│ 195.8 KB из 500 GB           │
│                              │
│ [████████░░░░░░░░░░] 0%     │
│                              │
│ Рекомендации:                │
│ • Найти крупные файлы (>50M) │
│   [→ Find Large]             │
│ • Найти возм. дубликаты      │
│   [→ Find Duplicates]        │
│                              │
│ [→ Управление хранилищем]   │
│                              │
└──────────────────────────────┘
```

**API endpoint:**
```
GET /api/v4/user/storage-info/?organization_id=X
→ {
    'used_bytes': 195800,
    'quota_bytes': 536870912000,  # 500 GB
    'usage_percent': 0.0000365,
    'recommendations': [
        {'type': 'large_files', 'count': 3, 'total_bytes': 2147483648},
        {'type': 'duplicates', 'count': 5, 'potential_savings': 1073741824}
    ]
}
```

---

### 4.6 Адаптивность и Responsive Design

| Breakpoint | Layout |
|------------|--------|
| **Desktop (1200px+)** | 2-column (60% left, 40% right) |
| **Tablet (768-1199px)** | 2-column, narrower right sidebar (300px → 280px) |
| **Mobile (<768px)** | 1-column stacked (right panel → drawer/tabs) |

На мобильном:
- Right panel становится **Bottom Sheet** (drawer) или **Tabs**.
- KPI Bar → Горизонтальный скролл (не переносится).
- My Inbox & Recent Assets переходят в **Collapse** (collapse-по-умолчанию).

---

## 5. Требования по взаимодействию (Interaction Model)

### 5.1 Персонализация по ролям

Главная **должна адаптироваться** в зависимости от `user.role` в текущей организации:

| Роль | KPI Priority | Quick Actions | Inbox Focus | Notes |
|------|--------------|---------------|-------------|-------|
| **Brand Manager** | Stock alerts, Compliance breaches, Watermark errors | Audit logs, Find violations, Export compliance report | Approvals, System alerts | Контроль и соответствие |
| **Content Manager** | New uploads, AI analysis %, Engagement metrics | Auto-tag, Find missing descriptions, Export for campaign | Comments, Shared collections | Скорость, эффективность |
| **Designer/Creative** | Latest briefings, Approved assets, My uploads | Quick collections, Download approved | Feedback, Design requests | Инструменты, колаборация |
| **Admin** | System health, User activity, Storage %, API errors | Manage users, View audit logs, System settings | System alerts, Errors | Управление системой |

**На бэке:**

```python
# models.py
class UserRole(models.TextChoices):
    ADMIN = 'admin'
    BRAND_MANAGER = 'brand_manager'
    CONTENT_MANAGER = 'content_manager'
    DESIGNER = 'designer'
    CONTRIBUTOR = 'contributor'

class UserOrganizationProfile(models.Model):
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization)
    role = models.CharField(max_length=20, choices=UserRole.choices)

# serializers.py
class HomepageConfigSerializer(serializers.Serializer):
    """
    Возвращает конфигурацию главной страницы в зависимости от роли пользователя.
    """
    def to_representation(self, obj):
        user_role = obj.user_profile.role
        
        config = {
            'kpi_metrics': self.get_kpi_for_role(user_role),
            'quick_actions': self.get_actions_for_role(user_role),
            'inbox_groups': self.get_inbox_for_role(user_role),
        }
        return config
```

**На фронте:**

```vue
<!-- pages/index.vue (Главная) -->
<template>
  <div v-if="config" class="home-page">
    <!-- KPI Bar -->
    <KPIBar :metrics="config.kpi_metrics" />
    
    <!-- Main Content -->
    <div class="content-grid">
      <!-- Left Column -->
      <div class="col-left">
        <MyInbox :groups="config.inbox_groups" />
        <RecentAssets :tab="config.recent_assets_tab" />
        <ActivityFeed v-if="config.show_activity_feed" />
      </div>
      
      <!-- Right Column -->
      <aside class="col-right">
        <QuickActionsPanel :actions="config.quick_actions" />
        <SavedSearchesPanel v-if="config.show_saved_searches" />
        <StoragePanel />
      </aside>
    </div>
  </div>
</template>

<script setup>
const { data: config } = await useFetch('/api/v4/homepage/config/')
</script>
```

---

### 5.2 State Management

**Использовать:** Pinia (Vue 3 state management).

```typescript
// stores/homeStore.ts
import { defineStore } from 'pinia'

export const useHomeStore = defineStore('home', {
  state: () => ({
    config: null,
    inbox: {
      items: [],
      unreadCount: 0,
      selectedFilter: 'all' // 'all' | 'unread' | 'mentions' | 'approvals'
    },
    recentAssets: {
      items: [],
      selectedTab: 'recent' // 'recent' | 'favorites' | 'accessible' | 'approved'
    },
    activityFeed: {
      items: [],
      filters: {
        uploads: true,
        comments: true,
        publications: true,
        ai_analysis: true,
        system: true
      }
    },
    isLoading: false,
    error: null
  }),

  getters: {
    inboxItemsForFilter: (state) => {
      const filter = state.inbox.selectedFilter
      if (filter === 'all') return state.inbox.items
      return state.inbox.items.filter(item => item.type === filter)
    }
  },

  actions: {
    async fetchHomepageConfig() {
      this.isLoading = true
      try {
        const { data } = await $fetch('/api/v4/homepage/config/')
        this.config = data
      } catch (err) {
        this.error = err.message
      } finally {
        this.isLoading = false
      }
    },

    async fetchInbox() {
      const { data } = await $fetch('/api/v4/user/inbox/')
      this.inbox.items = data
      this.inbox.unreadCount = data.filter(i => !i.is_read).length
    },

    setInboxFilter(filter) {
      this.inbox.selectedFilter = filter
    }
  }
})
```

---

### 5.3 Real-Time Updates (WebSocket)

Для "живых" уведомлений используем **WebSocket** (например, через Django Channels):

```python
# consumers.py
class HomepageConsumer(AsyncWebsocketConsumer):
    """
    Sends real-time updates for homepage:
    - New comments
    - New notifications
    - Activity feed
    - AI analysis completion
    """
    async def connect(self):
        self.user = self.scope["user"]
        self.organization_id = self.scope["url_route"]["kwargs"]["organization_id"]
        
        await self.channel_layer.group_add(
            f"homepage_{self.organization_id}_{self.user.id}",
            self.channel_name
        )
        await self.accept()

    async def notification_created(self, event):
        """Sends new notification to client"""
        await self.send(text_data=json.dumps({
            'type': 'notification_created',
            'notification': event['notification']
        }))

    async def activity_created(self, event):
        """Sends new activity to client"""
        await self.send(text_data=json.dumps({
            'type': 'activity_created',
            'activity': event['activity']
        }))
```

```javascript
// composables/useHomepageWS.ts
export const useHomepageWS = () => {
  const ws = ref(null)
  const homeStore = useHomeStore()

  const connect = (organizationId) => {
    ws.value = new WebSocket(
      `wss://${window.location.host}/ws/homepage/${organizationId}/`
    )

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      switch (data.type) {
        case 'notification_created':
          homeStore.inbox.items.unshift(data.notification)
          homeStore.inbox.unreadCount++
          break
        
        case 'activity_created':
          homeStore.activityFeed.items.unshift(data.activity)
          break
      }
    }
  }

  return { connect, ws }
}
```

---

## 6. Приоритеты и фазы разработки

### 6.1 Приоритизация (MoSCoW)

| Категория | Компоненты | Сложность | Фаза |
|-----------|-----------|-----------|------|
| **MUST** (P0) | KPI Bar (3 карточки), My Inbox, Quick Actions | Low-Medium | 1 |
| **SHOULD** (P1) | Recent Assets, Activity Feed, Storage Panel | Medium | 1-2 |
| **NICE** (P2) | AI Insights card, Saved Searches, Advanced filters | Medium-High | 2-3 |
| **COULD** (P3) | Role-based personalization advanced, Real-time WS | High | 3 |

### 6.2 Фазы реализации

#### **ФАЗА 1 (Week 1-2): MVP "Рабочее пространство"** 

**Цель:** Минимально жизнеспособный продукт для замены старой главной.

**Включает:**
- ✅ KPI Bar (3 карточки: Активы, AI анализы, Мне нужно сделать)
- ✅ My Inbox (комментарии, одобрения, коллекции)
- ✅ Recent Assets (6 карточек, таб "Недавние")
- ✅ Quick Actions Panel (базовые действия)
- ✅ Storage Panel

**Backend:**
- Endpoints: `/api/v4/documents/stats/`, `/api/v4/documents/ai-stats/`, `/api/v4/user/inbox-stats/`, `/api/v4/user/inbox/`, `/api/v4/documents/?tab=recent`, `/api/v4/user/storage-info/`
- Миграции: Ничего не требуется (используются существующие модели).

**Frontend:**
- Pages: `pages/index.vue` (Главная)
- Components: `KPIBar.vue`, `MyInbox.vue`, `RecentAssets.vue`, `QuickActionsPanel.vue`, `StoragePanel.vue`
- Store: `stores/homeStore.ts`

**QA:**
- Unit: Components загружаются и рендерятся.
- Integration: API endpoints возвращают корректные данные.
- E2E: Клики работают, переходы логичны.

---

#### **ФАЗА 2 (Week 3-4): Обогащение + Инсайты**

**Цель:** Добавить AI‑рекомендации и расширенную активность.

**Включает:**
- ✅ AI Insights Card (рекомендации каждый день)
- ✅ Activity Feed (сгруппированная лента)
- ✅ Saved Searches Panel
- ✅ Advanced filters в Recent Assets
- ✅ Tab switcher в Recent Assets ("Недавние / Избранное / Одобренные")

**Backend:**
- Celery Task: `generate_daily_insights()` (daily @ 09:00 UTC)
- Endpoint: `/api/v4/user/daily-insights/`
- Endpoint: `/api/v4/activity-feed/`
- Endpoint: `/api/v4/user/saved-searches/`
- Optimization: Кэширование insights (Redis, TTL 24h)

**Frontend:**
- Components: `AIInsightsCard.vue`, `ActivityFeed.vue`, `SavedSearchesPanel.vue`
- Store: Extend `homeStore.ts` for activity filters

**QA:**
- Task verification: Celery task выполняется ежедневно и создаёт инсайты.
- Feed consistency: Активность загружается корректно, фильтры работают.

---

#### **ФАЗА 3 (Week 5-6): Role-based & Real-time**

**Цель:** Персонализация по ролям и live-updates.

**Включает:**
- ✅ Role-based config (разные KPI/actions для Brand Manager, Designer, etc.)
- ✅ WebSocket для real-time notifications
- ✅ Optimization: Lazy-loading панелей, infinite scroll в Activity Feed
- ✅ Mobile responsive overhaul

**Backend:**
- Endpoint: `/api/v4/homepage/config/` (role-aware)
- Django Channels: Consumer для WebSocket
- Миграции: `UserOrganizationProfile.role` (если нет)

**Frontend:**
- Dynamic config loading, conditional rendering
- WebSocket connection manager
- Mobile breakpoint adjustments

**QA:**
- Multi-role testing: Каждая роль видит свой интерфейс.
- Real-time: Notification приходит на клиент в реальном времени.
- Mobile: Все компоненты ладно укладываются на 375px (iPhone SE).

---

### 6.3 Временна́я шкала

```
Week 1-2: Phase 1 MVP
├─ Backend: Stats endpoints, Inbox API
├─ Frontend: Components, Store, Layout
└─ QA: Integration tests

Week 3-4: Phase 2 Enrichment
├─ Backend: Celery tasks, Activity feed
├─ Frontend: Insights, Activity components
└─ QA: Task verification, E2E

Week 5-6: Phase 3 Polish
├─ Backend: Config endpoint, WebSocket
├─ Frontend: Personalization, Real-time
└─ QA: Mobile, Multi-role, Performance

Week 7: Buffer & Deployment
├─ Performance optimization
├─ Browser compatibility
└─ Staging → Production
```

---

## 7. Технические требования

### 7.1 Backend Stack

| Компонент | Версия | Назначение |
|-----------|--------|-----------|
| Django | 4.2+ | Web framework |
| DRF (Django REST Framework) | 3.14+ | API |
| Celery | 5.3+ | Async tasks (daily insights) |
| Redis | 7.0+ | Cache, Message broker |
| PostgreSQL | 14+ | БД |
| Django Channels | 4.0+ | WebSocket (real-time) |
| django-cors-headers | 4.3+ | CORS для фронта |

### 7.2 Frontend Stack

| Компонент | Версия | Назначение |
|-----------|--------|-----------|
| Vue | 3.3+ | UI framework |
| Nuxt | 3.8+ | Meta-framework |
| Pinia | 2.1+ | State management |
| TailwindCSS | 3.3+ | Styling |
| Headless UI | 1.7+ | Accessible components |
| Axios / Fetch API | Latest | HTTP client |

### 7.3 Database Schema Changes (Minimal)

Новых таблиц не требуется. Используются существующие:
- `Document`, `DocumentVersion`, `DocumentFile`
- `User`, `Organization`
- `AssetEvent` (для Activity Feed)
- `Comment` (для My Inbox)
- `CabinetShare` (для Shared Collections)

**Опциональные добавления:**
- `UserOrganizationProfile.role` (если нет) — для role‑based config
- `DailyInsight` (model для хранения инсайтов, или Redis cache)

### 7.4 API Versioning

Все новые endpoints в `/api/v4/`:
```
GET /api/v4/documents/stats/
GET /api/v4/documents/ai-stats/
GET /api/v4/user/inbox/
GET /api/v4/user/inbox-stats/
GET /api/v4/user/inbox-counts/
GET /api/v4/user/daily-insights/
GET /api/v4/activity-feed/
GET /api/v4/documents/ (tab=recent)
GET /api/v4/user/saved-searches/
GET /api/v4/user/storage-info/
GET /api/v4/homepage/config/  (role-aware)
```

### 7.5 Производительность

| Метрика | Требование | Примечание |
|---------|-----------|-----------|
| **Page Load Time** | < 2s (First Contentful Paint) | Ленивая загрузка разделов |
| **API Response Time** | < 500ms per endpoint | Кэширование (Redis) |
| **Bundle Size** | < 300KB (main JS) | Code splitting, Tree-shaking |
| **Lighthouse Score** | ≥ 80 (Performance) | Optimization budgets |

**Optimization Strategies:**
- Redis cache на инсайты (TTL 24h, recompute daily)
- Pagination в Activity Feed (limit 20, infinite scroll)
- Lazy-load компоненты (React.lazy / defineAsyncComponent)
- Image optimization (WebP thumbnails via Converter)
- ServiceWorker для offline fallback

---

## 8. Метрики успеха

### 8.1 Продуктовые метрики

| Метрика | Baseline | Target | Как измерять |
|---------|----------|--------|--------------|
| **Daily Active Users (DAU)** | 45% logged-in users | 65% spend ≥5 min on home | Google Analytics |
| **Inbox Engagement** | <10% open inbox | >40% daily check | Event tracking |
| **Quick Action CTR** | N/A (новая фича) | >25% click rate | Mixpanel / Amplitude |
| **Insights Conversion** | N/A (новая фича) | >30% act on recommendations | Event tracking |
| **Recent Assets Usage** | <5% reopen recent | >20% click recent assets | Session replay |
| **Time to Task Completion** | Varies | -30% average (speed up workflow) | User testing |

### 8.2 Технические метрики

| Метрика | Требование | Инструмент |
|---------|-----------|-----------|
| **FCP (First Contentful Paint)** | < 1.5s | Lighthouse, WebPageTest |
| **LCP (Largest Contentful Paint)** | < 2.5s | Core Web Vitals |
| **API P95 Response Time** | < 800ms | DataDog / New Relic APM |
| **Error Rate (API)** | < 0.5% | Sentry |
| **Real-time Latency (WebSocket)** | < 200ms | Custom monitoring |
| **Mobile Responsiveness** | All breakpoints | Manual + Automated testing |

### 8.3 Feedback Loops

**Post-Launch (неделя 1-2):**
- User interviews (5-10 пользователей) о удобстве.
- Bug reports & fix time SLA < 24h.

**Post-Launch (неделя 3-4):**
- A/B тесты: текущая главная vs новая (50/50 split).
- NPS survey (Net Promoter Score).

**Ongoing:**
- Weekly reviews: DAU, engagement, error rates.
- Monthly deep-dives: Feature adoption, feature requests.

---

## Приложения

### Приложение A: Примеры API Responses

#### Get Homepage Config (Role-Aware)

```json
{
  "role": "content_manager",
  "kpi_metrics": [
    {
      "id": "total_documents",
      "label": "Всего документов",
      "value": 2,
      "subtext": "+0 за 7 дней",
      "trend": "neutral",
      "cta": {
        "label": "→ Обзор",
        "url": "/dam?created_at__gte=7d"
      }
    },
    {
      "id": "ai_analysis",
      "label": "Завершённых анализов",
      "progress": { "value": 1, "max": 2 },
      "subtext": "1 в очереди",
      "cta": {
        "label": "⚡ Запустить недостающие",
        "action": "open_bulk_ai_dialog"
      }
    },
    {
      "id": "inbox_count",
      "label": "Требуется действие",
      "value": 6,
      "breakdown": {
        "comments": 3,
        "approvals": 1,
        "collections": 2
      },
      "cta": {
        "label": "📬 Открыть",
        "action": "scroll_to_inbox"
      }
    }
  ],
  "quick_actions": [
    {
      "id": "run_ai_bulk",
      "label": "Запустить AI-анализ",
      "emoji": "🚀",
      "subtext": "для 3 активов без тегов",
      "action_type": "dialog",
      "action_endpoint": "/api/v4/ai-analysis/bulk-analyze/"
    },
    {
      "id": "find_duplicates",
      "label": "Найти дубликаты",
      "emoji": "🔍",
      "subtext": "сэкономить место",
      "action_type": "filter",
      "action_endpoint": "/dam?duplicates=true"
    }
  ],
  "show_activity_feed": true,
  "show_saved_searches": true,
  "recent_assets_tabs": ["recent", "favorites", "approved"]
}
```

#### Get User Inbox

```json
[
  {
    "id": "notif_001",
    "type": "comment",
    "actor": {
      "id": 1,
      "name": "Maria",
      "avatar_url": "https://...profile.jpg"
    },
    "target": {
      "type": "document",
      "id": "doc_456",
      "label": "photo_123.jpg"
    },
    "text": "Check the colors of the product shot",
    "timestamp": "2026-02-19T14:30:00Z",
    "is_read": false,
    "action_url": "/dam/assets/doc_456",
    "meta": {
      "highlight": "colors"
    }
  },
  {
    "id": "notif_002",
    "type": "approval_request",
    "actor": {
      "id": 2,
      "name": "PM User",
      "avatar_url": "https://...pm.jpg"
    },
    "target": {
      "type": "cabinet",
      "id": "cab_789",
      "label": "Q1 2026 Campaign Kit"
    },
    "text": "Waiting for your approval to publish",
    "timestamp": "2026-02-19T10:15:00Z",
    "is_read": false,
    "action_buttons": [
      { "label": "✓ Approve", "action": "approve", "endpoint": "/api/v4/approvals/123/approve/" },
      { "label": "✕ Reject", "action": "reject", "endpoint": "/api/v4/approvals/123/reject/" }
    ]
  }
]
```

### Приложение B: Компоненты (Vue 3 структура)

```
components/DAM/
├── HomePage/
│   ├── HomePage.vue
│   ├── KPIBar.vue
│   ├── MyInbox.vue
│   ├── RecentAssets.vue
│   ├── ActivityFeed.vue
│   ├── QuickActionsPanel.vue
│   ├── StoragePanel.vue
│   ├── SavedSearchesPanel.vue
│   └── AIInsightsCard.vue
├── shared/
│   ├── NotificationItem.vue
│   ├── AssetCard.vue
│   ├── ActivityGroupItem.vue
│   └── KPICard.vue
└── dialogs/
    ├── BulkAIAnalysisDialog.vue
    └── FindDuplicatesDialog.vue
```

### Приложение C: Celery Tasks

```python
# mayan/apps/homepage/tasks.py

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

@shared_task
def generate_daily_insights():
    """
    Generates AI-powered insights for all organizations.
    Runs daily at 09:00 UTC via celery-beat.
    """
    from mayan.apps.documents.models import Document
    from mayan.apps.organizations.models import Organization
    
    for org in Organization.objects.all():
        insights = []
        
        # Insight 1: Untagged documents in last 7 days
        untagged_count = Document.objects.filter(
            organization=org,
            ai_tags__isnull=True,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        if untagged_count > 0:
            insights.append({
                'type': 'auto_tag_missing',
                'count': untagged_count,
                'emoji': '🏷️',
                'cta_label': 'Generate Tags',
                'action_endpoint': '/api/v4/ai-analysis/bulk-analyze/',
                'priority': 'high' if untagged_count > 10 else 'medium'
            })
        
        # Insight 2: Possible duplicates
        # (pseudo-code, requires hash-based dedup logic)
        duplicate_groups = find_potential_duplicates(org)
        if duplicate_groups:
            insights.append({
                'type': 'duplicates_found',
                'count': len(duplicate_groups),
                'emoji': '🔄',
                'cta_label': 'Review Duplicates',
                'action_endpoint': '/api/v4/documents/duplicates/',
                'priority': 'medium'
            })
        
        # Insight 3: Unused archived documents
        unused_count = Document.objects.filter(
            organization=org,
            created_at__lt=timezone.now() - timedelta(days=180),
            download_count=0,
            is_archived=True
        ).count()
        
        if unused_count > 3:
            insights.append({
                'type': 'unused_archived',
                'count': unused_count,
                'emoji': '📦',
                'cta_label': 'Delete Old Files',
                'action_endpoint': '/dam?archived=true&days_old__gt=180',
                'priority': 'low'
            })
        
        # Store top 2 insights in cache (TTL 24h)
        cache_key = f'homepage_insights_{org.id}'
        sorted_insights = sorted(insights, key=lambda x: x.get('priority') == 'high', reverse=True)
        cache.set(cache_key, sorted_insights[:2], 86400)
```

---

## Заключение

Эта ТЗ превращает главную страницу DAM из **статического дашборда** в **динамическое рабочее пространство**, которое:

✅ **Персонализировано** по ролям и контексту пользователя.  
✅ **Actionable** — каждая метрика ведёт к действию.  
✅ **Intelligent** — AI рекомендации встроены в workflow.  
✅ **Collaborative** — командные события и уведомления в центре внимания.  
✅ **Real-time** — live-updates и notifications через WebSocket.  

**Результат:** Пользователи проводят на главной больше времени, быстрее находят нужное, легче сотрудничают и чувствуют ценность AI-функций.
