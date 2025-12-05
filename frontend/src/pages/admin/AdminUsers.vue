<template>
  <div class="admin-users space-y-4 sm:space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Пользователи</h1>
        <p class="text-sm text-gray-600 mt-1">Управление пользователями и правами доступа</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
        @click="showInviteModal = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
        </svg>
        <span class="hidden sm:inline">Пригласить пользователя</span>
        <span class="sm:hidden">Пригласить</span>
      </button>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 overflow-x-auto">
      <nav class="flex gap-4 sm:gap-6 min-w-max">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          :class="[
            'pb-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap focus:outline-none',
            activeTab === tab.id
              ? 'border-violet-600 text-violet-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
          <span
            v-if="tab.count !== undefined"
            :class="[
              'ml-1.5 sm:ml-2 px-1.5 sm:px-2 py-0.5 text-xs rounded-full',
              activeTab === tab.id ? 'bg-violet-100 text-violet-600' : 'bg-gray-100 text-gray-600'
            ]"
          >
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Users Tab -->
    <div v-if="activeTab === 'users'" class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <!-- Toolbar -->
      <div class="px-4 sm:px-5 py-3 sm:py-4 border-b border-gray-100">
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <!-- Search -->
          <div class="relative flex-1">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск..."
              class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
            />
          </div>

          <!-- Filters -->
          <div class="flex items-center gap-2 sm:gap-3">
            <!-- Status Filter -->
            <select
              v-model="statusFilter"
              class="flex-1 sm:flex-none px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <option value="">Статус</option>
              <option value="active">Активные</option>
              <option value="invited">Приглашённые</option>
              <option value="suspended">Заблокированные</option>
            </select>

            <!-- Role Filter -->
            <select
              v-model="roleFilter"
              class="flex-1 sm:flex-none px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <option value="">Роль</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.label }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Desktop Table -->
      <div class="hidden lg:block overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Пользователь
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Роль
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                2FA
              </th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Последний вход
              </th>
              <th class="px-5 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-sm"
                    :style="{ backgroundColor: getAvatarColor(user.username) }"
                  >
                    {{ getInitials(user) }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">
                      {{ user.first_name }} {{ user.last_name }}
                    </p>
                    <p class="text-sm text-gray-500">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="role in user.roles"
                    :key="role.id"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-violet-100 text-violet-700"
                  >
                    {{ role.label }}
                  </span>
                  <span
                    v-if="user.is_superuser"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700"
                  >
                    Супер
                  </span>
                </div>
              </td>
              <td class="px-5 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
                    statusStyles[user.status]
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full',
                      user.status === 'active' ? 'bg-emerald-500' :
                      user.status === 'invited' ? 'bg-blue-500' :
                      user.status === 'suspended' ? 'bg-red-500' : 'bg-gray-400'
                    ]"
                  />
                  {{ statusLabels[user.status] }}
                </span>
              </td>
              <td class="px-5 py-4">
                <span
                  v-if="user.two_factor_enabled"
                  class="inline-flex items-center gap-1 text-sm text-emerald-600"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  Да
                </span>
                <span v-else class="text-sm text-gray-400">—</span>
              </td>
              <td class="px-5 py-4">
                <span class="text-sm text-gray-600">
                  {{ user.last_login ? formatDate(user.last_login) : 'Никогда' }}
                </span>
              </td>
              <td class="px-5 py-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    type="button"
                    class="p-2 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500"
                    title="Войти как пользователь"
                    @click="impersonateUser(user)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    type="button"
                    class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
                    title="Редактировать"
                    @click="editUser(user)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    type="button"
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
                    title="Удалить"
                    @click="deleteUser(user)"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Card View -->
      <div class="lg:hidden divide-y divide-gray-100">
        <div
          v-for="user in filteredUsers"
          :key="user.id"
          class="p-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-start gap-3">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-sm flex-shrink-0"
              :style="{ backgroundColor: getAvatarColor(user.username) }"
            >
              {{ getInitials(user) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ user.first_name }} {{ user.last_name }}
                  </p>
                  <p class="text-xs text-gray-500 truncate">{{ user.email }}</p>
                </div>
                <span
                  :class="[
                    'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium flex-shrink-0',
                    statusStyles[user.status]
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full',
                      user.status === 'active' ? 'bg-emerald-500' :
                      user.status === 'invited' ? 'bg-blue-500' :
                      user.status === 'suspended' ? 'bg-red-500' : 'bg-gray-400'
                    ]"
                  />
                  {{ statusLabels[user.status] }}
                </span>
              </div>
              <div class="flex flex-wrap items-center gap-2 mt-2">
                <span
                  v-for="role in user.roles"
                  :key="role.id"
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-violet-100 text-violet-700"
                >
                  {{ role.label }}
                </span>
                <span
                  v-if="user.two_factor_enabled"
                  class="inline-flex items-center gap-1 text-[10px] text-emerald-600"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  2FA
                </span>
                <span class="text-[10px] text-gray-400">
                  {{ user.last_login ? formatDate(user.last_login) : 'Не входил' }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-end gap-1 mt-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              class="p-2 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
              @click="impersonateUser(user)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
            <button
              type="button"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              @click="editUser(user)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              type="button"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              @click="deleteUser(user)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="px-5 py-12 text-center">
        <svg class="animate-spin mx-auto w-8 h-8 text-violet-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-4 text-sm text-gray-500">Загрузка пользователей...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="px-5 py-12 text-center">
        <svg class="mx-auto w-12 h-12 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="mt-4 text-sm text-red-500">{{ error }}</p>
        <button
          type="button"
          class="mt-4 px-4 py-2 bg-violet-600 text-white text-sm rounded-lg hover:bg-violet-700 transition-colors"
          @click="loadUsers(currentPage)"
        >
          Повторить
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredUsers.length === 0" class="px-5 py-12 text-center">
        <svg class="mx-auto w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p class="mt-4 text-sm text-gray-500">Пользователи не найдены</p>
      </div>

      <!-- Pagination -->
      <div v-if="!isLoading && filteredUsers.length > 0" class="px-5 py-4 border-t border-gray-100 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          Показано {{ filteredUsers.length }} из {{ adminStore.totalUsersCount }} пользователей
          <span v-if="currentPage > 1">(страница {{ currentPage }})</span>
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            :disabled="!hasPrevPage"
            :class="[
              'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors',
              hasPrevPage
                ? 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            ]"
            @click="goToPrevPage"
          >
            ← Назад
          </button>
          <span class="px-3 py-1.5 text-sm text-gray-600">{{ currentPage }}</span>
          <button
            type="button"
            :disabled="!hasNextPage"
            :class="[
              'px-3 py-1.5 text-sm font-medium rounded-lg transition-colors',
              hasNextPage
                ? 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            ]"
            @click="goToNextPage"
          >
            Вперёд →
          </button>
        </div>
      </div>
    </div>

    <!-- Roles Tab -->
    <div v-if="activeTab === 'roles'" class="bg-white rounded-xl border border-gray-200">
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="font-semibold text-gray-900">Матрица прав доступа</h2>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Создать роль
        </button>
      </div>

      <!-- Permission Matrix -->
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50">
                Право доступа
              </th>
              <th
                v-for="role in roles"
                :key="role.id"
                class="px-5 py-3 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider min-w-[120px]"
              >
                {{ role.label }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <template v-for="(perms, namespace) in groupedPermissions" :key="namespace">
              <!-- Namespace Header -->
              <tr class="bg-gray-50/50">
                <td
                  :colspan="roles.length + 1"
                  class="px-5 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  {{ namespace }}
                </td>
              </tr>
              <!-- Permission Rows -->
              <tr
                v-for="perm in perms"
                :key="perm.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-5 py-3 text-sm text-gray-700 sticky left-0 bg-white">
                  {{ perm.label }}
                </td>
                <td
                  v-for="role in roles"
                  :key="role.id"
                  class="px-5 py-3 text-center"
                >
                  <button
                    type="button"
                    :class="[
                      'w-5 h-5 rounded border-2 transition-colors',
                      hasPermission(role.id, perm.name)
                        ? 'bg-violet-600 border-violet-600'
                        : 'bg-white border-gray-300 hover:border-gray-400'
                    ]"
                    @click="togglePermission(role.id, perm.name)"
                  >
                    <svg
                      v-if="hasPermission(role.id, perm.name)"
                      class="w-full h-full text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Invite Modal -->
    <Teleport to="body">
      <div
        v-if="showInviteModal"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="showInviteModal = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Пригласить пользователя</h2>
          
          <form @submit.prevent="inviteUser" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Имя пользователя *</label>
              <input
                v-model="inviteForm.username"
                type="text"
                required
                placeholder="username"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input
                v-model="inviteForm.email"
                type="email"
                required
                placeholder="user@company.ru"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Пароль *</label>
              <input
                v-model="inviteForm.password"
                type="password"
                required
                placeholder="••••••••"
                minlength="8"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
              <p class="mt-1 text-xs text-gray-500">Минимум 8 символов</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Группа (роль)</label>
              <select
                v-model="inviteForm.roleId"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              >
                <option value="">Без группы</option>
                <option v-for="role in roles" :key="role.id" :value="role.id">
                  {{ role.label }}
                </option>
              </select>
            </div>

            <div class="flex items-center gap-2">
              <input
                v-model="inviteForm.sendEmail"
                type="checkbox"
                id="send-email"
                class="w-4 h-4 text-violet-600 border-gray-300 rounded focus:ring-violet-500"
              />
              <label for="send-email" class="text-sm text-gray-600">
                Отправить приглашение на email (не реализовано)
              </label>
            </div>

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                @click="showInviteModal = false"
              >
                Отмена
              </button>
              <button
                type="submit"
                :disabled="isLoading"
                class="flex-1 px-4 py-2.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors disabled:opacity-50"
              >
                {{ isLoading ? 'Создание...' : 'Создать' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit User Modal -->
    <Teleport to="body">
      <div
        v-if="showEditModal && editingUser"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="closeEditModal" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-hidden flex flex-col">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">Редактировать пользователя</h2>
            <button
              type="button"
              class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              @click="closeEditModal"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="saveUser" class="flex-1 overflow-y-auto p-6 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                <input
                  v-model="editForm.first_name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
                <input
                  v-model="editForm.last_name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                v-model="editForm.email"
                type="email"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Имя пользователя</label>
              <input
                v-model="editForm.username"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Роли</label>
              <div class="space-y-2">
                <label
                  v-for="role in roles"
                  :key="role.id"
                  class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :checked="editForm.roleIds.includes(role.id)"
                    @change="toggleRole(role.id)"
                    class="w-4 h-4 text-violet-600 border-gray-300 rounded focus:ring-violet-500"
                  />
                  <span class="text-sm text-gray-700">{{ role.label }}</span>
                </label>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Статус</label>
              <select
                v-model="editForm.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              >
                <option value="active">Активен</option>
                <option value="suspended">Заблокирован</option>
                <option value="inactive">Неактивен</option>
              </select>
            </div>

            <div class="flex items-center gap-4 pt-2">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="editForm.is_staff"
                  type="checkbox"
                  class="w-4 h-4 text-violet-600 border-gray-300 rounded focus:ring-violet-500"
                />
                <span class="text-sm text-gray-700">Сотрудник</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  v-model="editForm.is_superuser"
                  type="checkbox"
                  class="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
                />
                <span class="text-sm text-gray-700">Суперпользователь</span>
              </label>
            </div>
          </form>

          <div class="px-6 py-4 border-t border-gray-100 flex gap-3">
            <button
              type="button"
              class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              @click="closeEditModal"
            >
              Отмена
            </button>
            <button
              type="button"
              class="flex-1 px-4 py-2.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors"
              @click="saveUser"
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div
        v-if="showDeleteModal && deletingUser"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="showDeleteModal = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-gray-900">Удалить пользователя?</h2>
              <p class="text-sm text-gray-500">Это действие нельзя отменить</p>
            </div>
          </div>
          
          <div class="p-4 bg-gray-50 rounded-lg mb-6">
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium"
                :style="{ backgroundColor: getAvatarColor(deletingUser.username) }"
              >
                {{ getInitials(deletingUser) }}
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ deletingUser.first_name }} {{ deletingUser.last_name }}
                </p>
                <p class="text-sm text-gray-500">{{ deletingUser.email }}</p>
              </div>
            </div>
          </div>

          <div class="flex gap-3">
            <button
              type="button"
              class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              @click="showDeleteModal = false"
            >
              Отмена
            </button>
            <button
              type="button"
              class="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
              @click="confirmDeleteUser"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Toast Notification -->
    <Teleport to="body">
      <Transition name="toast">
        <div
          v-if="toast.show"
          :class="[
            'fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg',
            toast.type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
          ]"
        >
          <svg v-if="toast.type === 'success'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import type { AdminUser, AdminRole, StoredPermission } from '@/types/admin'
import { useAdminStore } from '@/stores/adminStore'
import { adminService } from '@/services/adminService'
import { debounce } from '@/utils/debounce'

// ═══════════════════════════════════════════════════════════════════════════════
// Store & State
// ═══════════════════════════════════════════════════════════════════════════════
const adminStore = useAdminStore()

const activeTab = ref<'users' | 'roles'>('users')
const searchQuery = ref('')
const statusFilter = ref('')
const roleFilter = ref('')
const showInviteModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref<AdminUser | null>(null)
const deletingUser = ref<AdminUser | null>(null)

// Pagination state
const currentPage = ref(1)
const pageSize = ref(20)
const hasNextPage = ref(false)
const hasPrevPage = ref(false)

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

const inviteForm = ref({
  email: '',
  username: '',
  password: '',
  roleId: '',
  sendEmail: true
})

const editForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  status: 'active' as string,
  roleIds: [] as number[],
  is_staff: false,
  is_superuser: false,
  is_active: true
})

const tabs = computed(() => [
  { id: 'users' as const, label: 'Пользователи', count: adminStore.totalUsersCount },
  { id: 'roles' as const, label: 'Роли и права' }
])

const statusStyles: Record<string, string> = {
  active: 'bg-emerald-50 text-emerald-700',
  invited: 'bg-blue-50 text-blue-700',
  suspended: 'bg-red-50 text-red-700',
  inactive: 'bg-gray-100 text-gray-600'
}

const statusLabels: Record<string, string> = {
  active: 'Активен',
  invited: 'Приглашён',
  suspended: 'Заблокирован',
  inactive: 'Неактивен'
}

// Groups (roles in Mayan context)
const roles = ref<AdminRole[]>([])
const isLoadingGroups = ref(false)

const permissions = ref<StoredPermission[]>([
  { id: 1, namespace: 'documents', name: 'documents.view', label: 'Просмотр документов' },
  { id: 2, namespace: 'documents', name: 'documents.create', label: 'Создание документов' },
  { id: 3, namespace: 'documents', name: 'documents.edit', label: 'Редактирование документов' },
  { id: 4, namespace: 'documents', name: 'documents.delete', label: 'Удаление документов' },
  { id: 5, namespace: 'metadata', name: 'metadata.view', label: 'Просмотр метаданных' },
  { id: 6, namespace: 'metadata', name: 'metadata.edit', label: 'Редактирование метаданных' },
  { id: 7, namespace: 'users', name: 'users.view', label: 'Просмотр пользователей' },
  { id: 8, namespace: 'users', name: 'users.manage', label: 'Управление пользователями' },
  { id: 9, namespace: 'sharing', name: 'sharing.create', label: 'Создание ссылок' },
  { id: 10, namespace: 'sharing', name: 'sharing.manage', label: 'Управление публикациями' }
])

const permissionMatrix = ref<Record<number, Set<string>>>({
  1: new Set(['documents.view', 'documents.create', 'documents.edit', 'documents.delete', 'metadata.view', 'metadata.edit', 'users.view', 'users.manage', 'sharing.create', 'sharing.manage']),
  2: new Set(['documents.view', 'documents.create', 'documents.edit', 'metadata.view', 'metadata.edit', 'sharing.create']),
  3: new Set(['documents.view', 'metadata.view']),
  4: new Set(['documents.view', 'documents.create', 'metadata.view'])
})

// Use store users instead of local mock
const users = computed(() => adminStore.users as AdminUser[])

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════

// Use store data directly - filtering is done server-side
const filteredUsers = computed(() => {
  let result = users.value || []
  
  // Client-side role filter (if needed)
  if (roleFilter.value) {
    result = result.filter(user => 
      user.roles?.some(r => r.id === Number(roleFilter.value))
    )
  }
  
  return result
})

const isLoading = computed(() => adminStore.isLoading)
const error = computed(() => adminStore.error)

const groupedPermissions = computed(() => {
  const groups: Record<string, StoredPermission[]> = {}
  permissions.value.forEach(perm => {
    if (!groups[perm.namespace]) {
      groups[perm.namespace] = []
    }
    groups[perm.namespace].push(perm)
  })
  return groups
})

// ═══════════════════════════════════════════════════════════════════════════════
// Data Fetching
// ═══════════════════════════════════════════════════════════════════════════════

async function loadUsers(page = 1) {
  currentPage.value = page
  
  try {
    await adminStore.fetchUsers({
      page,
      page_size: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value || undefined
    })
    
    // Update pagination state
    hasNextPage.value = adminStore.totalUsersCount > page * pageSize.value
    hasPrevPage.value = page > 1
  } catch (err) {
    console.error('[AdminUsers] Failed to load users:', err)
    showToast('Ошибка загрузки пользователей', 'error')
  }
}

async function loadGroups() {
  isLoadingGroups.value = true
  try {
    const response = await adminService.getGroups({ page_size: 100 })
    roles.value = response.results.map(g => ({
      id: g.id,
      label: g.name,
      permissions: [],
      groups: []
    }))
  } catch (err) {
    console.error('[AdminUsers] Failed to load groups:', err)
  } finally {
    isLoadingGroups.value = false
  }
}

// Debounced search
const debouncedSearch = debounce(() => {
  loadUsers(1)
}, 300)

// Watch for search query changes
watch(searchQuery, () => {
  debouncedSearch()
})

// Watch for filter changes
watch(statusFilter, () => {
  loadUsers(1)
})

// Initial load
onMounted(async () => {
  await Promise.all([
    loadUsers(1),
    loadGroups()
  ])
})

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function getAvatarColor(username: string): string {
  const colors = ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#EC4899']
  const index = username.charCodeAt(0) % colors.length
  return colors[index]
}

function getInitials(user: AdminUser): string {
  if (user.first_name && user.last_name) {
    return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
  }
  return user.username[0].toUpperCase()
}

function formatDate(iso: string): string {
  const date = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Сегодня'
  if (diffDays === 1) return 'Вчера'
  if (diffDays < 7) return `${diffDays} дн. назад`
  
  return date.toLocaleDateString('ru-RU')
}

function hasPermission(roleId: number, permName: string): boolean {
  return permissionMatrix.value[roleId]?.has(permName) ?? false
}

function togglePermission(roleId: number, permName: string): void {
  if (!permissionMatrix.value[roleId]) {
    permissionMatrix.value[roleId] = new Set()
  }
  
  if (permissionMatrix.value[roleId].has(permName)) {
    permissionMatrix.value[roleId].delete(permName)
  } else {
    permissionMatrix.value[roleId].add(permName)
  }
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

async function inviteUser(): Promise<void> {
  try {
    // Create user via API
    const userData = {
      username: inviteForm.value.username || inviteForm.value.email.split('@')[0],
      email: inviteForm.value.email,
      password: inviteForm.value.password || generateTempPassword(),
      first_name: '',
      last_name: '',
      is_active: true,
      groups_pk_list: inviteForm.value.roleId ? [Number(inviteForm.value.roleId)] : []
    }
    
    await adminStore.createUser(userData)
    
    showInviteModal.value = false
    inviteForm.value = { email: '', username: '', password: '', roleId: '', sendEmail: true }
    showToast('Пользователь создан: ' + userData.email)
    
    // Reload users list
    await loadUsers(currentPage.value)
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Ошибка создания пользователя'
    showToast(errorMsg, 'error')
  }
}

function generateTempPassword(): string {
  return 'Temp' + Math.random().toString(36).slice(2, 10) + '!'
}

function editUser(user: AdminUser): void {
  editingUser.value = user
  editForm.value = {
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    username: user.username,
    status: user.status,
    roleIds: user.roles?.map(r => r.id) || [],
    is_staff: user.is_staff,
    is_superuser: user.is_superuser,
    is_active: user.is_active
  }
  showEditModal.value = true
}

function closeEditModal(): void {
  showEditModal.value = false
  editingUser.value = null
}

function toggleRole(roleId: number): void {
  const idx = editForm.value.roleIds.indexOf(roleId)
  if (idx > -1) {
    editForm.value.roleIds.splice(idx, 1)
  } else {
    editForm.value.roleIds.push(roleId)
  }
}

async function saveUser(): Promise<void> {
  if (!editingUser.value) return
  
  try {
    // Determine is_active based on status
    const is_active = editForm.value.status === 'active'
    
    await adminStore.updateUser(editingUser.value.id, {
      first_name: editForm.value.first_name,
      last_name: editForm.value.last_name,
      email: editForm.value.email,
      username: editForm.value.username,
      is_active,
      is_staff: editForm.value.is_staff,
      is_superuser: editForm.value.is_superuser,
      groups_pk_list: editForm.value.roleIds
    })
    
    closeEditModal()
    showToast('Пользователь успешно обновлён')
    
    // Reload users list
    await loadUsers(currentPage.value)
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Ошибка обновления пользователя'
    showToast(errorMsg, 'error')
  }
}

function deleteUser(user: AdminUser): void {
  deletingUser.value = user
  showDeleteModal.value = true
}

async function confirmDeleteUser(): Promise<void> {
  if (!deletingUser.value) return
  
  try {
    await adminStore.deleteUser(deletingUser.value.id)
    
    showDeleteModal.value = false
    deletingUser.value = null
    showToast('Пользователь удалён')
    
    // Reload users list
    await loadUsers(currentPage.value)
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Ошибка удаления пользователя'
    showToast(errorMsg, 'error')
  }
}

function impersonateUser(user: AdminUser): void {
  showToast(`Вход от имени ${user.first_name} ${user.last_name}... (не реализовано)`)
}

// Pagination handlers
function goToNextPage() {
  if (hasNextPage.value) {
    loadUsers(currentPage.value + 1)
  }
}

function goToPrevPage() {
  if (hasPrevPage.value) {
    loadUsers(currentPage.value - 1)
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>

