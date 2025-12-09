# 👨‍💼 Admin Guide
## Руководство администратора DAM Frontend

**Версия:** 1.0  
**Дата:** 2025-01-27  
**Для:** System Administrators

---

## 📑 Содержание

1. [User Management](#user-management)
2. [System Configuration](#system-configuration)
3. [Metadata Schemas](#metadata-schemas)
4. [Workflows](#workflows)
5. [Reports & Analytics](#reports--analytics)
6. [Troubleshooting](#troubleshooting)

---

## 👥 User Management

### Создание пользователя

1. Перейдите в **Admin** → **Users**
2. Кликните "+ Create User"
3. Заполните форму:
   - Username (обязательно)
   - Email (обязательно)
   - First Name
   - Last Name
   - Password (или отправить reset link)
4. Назначьте роли и права
5. Сохраните

### Управление правами

**Роли:**
- **Viewer** - Только просмотр
- **Editor** - Просмотр и редактирование
- **Admin** - Полный доступ
- **Custom** - Кастомные роли

**Права:**
- `documents.document_view` - Просмотр документов
- `documents.document_edit` - Редактирование
- `documents.document_delete` - Удаление
- `documents.document_upload` - Загрузка
- И другие...

### Деактивация пользователя

1. Найдите пользователя
2. Откройте детали
3. Измените "Active" на "Inactive"
4. Пользователь не сможет войти

---

## ⚙️ System Configuration

### Общие настройки

**Settings → System:**
- Site name
- Default language
- Default timezone
- Max file size
- Allowed file types

### Storage Configuration

**Settings → Storage:**
- Storage backend (Local/S3/Yandex Disk)
- Storage path
- Quota limits
- Cleanup policies

### API Configuration

**Settings → API:**
- API version
- Rate limits
- CORS settings
- Authentication methods

---

## 📋 Metadata Schemas

### Создание metadata schema

1. Перейдите в **Admin** → **Metadata Schemas**
2. Кликните "+ Create Schema"
3. Настройте:
   - Schema name
   - Description
   - Applies to (file types)
4. Добавьте поля:
   - Field name
   - Field type (Text, Number, Date, Select, etc.)
   - Required/Optional
   - Default value
   - Validation rules
5. Сохраните

### Применение schema

1. Выберите schema
2. Выберите коллекции для применения
3. Schema будет применяться к новым активам в этих коллекциях

---

## 🔄 Workflows

### Создание workflow

1. Перейдите в **Admin** → **Workflows**
2. Кликните "+ Create Workflow"
3. Создайте states:
   - Draft
   - In Review
   - Approved
   - Rejected
4. Настройте transitions:
   - Draft → In Review
   - In Review → Approved
   - In Review → Rejected
5. Настройте permissions для каждого state
6. Сохраните

### Применение workflow

1. Выберите workflow
2. Выберите коллекции
3. Workflow будет применяться к активам в этих коллекциях

---

## 📊 Reports & Analytics

### System Reports

**Admin → Reports:**
- User activity
- Storage usage
- Upload statistics
- Search statistics
- Error logs

### Export Reports

1. Выберите отчет
2. Настройте параметры (даты, фильтры)
3. Кликните "Export"
4. Выберите формат (CSV, PDF, Excel)

---

## 🔧 Troubleshooting

### Common Admin Issues

**Issue: User cannot login**
- Проверьте, что пользователь активен
- Проверьте права доступа
- Проверьте, не заблокирован ли аккаунт

**Issue: Storage quota exceeded**
- Проверьте использование хранилища
- Увеличьте квоту или очистите старые файлы
- Настройте автоматическую очистку

**Issue: Workflow not working**
- Проверьте, что workflow применен к коллекции
- Проверьте permissions для transitions
- Проверьте, что пользователь имеет права

---

## 🔐 Security Best Practices

1. **Regular audits:**
   - Проверяйте права пользователей
   - Проверяйте активность
   - Проверяйте логи

2. **Password policy:**
   - Strong passwords required
   - Regular password changes
   - 2FA для администраторов

3. **Access control:**
   - Least privilege principle
   - Regular review of permissions
   - Audit logging enabled

---

**Документ создан:** 2025-01-27  
**Версия:** 1.0  
**Статус:** ✅ Ready
















