<template>
  <div
    ref="canvasRef"
    class="workflow-canvas"
    :style="canvasStyle"
    @wheel.prevent="handleWheel"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @mouseleave="handleMouseLeave"
  >
    <!-- Grid Background -->
    <svg
      v-if="showGrid"
      class="workflow-canvas__grid"
      :width="canvasWidth"
      :height="canvasHeight"
    >
      <defs>
        <pattern
          id="grid"
          :width="gridSize"
          :height="gridSize"
          patternUnits="userSpaceOnUse"
        >
          <path
            :d="`M ${gridSize} 0 L 0 0 0 ${gridSize}`"
            fill="none"
            stroke="var(--color-border, #e5e7eb)"
            stroke-width="1"
          />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
    </svg>

    <!-- Nodes -->
    <div
      v-for="node in nodes"
      :key="node.id"
      :class="[
        'workflow-node',
        `workflow-node--${node.type}`,
        { 'workflow-node--selected': selectedNodeId === node.id }
      ]"
      :style="getNodeStyle(node)"
      @mousedown.stop="handleNodeMouseDown($event, node)"
      @click.stop="handleNodeClick(node)"
      :draggable="true"
      @dragstart="handleNodeDragStart($event)"
      @dragend="handleNodeDragEnd"
      role="button"
      tabindex="0"
      :aria-label="`Workflow node: ${node.name}`"
    >
      <div class="workflow-node__header">
        <span class="workflow-node__type-icon">
          <svg
            v-if="node.type === 'start'"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else-if="node.type === 'end'"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
            />
          </svg>
          <svg
            v-else
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </span>
        <span class="workflow-node__name">{{ node.name }}</span>
      </div>
      <p v-if="node.description" class="workflow-node__description">
        {{ node.description }}
      </p>
    </div>

    <!-- Transitions (Arrows) -->
    <svg
      class="workflow-canvas__transitions"
      :width="canvasWidth"
      :height="canvasHeight"
    >
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="3"
          orient="auto"
        >
          <polygon points="0 0, 10 3, 0 6" fill="var(--color-text, #111827)" />
        </marker>
      </defs>
      <g
        v-for="transition in transitions"
        :key="transition.id"
        @click.stop="handleTransitionClick(transition)"
        class="workflow-transition"
        :class="{ 'workflow-transition--selected': selectedTransitionId === transition.id }"
      >
        <path
          :d="getTransitionPath(transition)"
          fill="none"
          stroke="var(--color-text, #111827)"
          stroke-width="2"
          marker-end="url(#arrowhead)"
          class="workflow-transition__line"
        />
        <text
          :x="getTransitionLabelX(transition)"
          :y="getTransitionLabelY(transition)"
          class="workflow-transition__label"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          {{ transition.label || '→' }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { WorkflowNode, WorkflowTransition } from '@/types/admin'

interface Props {
  nodes: WorkflowNode[]
  transitions: WorkflowTransition[]
  zoom: number
  pan: { x: number; y: number }
  selectedNodeId?: string | null
  selectedTransitionId?: string | null
  showGrid?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  zoom: 1,
  pan: () => ({ x: 0, y: 0 }),
  selectedNodeId: null,
  selectedTransitionId: null,
  showGrid: true
})

const emit = defineEmits<{
  'node-click': [node: WorkflowNode]
  'transition-click': [transition: WorkflowTransition]
  'node-drag': [nodeId: string, position: { x: number; y: number }]
  'pan-change': [pan: { x: number; y: number }]
  'zoom-change': [zoom: number]
}>()

const canvasRef = ref<HTMLElement | null>(null)
const canvasWidth = ref(2000)
const canvasHeight = ref(2000)
const gridSize = 20
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragNodeId = ref<string | null>(null)
const dragStart = ref({ x: 0, y: 0 })

const canvasStyle = computed(() => {
  return {
    transform: `translate(${props.pan.x}px, ${props.pan.y}px) scale(${props.zoom})`,
    transformOrigin: '0 0'
  }
})

const getNodeStyle = (node: WorkflowNode) => {
  return {
    left: `${node.position.x}px`,
    top: `${node.position.y}px`
  }
}

const getTransitionPath = (transition: WorkflowTransition): string => {
  const fromNode = props.nodes.find((n) => n.id === transition.from_node)
  const toNode = props.nodes.find((n) => n.id === transition.to_node)

  if (!fromNode || !toNode) return ''

  const fromX = fromNode.position.x + 100 // Node width / 2
  const fromY = fromNode.position.y + 50 // Node height / 2
  const toX = toNode.position.x + 100
  const toY = toNode.position.y + 50

  // Calculate control points for curved line
  const dx = toX - fromX
  const controlX1 = fromX + dx * 0.5
  const controlY1 = fromY
  const controlX2 = toX - dx * 0.5
  const controlY2 = toY

  return `M ${fromX} ${fromY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${toX} ${toY}`
}

const getTransitionLabelX = (transition: WorkflowTransition): number => {
  const fromNode = props.nodes.find((n) => n.id === transition.from_node)
  const toNode = props.nodes.find((n) => n.id === transition.to_node)
  if (!fromNode || !toNode) return 0
  return (fromNode.position.x + toNode.position.x) / 2 + 100
}

const getTransitionLabelY = (transition: WorkflowTransition): number => {
  const fromNode = props.nodes.find((n) => n.id === transition.from_node)
  const toNode = props.nodes.find((n) => n.id === transition.to_node)
  if (!fromNode || !toNode) return 0
  return (fromNode.position.y + toNode.position.y) / 2 + 50
}

const handleWheel = (event: WheelEvent): void => {
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  const newZoom = Math.max(0.5, Math.min(2, props.zoom + delta))
  emit('zoom-change', newZoom)
}

const handleMouseDown = (event: MouseEvent): void => {
  if (event.button === 1 || (event.button === 0 && event.ctrlKey)) {
    // Middle mouse or Ctrl+Left for panning
    isPanning.value = true
    panStart.value = { x: event.clientX - props.pan.x, y: event.clientY - props.pan.y }
    event.preventDefault()
  }
}

const handleMouseMove = (event: MouseEvent): void => {
  if (isPanning.value) {
    emit('pan-change', {
      x: event.clientX - panStart.value.x,
      y: event.clientY - panStart.value.y
    })
  } else if (isDragging.value && dragNodeId.value) {
    const rect = canvasRef.value?.getBoundingClientRect()
    if (rect) {
      const x = (event.clientX - rect.left - props.pan.x) / props.zoom
      const y = (event.clientY - rect.top - props.pan.y) / props.zoom
      emit('node-drag', dragNodeId.value, { x, y })
    }
  }
}

const handleMouseUp = (): void => {
  isPanning.value = false
  isDragging.value = false
  dragNodeId.value = null
}

const handleMouseLeave = (): void => {
  isPanning.value = false
  isDragging.value = false
  dragNodeId.value = null
}

const handleNodeMouseDown = (event: MouseEvent, node: WorkflowNode): void => {
  if (event.button === 0 && !event.ctrlKey) {
    isDragging.value = true
    dragNodeId.value = node.id
    const rect = canvasRef.value?.getBoundingClientRect()
    if (rect) {
      dragStart.value = {
        x: event.clientX - rect.left - node.position.x * props.zoom,
        y: event.clientY - rect.top - node.position.y * props.zoom
      }
    }
  }
}

const handleNodeClick = (node: WorkflowNode): void => {
  emit('node-click', node)
}

const handleNodeDragStart = (event: DragEvent): void => {
  // Prevent default drag behavior, we handle it manually
  event.preventDefault()
}

const handleNodeDragEnd = (): void => {
  isDragging.value = false
  dragNodeId.value = null
}

const handleTransitionClick = (transition: WorkflowTransition): void => {
  emit('transition-click', transition)
}

onMounted(() => {
  if (canvasRef.value) {
    canvasWidth.value = canvasRef.value.offsetWidth || 2000
    canvasHeight.value = canvasRef.value.offsetHeight || 2000
  }
})

onUnmounted(() => {
  isPanning.value = false
  isDragging.value = false
})
</script>

<style scoped lang="css">
.workflow-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--color-bg-1, #f9fafb);
  cursor: grab;
}

.workflow-canvas:active {
  cursor: grabbing;
}

.workflow-canvas__grid {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.workflow-canvas__transitions {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: stroke;
}

.workflow-node {
  position: absolute;
  width: 200px;
  min-height: 80px;
  padding: 12px;
  background: var(--color-surface, #ffffff);
  border: 2px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 8px);
  cursor: move;
  transition: all 150ms ease;
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.1));
}

.workflow-node:hover {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: var(--shadow-md, 0 4px 6px rgba(0, 0, 0, 0.1));
}

.workflow-node--selected {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.workflow-node--start {
  border-color: var(--color-success, #10b981);
}

.workflow-node--end {
  border-color: var(--color-error, #ef4444);
}

.workflow-node__header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.workflow-node__type-icon {
  display: flex;
  align-items: center;
  color: var(--color-text-secondary, #6b7280);
}

.workflow-node__name {
  font-weight: 600;
  color: var(--color-text, #111827);
  font-size: var(--font-size-base, 14px);
}

.workflow-node__description {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

.workflow-transition {
  cursor: pointer;
}

.workflow-transition__line {
  transition: stroke-width 150ms ease;
}

.workflow-transition:hover .workflow-transition__line {
  stroke-width: 3;
  stroke: var(--color-primary, #3b82f6);
}

.workflow-transition--selected .workflow-transition__line {
  stroke: var(--color-primary, #3b82f6);
  stroke-width: 3;
}

.workflow-transition__label {
  font-size: 12px;
  fill: var(--color-text, #111827);
  pointer-events: none;
  background: var(--color-surface, #ffffff);
  padding: 2px 4px;
}
</style>

