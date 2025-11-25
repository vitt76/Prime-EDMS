<template>
  <div class="comments-thread">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
        Комментарии ({{ totalCommentsCount }})
      </h3>
    </div>

    <!-- Add Comment Form -->
    <div class="mb-6">
      <div class="flex gap-3">
        <div class="flex-1">
          <textarea
            v-model="newCommentText"
            :placeholder="replyingTo ? `Ответить ${replyingTo.author}...` : 'Добавить комментарий...'"
            class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-neutral-0 dark:text-neutral-900"
            rows="3"
            @keydown.ctrl.enter="handleSubmitComment"
            @keydown.meta.enter="handleSubmitComment"
            @input="handleMentionInput"
          ></textarea>
          <div v-if="replyingTo" class="mt-2 flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-600">
            <span>Ответ на комментарий от {{ replyingTo.author }}</span>
            <button
              class="text-primary-500 hover:text-primary-600"
              @click="cancelReply"
            >
              Отмена
            </button>
          </div>
          <div v-if="mentionSuggestions.length > 0" class="mt-2">
            <div class="bg-white dark:bg-neutral-0 border border-neutral-300 dark:border-neutral-300 rounded-md shadow-lg max-h-40 overflow-y-auto">
              <button
                v-for="user in mentionSuggestions"
                :key="user"
                class="w-full text-left px-4 py-2 hover:bg-neutral-100 dark:hover:bg-neutral-100 text-sm"
                @click="selectMention(user)"
              >
                @{{ user }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="mt-2 flex justify-end gap-2">
        <Button
          v-if="replyingTo"
          variant="outline"
          size="sm"
          @click="cancelReply"
        >
          Отмена
        </Button>
        <Button
          variant="primary"
          size="sm"
          :disabled="!newCommentText.trim() || isSubmitting"
          :loading="isSubmitting"
          @click="handleSubmitComment"
        >
          {{ replyingTo ? 'Ответить' : 'Отправить' }}
        </Button>
      </div>
    </div>

    <!-- Comments List -->
    <div v-if="comments.length > 0" class="space-y-4">
      <CommentItem
        v-for="comment in topLevelComments"
        :key="comment.id"
        :comment="comment"
        :current-user-id="currentUserId"
        @reply="handleReply"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8 text-neutral-600 dark:text-neutral-600">
      <svg
        class="mx-auto h-12 w-12 mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
      <p>Пока нет комментариев. Будьте первым!</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-4">
      <div class="animate-spin h-6 w-6 mx-auto text-primary-500"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { commentService } from '@/services/commentService'
import { websocketService } from '@/services/websocketService'
import type { Comment, CreateCommentRequest } from '@/types/api'
import { formatRelativeTime } from '@/utils/formatters'
import Button from '@/components/Common/Button.vue'
import CommentItem from './CommentItem.vue'
import { useAuthStore } from '@/stores/authStore'
import { onMounted, onUnmounted } from 'vue'

interface Props {
  assetId: number
  initialComments?: Comment[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'comment-added': [comment: Comment]
  'comment-updated': [comment: Comment]
  'comment-deleted': [commentId: number]
}>()

const authStore = useAuthStore()
const comments = ref<Comment[]>(props.initialComments || [])
const newCommentText = ref('')
const replyingTo = ref<Comment | null>(null)
const isSubmitting = ref(false)
const isLoading = ref(false)
const mentionSuggestions = ref<string[]>([])
const currentMentionQuery = ref('')

// Mock user list for mentions (in real app, this would come from API)
const availableUsers = ref<string[]>(['admin', 'user1', 'user2', 'designer', 'manager'])

const currentUserId = computed(() => authStore.user?.id)

const topLevelComments = computed(() => {
  return comments.value.filter((c) => !c.parent_id)
})

const totalCommentsCount = computed(() => {
  const countReplies = (comment: Comment): number => {
    return 1 + (comment.replies?.reduce((sum, reply) => sum + countReplies(reply), 0) || 0)
  }
  return topLevelComments.value.reduce((sum, comment) => sum + countReplies(comment), 0)
})

onMounted(async () => {
  if (!props.initialComments) {
    await loadComments()
  }

  // Subscribe to WebSocket events for real-time updates
  websocketService.subscribeToAsset(props.assetId)
  
  // Listen for comment events
  const unsubscribeAdded = websocketService.on('comment_added', (data: any) => {
    if (data.asset_id === props.assetId) {
      const newComment = data.comment as Comment
      if (newComment.parent_id) {
        const parent = findCommentById(comments.value, newComment.parent_id)
        if (parent) {
          if (!parent.replies) {
            parent.replies = []
          }
          parent.replies.push(newComment)
        }
      } else {
        comments.value.push(newComment)
      }
    }
  })

  const unsubscribeUpdated = websocketService.on('comment_updated', (data: any) => {
    if (data.asset_id === props.assetId) {
      const updated = data.comment as Comment
      const found = findCommentById(comments.value, updated.id)
      if (found) {
        found.text = updated.text
        found.updated_date = updated.updated_date
        found.edited = true
      }
    }
  })

  const unsubscribeDeleted = websocketService.on('comment_deleted', (data: any) => {
    if (data.asset_id === props.assetId) {
      const commentId = data.comment_id as number
      // Remove comment from tree
      if (data.parent_id) {
        const parent = findCommentById(comments.value, data.parent_id)
        if (parent?.replies) {
          const index = parent.replies.findIndex((c) => c.id === commentId)
          if (index !== -1) {
            parent.replies.splice(index, 1)
          }
        }
      } else {
        const index = comments.value.findIndex((c) => c.id === commentId)
        if (index !== -1) {
          comments.value.splice(index, 1)
        }
      }
    }
  })

  // Store unsubscribe functions for cleanup
  ;(window as any).__commentUnsubscribers = [
    unsubscribeAdded,
    unsubscribeUpdated,
    unsubscribeDeleted
  ]
})

onUnmounted(() => {
  // Unsubscribe from WebSocket events
  websocketService.unsubscribeFromAsset(props.assetId)
  
  // Clean up event handlers
  const unsubscribers = (window as any).__commentUnsubscribers
  if (unsubscribers) {
    unsubscribers.forEach((unsub: () => void) => unsub())
    delete (window as any).__commentUnsubscribers
  }
})

watch(() => props.initialComments, (newComments) => {
  if (newComments) {
    comments.value = newComments
  }
})

async function loadComments() {
  isLoading.value = true
  try {
    comments.value = await commentService.getComments(props.assetId)
  } catch (error) {
    console.error('Failed to load comments:', error)
  } finally {
    isLoading.value = false
  }
}

function handleMentionInput(event: Event) {
  const textarea = event.target as HTMLTextAreaElement
  const text = textarea.value
  const cursorPos = textarea.selectionStart
  const textBeforeCursor = text.substring(0, cursorPos)
  const mentionMatch = textBeforeCursor.match(/@(\w*)$/)

  if (mentionMatch) {
    currentMentionQuery.value = mentionMatch[1]
    const query = currentMentionQuery.value.toLowerCase()
    mentionSuggestions.value = availableUsers.value.filter((user) =>
      user.toLowerCase().startsWith(query) && user.toLowerCase() !== query
    )
  } else {
    mentionSuggestions.value = []
  }
}

function selectMention(username: string) {
  const textarea = document.querySelector('textarea') as HTMLTextAreaElement
  if (!textarea) return

  const text = newCommentText.value
  const cursorPos = textarea.selectionStart
  const textBeforeCursor = text.substring(0, cursorPos)
  const mentionMatch = textBeforeCursor.match(/@(\w*)$/)

  if (mentionMatch) {
    const start = cursorPos - mentionMatch[0].length
    newCommentText.value =
      text.substring(0, start) + `@${username} ` + text.substring(cursorPos)
    mentionSuggestions.value = []
    currentMentionQuery.value = ''
    
    // Set cursor position after mention
    setTimeout(() => {
      textarea.focus()
      const newPos = start + `@${username} `.length
      textarea.setSelectionRange(newPos, newPos)
    }, 0)
  }
}

async function handleSubmitComment() {
  if (!newCommentText.value.trim() || isSubmitting.value) return

  isSubmitting.value = true
  try {
    const mentions = extractMentions(newCommentText.value)
    const commentData: CreateCommentRequest = {
      text: newCommentText.value.trim(),
      mentions,
      parent_id: replyingTo.value?.id
    }

    const newComment = await commentService.createComment(props.assetId, commentData)
    
    if (replyingTo.value) {
      // Add reply to parent comment
      const parent = findCommentById(comments.value, replyingTo.value.id)
      if (parent) {
        if (!parent.replies) {
          parent.replies = []
        }
        parent.replies.push(newComment)
      }
      replyingTo.value = null
    } else {
      // Add as top-level comment
      comments.value.push(newComment)
    }

    newCommentText.value = ''
    emit('comment-added', newComment)
  } catch (error) {
    console.error('Failed to create comment:', error)
    // TODO: Show error toast
  } finally {
    isSubmitting.value = false
  }
}

function extractMentions(text: string): string[] {
  const mentionRegex = /@(\w+)/g
  const mentions: string[] = []
  let match

  while ((match = mentionRegex.exec(text)) !== null) {
    mentions.push(match[1])
  }

  return [...new Set(mentions)] // Remove duplicates
}

function findCommentById(commentsList: Comment[], id: number): Comment | null {
  for (const comment of commentsList) {
    if (comment.id === id) return comment
    if (comment.replies) {
      const found = findCommentById(comment.replies, id)
      if (found) return found
    }
  }
  return null
}

function handleReply(comment: Comment) {
  replyingTo.value = comment
  // Scroll to textarea
  setTimeout(() => {
    const textarea = document.querySelector('textarea')
    textarea?.focus()
  }, 100)
}

function cancelReply() {
  replyingTo.value = null
}

async function handleEdit(comment: Comment, newText: string) {
  try {
    const updated = await commentService.updateComment(
      props.assetId,
      comment.id,
      { text: newText }
    )
    
    // Update comment in tree
    const found = findCommentById(comments.value, comment.id)
    if (found) {
      found.text = updated.text
      found.updated_date = updated.updated_date
      found.edited = true
    }
    
    emit('comment-updated', updated)
  } catch (error) {
    console.error('Failed to update comment:', error)
  }
}

async function handleDelete(comment: Comment) {
  if (!confirm('Вы уверены, что хотите удалить этот комментарий?')) {
    return
  }

  try {
    await commentService.deleteComment(props.assetId, comment.id)
    
    // Remove comment from tree
    if (comment.parent_id) {
      const parent = findCommentById(comments.value, comment.parent_id)
      if (parent?.replies) {
        const index = parent.replies.findIndex((c) => c.id === comment.id)
        if (index !== -1) {
          parent.replies.splice(index, 1)
        }
      }
    } else {
      const index = comments.value.findIndex((c) => c.id === comment.id)
      if (index !== -1) {
        comments.value.splice(index, 1)
      }
    }
    
    emit('comment-deleted', comment.id)
  } catch (error) {
    console.error('Failed to delete comment:', error)
  }
}
</script>

<style scoped>
.comments-thread {
  padding: 1rem;
}
</style>

