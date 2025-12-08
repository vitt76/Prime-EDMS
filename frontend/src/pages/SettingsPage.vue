<template>
  <div class="settings-page min-h-screen bg-neutral-50 dark:bg-neutral-50">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
      <h1 class="text-3xl font-bold text-neutral-900 dark:text-neutral-900 mb-8">
        Настройки
      </h1>

      <div class="space-y-6">
        <!-- Profile Settings -->
        <Card class="p-6">
          <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
            Профиль
          </h2>
          <div class="space-y-4">
            <div>
              <label
                for="first-name"
                class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2"
              >
                Имя
              </label>
              <Input
                id="first-name"
                v-model="profileForm.firstName"
                placeholder="Введите имя"
                class="w-full"
              />
            </div>
            <div>
              <label
                for="last-name"
                class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2"
              >
                Фамилия
              </label>
              <Input
                id="last-name"
                v-model="profileForm.lastName"
                placeholder="Введите фамилию"
                class="w-full"
              />
            </div>
            <div>
              <label
                for="email"
                class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2"
              >
                Email
              </label>
              <Input
                id="email"
                v-model="profileForm.email"
                type="email"
                placeholder="email@example.com"
                class="w-full"
                disabled
              />
              <p class="mt-1 text-xs text-neutral-600 dark:text-neutral-600">
                Email нельзя изменить
              </p>
            </div>
            <div class="flex justify-end">
              <Button
                variant="primary"
                @click="handleSaveProfile"
                :loading="isSavingProfile"
                type="button"
                aria-label="Сохранить изменения профиля"
              >
                Сохранить
              </Button>
            </div>
          </div>
        </Card>

        <!-- Theme Settings -->
        <Card class="p-6">
          <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
            Внешний вид
          </h2>
          <div class="space-y-4">
            <div>
              <label
                for="theme"
                class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2"
              >
                Тема оформления
              </label>
              <Select
                id="theme"
                v-model="theme"
                :options="themeOptions"
                class="w-full"
                @change="handleThemeChange"
              />
              <p class="mt-1 text-xs text-neutral-600 dark:text-neutral-600">
                Выберите светлую, темную тему или автоматический режим
              </p>
            </div>
          </div>
        </Card>

        <!-- Notification Settings -->
        <Card class="p-6">
          <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
            Уведомления
          </h2>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <label
                  for="email-notifications"
                  class="text-sm font-medium text-neutral-900 dark:text-neutral-900"
                >
                  Email уведомления
                </label>
                <p class="text-xs text-neutral-600 dark:text-neutral-600 mt-1">
                  Получать уведомления на email
                </p>
              </div>
              <input
                id="email-notifications"
                v-model="notificationSettings.email"
                type="checkbox"
                class="w-5 h-5 rounded border-neutral-300 text-primary-500 focus:ring-primary-500 min-w-[44px] min-h-[44px]"
                @change="handleNotificationChange"
                aria-label="Включить email уведомления"
              />
            </div>
            <div class="flex items-center justify-between">
              <div>
                <label
                  for="push-notifications"
                  class="text-sm font-medium text-neutral-900 dark:text-neutral-900"
                >
                  Push уведомления
                </label>
                <p class="text-xs text-neutral-600 dark:text-neutral-600 mt-1">
                  Получать push уведомления в браузере
                </p>
              </div>
              <input
                id="push-notifications"
                v-model="notificationSettings.push"
                type="checkbox"
                class="w-5 h-5 rounded border-neutral-300 text-primary-500 focus:ring-primary-500 min-w-[44px] min-h-[44px]"
                @change="handleNotificationChange"
                aria-label="Включить push уведомления"
              />
            </div>
            <div class="flex items-center justify-between">
              <div>
                <label
                  for="in-app-notifications"
                  class="text-sm font-medium text-neutral-900 dark:text-neutral-900"
                >
                  Внутренние уведомления
                </label>
                <p class="text-xs text-neutral-600 dark:text-neutral-600 mt-1">
                  Показывать уведомления в приложении
                </p>
              </div>
              <input
                id="in-app-notifications"
                v-model="notificationSettings.inApp"
                type="checkbox"
                class="w-5 h-5 rounded border-neutral-300 text-primary-500 focus:ring-primary-500 min-w-[44px] min-h-[44px]"
                @change="handleNotificationChange"
                aria-label="Включить внутренние уведомления"
              />
            </div>
          </div>
        </Card>

        <!-- Preferences -->
        <Card class="p-6">
          <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
            Предпочтения
          </h2>
          <div class="space-y-4">
            <div>
              <label
                for="language"
                class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2"
              >
                Язык интерфейса
              </label>
              <Select
                id="language"
                v-model="preferences.language"
                :options="languageOptions"
                class="w-full"
                @change="handlePreferencesChange"
              />
            </div>
            <div>
              <label
                for="timezone"
                class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2"
              >
                Часовой пояс
              </label>
              <Select
                id="timezone"
                v-model="preferences.timezone"
                :options="timezoneOptions"
                class="w-full"
                @change="handlePreferencesChange"
              />
            </div>
            <div>
              <label
                for="items-per-page"
                class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2"
              >
                Элементов на странице
              </label>
              <Select
                id="items-per-page"
                v-model.number="preferences.itemsPerPage"
                :options="itemsPerPageOptions"
                class="w-full"
                @change="handlePreferencesChange"
              />
            </div>
          </div>
        </Card>

        <!-- Security Settings -->
        <Card class="p-6">
          <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900 mb-4">
            Безопасность
          </h2>
          <div class="space-y-4">
            <div>
              <p class="text-sm text-neutral-600 dark:text-neutral-600 mb-4">
                Управление безопасностью аккаунта
              </p>
              <div class="space-y-2">
                <Button
                  variant="outline"
                  @click="handleChangePassword"
                  type="button"
                  aria-label="Изменить пароль"
                >
                  Изменить пароль
                </Button>
                <Button
                  variant="outline"
                  @click="handleManageApiKeys"
                  type="button"
                  aria-label="Управление API ключами"
                >
                  Управление API ключами
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
    <ChangePasswordModal
      v-if="showChangePassword"
      :isOpen="showChangePassword"
      @close="showChangePassword = false"
      @changed="showChangePassword = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import Card from '@/components/Common/Card.vue'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import ChangePasswordModal from '@/components/modals/ChangePasswordModal.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()

const isSavingProfile = ref(false)
const showChangePassword = ref(false)

// Profile form
const profileForm = ref({
  firstName: '',
  lastName: '',
  email: ''
})

// Theme
const theme = computed({
  get: () => uiStore.theme,
  set: (value) => uiStore.setTheme(value)
})

const themeOptions = [
  { value: 'light', label: 'Светлая' },
  { value: 'dark', label: 'Темная' },
  { value: 'auto', label: 'Автоматически' }
]

// Notification settings
const notificationSettings = ref({
  email: true,
  push: false,
  inApp: true
})

// Preferences
const preferences = ref({
  language: 'ru',
  timezone: 'Europe/Moscow',
  itemsPerPage: 50
})

const languageOptions = [
  { value: 'ru', label: 'Русский' },
  { value: 'en', label: 'English' }
]

const timezoneOptions = [
  { value: 'Europe/Moscow', label: 'Москва (UTC+3)' },
  { value: 'Europe/Kiev', label: 'Киев (UTC+2)' },
  { value: 'UTC', label: 'UTC (UTC+0)' }
]

const itemsPerPageOptions = [
  { value: 20, label: '20' },
  { value: 50, label: '50' },
  { value: 100, label: '100' }
]

function handleThemeChange() {
  // Theme is already updated via computed setter
  // Save to localStorage is handled by uiStore persistence
}

function handleNotificationChange() {
  // Save notification settings to localStorage
  localStorage.setItem('notification_settings', JSON.stringify(notificationSettings.value))
}

function handlePreferencesChange() {
  // Save preferences to localStorage
  localStorage.setItem('user_preferences', JSON.stringify(preferences.value))
}

async function handleSaveProfile() {
  isSavingProfile.value = true
  try {
    // TODO: Implement API call to update profile
    // await authService.updateProfile(profileForm.value)
    await new Promise((resolve) => setTimeout(resolve, 500)) // Simulate API call
    // Show success notification
    uiStore.addNotification({
      type: 'success',
      message: 'Профиль успешно обновлен'
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Ошибка при обновлении профиля'
    })
  } finally {
    isSavingProfile.value = false
  }
}

function handleChangePassword() {
  showChangePassword.value = true
}

function handleManageApiKeys() {
  // TODO: Navigate to API keys page
  uiStore.addNotification({
    type: 'info',
    message: 'Управление API ключами будет доступно в следующей версии'
  })
}

onMounted(() => {
  // Load user data
  if (authStore.user) {
    profileForm.value = {
      firstName: authStore.user.first_name || '',
      lastName: authStore.user.last_name || '',
      email: authStore.user.email || authStore.user.username || ''
    }
  }

  // Load saved preferences
  const savedPreferences = localStorage.getItem('user_preferences')
  if (savedPreferences) {
    try {
      preferences.value = { ...preferences.value, ...JSON.parse(savedPreferences) }
    } catch (e) {
      console.error('Failed to parse saved preferences:', e)
    }
  }

  // Load saved notification settings
  const savedNotifications = localStorage.getItem('notification_settings')
  if (savedNotifications) {
    try {
      notificationSettings.value = { ...notificationSettings.value, ...JSON.parse(savedNotifications) }
    } catch (e) {
      console.error('Failed to parse saved notification settings:', e)
    }
  }
})
</script>

<style scoped>
.settings-page {
  padding-top: calc(var(--header-height, 64px) + 1rem);
}
</style>
