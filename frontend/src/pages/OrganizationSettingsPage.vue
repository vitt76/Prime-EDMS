<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Настройки организации</h1>

    <!-- Loading -->
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
    </div>

    <!-- Tabs -->
    <div v-else>
      <nav class="flex space-x-1 mb-8 border-b border-gray-200">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px"
          :class="
            activeTab === tab.id
              ? 'border-indigo-600 text-indigo-700'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          "
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>

      <!-- ═══ General Tab ═══ -->
      <section v-if="activeTab === 'general'" class="space-y-6">
        <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <h2 class="text-lg font-semibold text-gray-900">Основная информация</h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
              <input
                v-model="form.name"
                type="text"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                v-model="form.email"
                type="email"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Отрасль</label>
              <select
                v-model="form.industry"
                class="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
              >
                <option value="media">Медиа и развлечения</option>
                <option value="marketing">Маркетинговое агентство</option>
                <option value="ecommerce">E-commerce</option>
                <option value="healthcare">Здравоохранение</option>
                <option value="legal">Юриспруденция</option>
                <option value="education">Образование</option>
                <option value="government">Государство</option>
                <option value="other">Другое</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Цвет бренда</label>
              <div class="flex items-center gap-3">
                <input
                  v-model="form.branding_color"
                  type="color"
                  class="w-10 h-10 rounded cursor-pointer border border-gray-200"
                />
                <span class="text-sm text-gray-500">{{ form.branding_color }}</span>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
            />
          </div>

          <div class="pt-2">
            <button
              type="button"
              class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg
                     hover:bg-indigo-700 transition-colors disabled:opacity-50"
              :disabled="isSaving"
              @click="saveGeneral"
            >
              {{ isSaving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </section>

      <!-- ═══ Members Tab ═══ -->
      <section v-if="activeTab === 'members'" class="space-y-6">
        <div class="bg-white rounded-xl border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">
              Участники ({{ members.length }})
            </h2>
          </div>

          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Пользователь</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Роль</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                  <th class="px-4 py-3" />
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="member in members" :key="member.id" class="hover:bg-gray-50">
                  <td class="px-4 py-3">
                    <div class="text-sm font-medium text-gray-900">
                      {{ member.user_detail.first_name }} {{ member.user_detail.last_name }}
                    </div>
                    <div class="text-xs text-gray-500">{{ member.user_detail.email }}</div>
                  </td>
                  <td class="px-4 py-3">
                    <span
                      class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                      :class="roleBadgeClass(member.role)"
                    >
                      {{ roleLabel(member.role) }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-500">
                    {{ formatDate(member.joined_at) }}
                  </td>
                  <td class="px-4 py-3 text-right">
                    <button
                      v-if="member.role !== 'owner' && orgStore.isOwner"
                      type="button"
                      class="text-red-600 hover:text-red-800 text-xs"
                      @click="removeMember(member)"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ═══ Quota Tab ═══ -->
      <section v-if="activeTab === 'quota'" class="space-y-6">
        <div class="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
          <h2 class="text-lg font-semibold text-gray-900">Использование ресурсов</h2>

          <!-- Storage -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700">Хранилище</span>
              <span class="text-sm text-gray-500">
                {{ orgDetail?.storage_used_gb ?? '—' }} / {{ orgDetail?.storage_limit_gb ?? '∞' }} ГБ
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div
                class="h-2.5 rounded-full transition-all"
                :class="storageBarClass"
                :style="{ width: storagePercent + '%' }"
              />
            </div>
          </div>

          <!-- Users -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700">Пользователи</span>
              <span class="text-sm text-gray-500">
                {{ orgDetail?.active_users_count ?? '—' }} / {{ orgDetail?.max_users ?? '—' }}
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div
                class="h-2.5 rounded-full bg-indigo-500 transition-all"
                :style="{ width: usersPercent + '%' }"
              />
            </div>
          </div>

          <!-- AI analyses -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700">AI-анализы (месяц)</span>
              <span class="text-sm text-gray-500">
                {{ orgDetail?.can_perform_ai_analysis ? 'Доступно' : 'Лимит достигнут' }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ Plan Tab ═══ -->
      <section v-if="activeTab === 'plan'" class="space-y-6">
        <div class="bg-white rounded-xl border border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Текущий план</h2>

          <div v-if="orgDetail?.subscription?.plan_detail" class="space-y-3">
            <div class="flex items-center gap-3">
              <span class="text-xl font-bold text-gray-900">
                {{ orgDetail.subscription.plan_detail.name }}
              </span>
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
              >
                {{ orgDetail.subscription.status }}
              </span>
            </div>
            <p class="text-sm text-gray-500">
              {{ orgDetail.subscription.plan_detail.description }}
            </p>
            <div class="text-lg font-semibold text-gray-900">
              {{ orgDetail.subscription.amount }}
              {{ orgDetail.subscription.currency }} / {{ orgDetail.subscription.billing_cycle === 'monthly' ? 'мес.' : 'год' }}
            </div>
          </div>

          <div v-else class="text-sm text-gray-500">
            Информация о плане недоступна.
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useOrganizationStore } from '@/stores/organizationStore'
import { organizationService } from '@/services/organizationService'
import type { OrganizationDetail, OrganizationMember, OrganizationRole } from '@/types/organization'

const orgStore = useOrganizationStore()

const tabs = [
  { id: 'general', label: 'Основное' },
  { id: 'members', label: 'Участники' },
  { id: 'quota', label: 'Квоты' },
  { id: 'plan', label: 'План' },
]
const activeTab = ref('general')

const isLoading = ref(true)
const isSaving = ref(false)
const orgDetail = ref<OrganizationDetail | null>(null)
const members = ref<OrganizationMember[]>([])

const form = ref({
  name: '',
  email: '',
  description: '',
  industry: 'other',
  branding_color: '#3B82F6',
})

// Quota computed values
const storagePercent = computed(() => {
  if (!orgDetail.value || !orgDetail.value.storage_limit_gb) return 0
  return Math.min(
    100,
    Math.round(
      (orgDetail.value.storage_used_gb / orgDetail.value.storage_limit_gb) * 100
    )
  )
})

const storageBarClass = computed(() => {
  if (storagePercent.value >= 90) return 'bg-red-500'
  if (storagePercent.value >= 70) return 'bg-yellow-500'
  return 'bg-indigo-500'
})

const usersPercent = computed(() => {
  if (!orgDetail.value || !orgDetail.value.max_users) return 0
  return Math.min(
    100,
    Math.round(
      (orgDetail.value.active_users_count / orgDetail.value.max_users) * 100
    )
  )
})

function roleLabel(role: OrganizationRole | string): string {
  const labels: Record<string, string> = {
    owner: 'Владелец',
    admin: 'Администратор',
    member: 'Участник',
    viewer: 'Наблюдатель',
  }
  return labels[role] ?? role
}

function roleBadgeClass(role: string): string {
  const map: Record<string, string> = {
    owner: 'bg-purple-100 text-purple-800',
    admin: 'bg-blue-100 text-blue-800',
    member: 'bg-gray-100 text-gray-800',
    viewer: 'bg-green-100 text-green-800',
  }
  return map[role] ?? 'bg-gray-100 text-gray-800'
}

function formatDate(iso: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

async function loadData() {
  isLoading.value = true
  try {
    const orgId = orgStore.currentOrganization?.id
    if (!orgId) return

    const [detail, membersList] = await Promise.all([
      organizationService.getOrganization(orgId),
      organizationService.getMembers(orgId),
    ])

    orgDetail.value = detail
    members.value = membersList

    // Populate form
    form.value = {
      name: detail.name,
      email: detail.email,
      description: detail.description || '',
      industry: detail.industry || 'other',
      branding_color: detail.branding_color || '#3B82F6',
    }
  } catch (err) {
    console.error('[OrgSettings] Failed to load data:', err)
  } finally {
    isLoading.value = false
  }
}

async function saveGeneral() {
  const orgId = orgStore.currentOrganization?.id
  if (!orgId) return
  isSaving.value = true
  try {
    const updated = await organizationService.updateOrganization(orgId, {
      name: form.value.name,
      email: form.value.email,
      description: form.value.description,
      industry: form.value.industry,
      branding_color: form.value.branding_color,
    } as any)
    orgDetail.value = updated
  } catch (err) {
    console.error('[OrgSettings] Failed to save:', err)
  } finally {
    isSaving.value = false
  }
}

async function removeMember(member: OrganizationMember) {
  const orgId = orgStore.currentOrganization?.id
  if (!orgId) return
  if (!confirm(`Удалить пользователя ${member.user_detail.username} из организации?`)) return
  try {
    await organizationService.removeMember(orgId, member.user_detail.id)
    members.value = members.value.filter((m) => m.id !== member.id)
  } catch (err) {
    console.error('[OrgSettings] Failed to remove member:', err)
  }
}

onMounted(loadData)
</script>
