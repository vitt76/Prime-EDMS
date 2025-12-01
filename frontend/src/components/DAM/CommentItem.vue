<template>
  <div class="comment-item">
    <div class="flex gap-3">
      <!-- Avatar -->
      <div class="flex-shrink-0">
        <div
          v-if="comment.author_avatar"
          class="w-10 h-10 rounded-full bg-neutral-200 dark:bg-neutral-200 overflow-hidden"
        >
          <img :src="comment.author_avatar" :alt="comment.author" class="w-full h-full object-cover" />
        </div>
        <div
          v-else
          class="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold"
        >
          {{ comment.author.charAt(0).toUpperCase() }}
        </div>
      </div>

      <!-- Comment Content -->
      <div class="flex-1">
        <div class="bg-neutral-50 dark:bg-neutral-50 rounded-lg p-3">
          <!-- Header -->
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-sm text-neutral-900 dark:text-neutral-900">
                {{ comment.author }}
              </span>
              <span class="text-xs text-neutral-600 dark:text-neutral-600">
                {{ formatRelativeTime(comment.created_date) }}
              </span>
              <span v-if="comment.edited" class="text-xs text-neutral-500 dark:text-neutral-500 italic">
                (отредактировано)
              </span>
            </div>
            <div v-if="canEdit" class="flex items-center gap-1">
              <button
                v-if="!isEditing"
                class="text-xs text-neutral-600 dark:text-neutral-600 hover:text-primary-500"
                @click="startEdit"
              >
                Редактировать
              </button>
              <button
                class="text-xs text-neutral-600 dark:text-neutral-600 hover:text-error"
                @click="handleDelete"
              >
                Удалить
              </button>
            </div>
          </div>

          <!-- Comment Text -->
          <div v-if="!isEditing" class="text-sm text-neutral-900 dark:text-neutral-900 whitespace-pre-wrap">
            <span v-for="(part, index) in formattedText" :key="index">
              <span v-if="part.type === 'mention'" class="text-primary-500 font-medium">
                @{{ part.text }}
              </span>
              <span v-else>{{ part.text }}</span>
            </span>
          </div>

          <!-- Edit Form -->
          <div v-else class="space-y-2">
            <textarea
              v-model="editText"
              class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-0 dark:text-neutral-900"
              rows="3"
              @keydown.esc="cancelEdit"
              @keydown.ctrl.enter="saveEdit"
              @keydown.meta.enter="saveEdit"
            ></textarea>
            <div class="flex justify-end gap-2">
              <Button variant="outline" size="sm" @click="cancelEdit">
                Отмена
              </Button>
              <Button variant="primary" size="sm" @click="saveEdit">
                Сохранить
              </Button>
            </div>
          </div>

          <!-- Actions -->
          <div v-if="!isEditing" class="mt-2 flex items-center gap-4">
            <button
              class="text-xs text-neutral-600 dark:text-neutral-600 hover:text-primary-500"
              @click="handleReply"
            >
              Ответить
            </button>
          </div>
        </div>

        <!-- Replies -->
        <div v-if="comment.replies && comment.replies.length > 0" class="mt-3 ml-4 space-y-3 border-l-2 border-neutral-200 dark:border-neutral-200 pl-4">
          <CommentItem
            v-for="reply in comment.replies"
            :key="reply.id"
            :comment="reply"
            :current-user-id="currentUserId"
            @reply="$emit('reply', $event)"
            @edit="$emit('edit', $event, $event)"
            @delete="$emit('delete', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Comment } from '@/types/api'
import { formatRelativeTime } from '@/utils/formatters'
import Button from '@/components/Common/Button.vue'

interface Props {
  comment: Comment
  currentUserId?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  reply: [comment: Comment]
  edit: [comment: Comment, newText: string]
  delete: [comment: Comment]
}>()

const isEditing = ref(false)
const editText = ref('')

const canEdit = computed(() => {
  return props.currentUserId && props.comment.author_id === props.currentUserId
})

const formattedText = computed(() => {
  const text = props.comment.text
  const parts: Array<{ type: 'text' | 'mention'; text: string }> = []
  const mentionRegex = /@(\w+)/g
  let lastIndex = 0
  let match

  while ((match = mentionRegex.exec(text)) !== null) {
    // Add text before mention
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        text: text.substring(lastIndex, match.index)
      })
    }
    // Add mention
    parts.push({
      type: 'mention',
      text: match[1]
    })
    lastIndex = match.index + match[0].length
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push({
      type: 'text',
      text: text.substring(lastIndex)
    })
  }

  return parts.length > 0 ? parts : [{ type: 'text', text }]
})

function startEdit() {
  editText.value = props.comment.text
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  editText.value = ''
}

function saveEdit() {
  if (editText.value.trim() && editText.value !== props.comment.text) {
    emit('edit', props.comment, editText.value.trim())
  }
  isEditing.value = false
}

function handleReply() {
  emit('reply', props.comment)
}

function handleDelete() {
  if (confirm('Вы уверены, что хотите удалить этот комментарий?')) {
    emit('delete', props.comment)
  }
}
</script>

<style scoped>
.comment-item {
  margin-bottom: 0.5rem;
}
</style>

