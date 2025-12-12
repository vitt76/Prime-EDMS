// @ts-nocheck
<template>
  <div class="admin-workflows space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Рабочие процессы</h1>
        <p class="text-sm text-gray-500 mt-1">Автоматизация обработки документов</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors"
        @click="showCreateModal = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        Создать процесс
      </button>
    </div>

    <!-- Workflows Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div
        v-for="workflow in workflows"
        :key="workflow.id"
        class="bg-white rounded-xl border border-gray-200 overflow-hidden hover:border-violet-300 hover:shadow-lg transition-all cursor-pointer"
        @click="selectWorkflow(workflow)"
      >
        <!-- Header -->
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div
              :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center',
                workflow.auto_launch ? 'bg-emerald-100' : 'bg-gray-100'
              ]"
            >
              <svg
                :class="[
                  'w-5 h-5',
                  workflow.auto_launch ? 'text-emerald-600' : 'text-gray-500'
                ]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ workflow.label }}</h3>
              <p class="text-xs text-gray-500">{{ workflow.internal_name }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-if="workflow.auto_launch"
              class="px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 rounded-lg"
            >
              Автозапуск
            </span>
            <span class="text-sm text-gray-500">
              {{ workflow.instances_count }} активных
            </span>
          </div>
        </div>

        <!-- Flow Visualization -->
        <div class="px-5 py-4">
          <div class="flex items-center justify-between overflow-x-auto pb-2">
            <template v-for="(state, index) in workflow.states" :key="state.id">
              <!-- State Node -->
              <div class="flex flex-col items-center min-w-[100px]">
                <div
                  :class="[
                    'w-12 h-12 rounded-xl flex items-center justify-center border-2',
                    state.initial
                      ? 'bg-blue-50 border-blue-300'
                      : state.completion
                      ? 'bg-emerald-50 border-emerald-300'
                      : 'bg-gray-50 border-gray-200'
                  ]"
                >
                  <svg
                    v-if="state.initial"
                    class="w-5 h-5 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg
                    v-else-if="state.completion"
                    class="w-5 h-5 text-emerald-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span v-else class="text-sm font-semibold text-gray-500">{{ index }}</span>
                </div>
                <p class="mt-2 text-xs font-medium text-gray-700 text-center">{{ state.label }}</p>
                <p v-if="state.actions.length" class="text-[10px] text-gray-400">
                  {{ state.actions.length }} действий
                </p>
              </div>

              <!-- Arrow -->
              <div
                v-if="index < workflow.states.length - 1"
                class="flex-shrink-0 px-2"
              >
                <svg class="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </template>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
          <div class="flex items-center gap-4 text-xs text-gray-500">
            <span>{{ workflow.states.length }} состояний</span>
            <span>{{ workflow.transitions.length }} переходов</span>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-for="docType in workflow.document_types.slice(0, 2)"
              :key="docType.id"
              class="px-2 py-0.5 text-[10px] font-medium bg-gray-200 text-gray-600 rounded"
            >
              {{ docType.label }}
            </span>
            <span
              v-if="workflow.document_types.length > 2"
              class="text-xs text-gray-400"
            >
              +{{ workflow.document_types.length - 2 }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="workflows.length === 0" class="bg-white rounded-xl border border-gray-200 px-5 py-16 text-center">
      <svg class="mx-auto w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      <h3 class="mt-4 text-lg font-semibold text-gray-900">Нет рабочих процессов</h3>
      <p class="mt-2 text-sm text-gray-500 max-w-sm mx-auto">
        Создайте первый рабочий процесс для автоматизации обработки документов
      </p>
      <button
        type="button"
        class="mt-6 inline-flex items-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-medium text-sm rounded-lg transition-colors"
        @click="createWorkflow"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        Создать процесс
      </button>
    </div>

    <!-- Workflow Detail Modal with Drag-Drop Editor -->
    <Teleport to="body">
      <div
        v-if="selectedWorkflow"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="selectedWorkflow = null" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-5xl mx-4 max-h-[90vh] overflow-hidden flex flex-col">
          <!-- Header -->
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-gray-900">{{ selectedWorkflow.label }}</h2>
              <p class="text-sm text-gray-500">{{ selectedWorkflow.internal_name }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button
                type="button"
                :class="[
                  'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                  isEditing ? 'bg-emerald-600 text-white hover:bg-emerald-700' : 'text-violet-600 hover:bg-violet-50'
                ]"
                @click="isEditing ? saveWorkflowChanges() : (isEditing = true)"
              >
                {{ isEditing ? 'Сохранить' : 'Редактировать' }}
              </button>
              <button
                v-if="isEditing"
                type="button"
                class="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                @click="isEditing = false"
              >
                Отмена
              </button>
              <button
                type="button"
                class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                @click="selectedWorkflow = null; isEditing = false"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Content -->
          <div class="flex-1 overflow-y-auto">
            <!-- Drag-Drop Visual Editor -->
            <div class="p-6 bg-gray-50 border-b border-gray-200">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-sm font-semibold text-gray-900">Визуальный редактор</h3>
                <div v-if="isEditing" class="flex items-center gap-2">
                  <span class="text-xs text-gray-500">Перетащите для изменения порядка</span>
                  <button
                    type="button"
                    class="px-3 py-1.5 text-xs font-medium text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
                    @click="addState"
                  >
                    + Добавить состояние
                  </button>
                </div>
              </div>
              
              <!-- Workflow Canvas -->
              <div 
                class="relative min-h-[200px] bg-white rounded-xl border-2 border-dashed border-gray-300 p-6 overflow-x-auto"
                :class="{ 'border-violet-400': isEditing }"
              >
                <div class="flex items-center gap-4">
                  <template v-for="(state, index) in selectedWorkflow.states" :key="state.id">
                    <!-- State Node -->
                    <div
                      :class="[
                        'relative group cursor-pointer transition-all',
                        isEditing ? 'cursor-move' : ''
                      ]"
                      :draggable="isEditing"
                      @dragstart="onDragStart($event, index)"
                      @dragover.prevent="onDragOver($event, index)"
                      @drop="onDrop($event, index)"
                      @dragend="onDragEnd"
                    >
                      <div
                        :class="[
                          'w-32 h-32 rounded-2xl flex flex-col items-center justify-center border-2 p-3 transition-all',
                          state.initial
                            ? 'bg-blue-50 border-blue-300 hover:border-blue-400'
                            : state.completion
                            ? 'bg-emerald-50 border-emerald-300 hover:border-emerald-400'
                            : 'bg-white border-gray-200 hover:border-violet-300',
                          dragOverIndex === index ? 'ring-2 ring-violet-500 ring-offset-2' : '',
                          isEditing ? 'hover:shadow-lg' : ''
                        ]"
                        @click="editState(state)"
                      >
                        <!-- Type Icon -->
                        <div
                          :class="[
                            'w-8 h-8 rounded-full flex items-center justify-center mb-2',
                            state.initial ? 'bg-blue-100' : state.completion ? 'bg-emerald-100' : 'bg-gray-100'
                          ]"
                        >
                          <svg
                            :class="[
                              'w-4 h-4',
                              state.initial ? 'text-blue-600' : state.completion ? 'text-emerald-600' : 'text-gray-500'
                            ]"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path v-if="state.initial" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path v-else-if="state.completion" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                        </div>
                        <span class="text-xs font-semibold text-gray-700 text-center line-clamp-2">{{ state.label }}</span>
                        <span class="text-[10px] text-gray-400 mt-1">{{ state.actions.length }} действий</span>
                        
                        <!-- Delete button on hover (edit mode) -->
                        <button
                          v-if="isEditing && !state.initial && !state.completion"
                          type="button"
                          class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center shadow-lg"
                          @click.stop="removeState(state.id)"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>

                    <!-- Arrow -->
                    <div
                      v-if="index < selectedWorkflow.states.length - 1"
                      class="flex flex-col items-center"
                    >
                      <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                      <span class="text-[10px] text-gray-400 mt-1">
                        {{ getTransitionLabel(state.id, selectedWorkflow.states[index + 1]?.id) }}
                      </span>
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <!-- States & Actions Panel -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
              <!-- States List -->
              <div>
                <h3 class="text-sm font-semibold text-gray-900 mb-4">Состояния</h3>
                <div class="space-y-3">
                  <div
                    v-for="state in selectedWorkflow.states"
                    :key="state.id"
                    class="p-4 bg-gray-50 rounded-xl border border-gray-200 hover:border-violet-300 transition-colors cursor-pointer"
                    @click="editState(state)"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <div class="flex items-center gap-2">
                        <span class="font-medium text-gray-900">{{ state.label }}</span>
                        <span
                          v-if="state.initial"
                          class="px-2 py-0.5 text-[10px] font-medium bg-blue-100 text-blue-700 rounded"
                        >
                          Начальное
                        </span>
                        <span
                          v-if="state.completion"
                          class="px-2 py-0.5 text-[10px] font-medium bg-emerald-100 text-emerald-700 rounded"
                        >
                          Конечное
                        </span>
                      </div>
                      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                    <div v-if="state.actions.length" class="mt-3 space-y-1">
                      <div
                        v-for="action in state.actions"
                        :key="action.id"
                        class="flex items-center gap-2 text-xs text-gray-600"
                      >
                        <span
                          :class="[
                            'px-1.5 py-0.5 font-medium rounded',
                            action.when === 'on_entry' ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'
                          ]"
                        >
                          {{ action.when === 'on_entry' ? '→' : '←' }}
                        </span>
                        <span>{{ action.label }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Transitions -->
              <div>
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-sm font-semibold text-gray-900">Переходы</h3>
                  <button
                    v-if="isEditing"
                    type="button"
                    class="px-3 py-1.5 text-xs font-medium text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
                    @click="addTransition"
                  >
                    + Добавить
                  </button>
                </div>
                <div class="space-y-3">
                  <div
                    v-for="transition in selectedWorkflow.transitions"
                    :key="transition.id"
                    class="p-4 bg-gray-50 rounded-xl border border-gray-200 flex items-center justify-between hover:border-violet-300 transition-colors"
                  >
                    <div class="flex items-center gap-3">
                      <span class="px-2 py-1 text-xs font-medium bg-white border border-gray-200 rounded text-gray-700">
                        {{ getStateName(transition.origin_state_id) }}
                      </span>
                      <svg class="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                      <span class="px-2 py-1 text-xs font-medium bg-white border border-gray-200 rounded text-gray-700">
                        {{ getStateName(transition.destination_state_id) }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs text-gray-500">{{ transition.label }}</span>
                      <button
                        v-if="isEditing"
                        type="button"
                        class="p-1 text-gray-400 hover:text-red-500 transition-colors"
                        @click="removeTransition(transition.id)"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Create Workflow Modal -->
    <Teleport to="body">
      <div
        v-if="showCreateModal"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="showCreateModal = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Создать рабочий процесс</h2>
          
          <form @submit.prevent="createNewWorkflow" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
              <input
                v-model="newWorkflowForm.label"
                type="text"
                required
                placeholder="Например: Согласование документов"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Внутреннее имя</label>
              <input
                v-model="newWorkflowForm.internal_name"
                type="text"
                required
                placeholder="document_approval"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 font-mono"
              />
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model="newWorkflowForm.auto_launch"
                type="checkbox"
                id="auto-launch"
                class="w-4 h-4 text-violet-600 border-gray-300 rounded"
              />
              <label for="auto-launch" class="text-sm text-gray-700">Автозапуск для новых документов</label>
            </div>

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                @click="showCreateModal = false"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700"
              >
                Создать
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Edit State Modal -->
    <Teleport to="body">
      <div
        v-if="editingState"
        class="fixed inset-0 z-[60] flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="editingState = null" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Редактировать состояние</h2>
          
          <form @submit.prevent="saveStateChanges" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
              <input
                v-model="stateForm.label"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>
            <div class="flex items-center gap-4">
              <label class="flex items-center gap-2">
                <input
                  v-model="stateForm.initial"
                  type="checkbox"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded"
                />
                <span class="text-sm text-gray-700">Начальное</span>
              </label>
              <label class="flex items-center gap-2">
                <input
                  v-model="stateForm.completion"
                  type="checkbox"
                  class="w-4 h-4 text-emerald-600 border-gray-300 rounded"
                />
                <span class="text-sm text-gray-700">Конечное</span>
              </label>
            </div>

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                @click="editingState = null"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Toast -->
    <Teleport to="body">
      <Transition name="toast">
        <div
          v-if="toast.show"
          class="fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg bg-emerald-600 text-white"
        >
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, reactive, onMounted } from 'vue'
import type { Workflow, DocumentType, WorkflowState } from '@/types/admin'
import { adminService } from '@/services/adminService'

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const selectedWorkflow = ref<Workflow | null>(null)
const showCreateModal = ref(false)
const isEditing = ref(false)
const editingState = ref<WorkflowState | null>(null)
const dragOverIndex = ref<number | null>(null)
let draggedIndex: number | null = null
const isLoading = ref(false)
const error = ref<string | null>(null)

const toast = reactive({
  show: false,
  message: ''
})

const newWorkflowForm = ref({
  label: '',
  internal_name: '',
  auto_launch: false
})

const stateForm = ref({
  label: '',
  initial: false,
  completion: false
})

// Document types (will be loaded from API)
const documentTypes = ref<DocumentType[]>([])

// Workflows from real API
const workflows = ref<Workflow[]>([])

// ═══════════════════════════════════════════════════════════════════════════════
// Data Loading
// ═══════════════════════════════════════════════════════════════════════════════
async function loadWorkflows() {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await adminService.getWorkflows({ page_size: 100 })
    
    // Map Mayan workflows to frontend Workflow interface
    workflows.value = response.results.map(wf => ({
      id: wf.id,
      label: wf.label,
      internal_name: wf.internal_name || wf.label.toLowerCase().replace(/\s+/g, '_'),
      auto_launch: false, // Mayan doesn't have this concept directly
      document_types: wf.document_types || [],
      states: wf.states || [],
      transitions: wf.transitions || [],
      instances_count: 0
    }))
    
    console.log('[AdminWorkflows] Loaded workflows:', workflows.value.length)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Ошибка загрузки рабочих процессов'
    console.error('[AdminWorkflows] Failed to load workflows:', err)
  } finally {
    isLoading.value = false
  }
}

// Initial load
onMounted(() => {
  loadWorkflows()
})

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function showToast(message: string) {
  toast.message = message
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

function selectWorkflow(workflow: Workflow): void {
  selectedWorkflow.value = JSON.parse(JSON.stringify(workflow)) // Deep clone for editing
  isEditing.value = false
}

async function createNewWorkflow(): Promise<void> {
  try {
    const response = await adminService.createWorkflow({
      label: newWorkflowForm.value.label,
      internal_name: newWorkflowForm.value.internal_name || newWorkflowForm.value.label.toLowerCase().replace(/\s+/g, '_')
    })
    
    showCreateModal.value = false
    newWorkflowForm.value = { label: '', internal_name: '', auto_launch: false }
    showToast('Рабочий процесс создан')
    
    // Reload and select the new workflow
    await loadWorkflows()
    const newWorkflow = workflows.value.find(w => w.id === response.id)
    if (newWorkflow) {
      selectWorkflow(newWorkflow)
    }
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Ошибка создания процесса'
    showToast(errorMsg)
    console.error('[AdminWorkflows] Failed to create workflow:', err)
  }
}

function getStateName(stateId: number): string {
  if (!selectedWorkflow.value) return ''
  const state = selectedWorkflow.value.states.find(s => s.id === stateId)
  return state?.label ?? 'Unknown'
}

function getTransitionLabel(fromId: number, toId: number): string {
  if (!selectedWorkflow.value || !toId) return ''
  const transition = selectedWorkflow.value.transitions.find(
    t => t.origin_state_id === fromId && t.destination_state_id === toId
  )
  return transition?.label ?? ''
}

// Drag & Drop
function onDragStart(event: DragEvent, index: number): void {
  draggedIndex = index
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
}

function onDragOver(event: DragEvent, index: number): void {
  event.preventDefault()
  dragOverIndex.value = index
}

function onDrop(event: DragEvent, dropIndex: number): void {
  event.preventDefault()
  if (draggedIndex === null || !selectedWorkflow.value) return
  
  const states = selectedWorkflow.value.states
  const [draggedState] = states.splice(draggedIndex, 1)
  states.splice(dropIndex, 0, draggedState)
  
  // Update order
  states.forEach((state, idx) => {
    state.order = idx
  })
  
  dragOverIndex.value = null
  draggedIndex = null
  showToast('Порядок состояний изменён')
}

function onDragEnd(): void {
  dragOverIndex.value = null
  draggedIndex = null
}

// State CRUD
function editState(state: WorkflowState): void {
  if (!isEditing.value) return
  editingState.value = state
  stateForm.value = {
    label: state.label,
    initial: state.initial,
    completion: state.completion
  }
}

function saveStateChanges(): void {
  if (!editingState.value || !selectedWorkflow.value) return
  
  const stateIdx = selectedWorkflow.value.states.findIndex(s => s.id === editingState.value!.id)
  if (stateIdx > -1) {
    // If setting as initial, remove initial from others
    if (stateForm.value.initial) {
      selectedWorkflow.value.states.forEach(s => s.initial = false)
    }
    // If setting as completion, remove completion from others
    if (stateForm.value.completion) {
      selectedWorkflow.value.states.forEach(s => s.completion = false)
    }
    
    selectedWorkflow.value.states[stateIdx] = {
      ...selectedWorkflow.value.states[stateIdx],
      label: stateForm.value.label,
      initial: stateForm.value.initial,
      completion: stateForm.value.completion
    }
  }
  
  editingState.value = null
  showToast('Состояние обновлено')
}

function addState(): void {
  if (!selectedWorkflow.value) return
  
  const newState: WorkflowState = {
    id: Date.now(),
    workflow_id: selectedWorkflow.value.id,
    label: 'Новое состояние',
    initial: false,
    completion: false,
    actions: [],
    order: selectedWorkflow.value.states.length
  }
  
  // Insert before the last (completion) state
  const insertIndex = selectedWorkflow.value.states.length - 1
  selectedWorkflow.value.states.splice(insertIndex, 0, newState)
  showToast('Состояние добавлено')
}

function removeState(stateId: number): void {
  if (!selectedWorkflow.value) return
  
  const stateIdx = selectedWorkflow.value.states.findIndex(s => s.id === stateId)
  if (stateIdx > -1) {
    selectedWorkflow.value.states.splice(stateIdx, 1)
    // Also remove transitions involving this state
    selectedWorkflow.value.transitions = selectedWorkflow.value.transitions.filter(
      t => t.origin_state_id !== stateId && t.destination_state_id !== stateId
    )
  }
  showToast('Состояние удалено')
}

function addTransition(): void {
  if (!selectedWorkflow.value || selectedWorkflow.value.states.length < 2) return
  
  // Add transition between first two states that don't have one
  const states = selectedWorkflow.value.states
  for (let i = 0; i < states.length - 1; i++) {
    const existing = selectedWorkflow.value.transitions.find(
      t => t.origin_state_id === states[i].id && t.destination_state_id === states[i + 1].id
    )
    if (!existing) {
      selectedWorkflow.value.transitions.push({
        id: Date.now(),
        workflow_id: selectedWorkflow.value.id,
        label: 'Новый переход',
        origin_state_id: states[i].id,
        destination_state_id: states[i + 1].id,
        condition: '',
        triggers: []
      })
      showToast('Переход добавлен')
      return
    }
  }
  showToast('Все переходы уже существуют')
}

function removeTransition(transitionId: number): void {
  if (!selectedWorkflow.value) return
  
  const idx = selectedWorkflow.value.transitions.findIndex(t => t.id === transitionId)
  if (idx > -1) {
    selectedWorkflow.value.transitions.splice(idx, 1)
  }
  showToast('Переход удалён')
}

function saveWorkflowChanges(): void {
  if (!selectedWorkflow.value) return
  
  const idx = workflows.value.findIndex(w => w.id === selectedWorkflow.value!.id)
  if (idx > -1) {
    workflows.value[idx] = JSON.parse(JSON.stringify(selectedWorkflow.value))
  }
  
  isEditing.value = false
  showToast('Изменения сохранены')
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

