<template>
  <div class="dialog" data-testid="base-dialog">
    <!--#region Activator slot -->
    <slot
      name="activator"
      :props="{
        onClick: handleActivatorClick,
      }"
    />
    <!--#endregion    -->

    <!--#region Dialog overlay -->
    <Transition name="dialog--fade">
      <div
        v-if="modelValue"
        class="dialog--overlay"
        data-testid="base-dialog-overlay"
        :class="{ 'dialog--overlay--has-scrim': scrim }"
        :style="scrimStyles"
        @click="handleOverlayClick"
      >
        <div
          class="dialog--content"
          data-testid="base-dialog-content"
          :style="contentStyles"
          @click="handleContentClick"
        >
          <slot name="default" :isActive="{ value: modelValue }"></slot>
        </div>
      </div>
    </Transition>
    <!--#endregion    -->
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  closeOnContentClick: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  maxWidth: {
    type: [String, Number],
    default: null,
  },
  persistent: {
    type: Boolean,
    default: false,
  },
  scrim: {
    type: [String, Boolean],
    default: true,
  },
})

const emit = defineEmits(['update:modelValue'])

//#region Styles
const scrimStyles = computed(() => {
  if (typeof props.scrim === 'string') {
    return { backgroundColor: props.scrim }
  }
  return {}
})

const contentStyles = computed(() => {
  const styles = {}
  if (props.maxWidth) {
    styles.maxWidth = isNaN(props.maxWidth)
      ? props.maxWidth
      : `${props.maxWidth}px`
  }
  return styles
})
//#endregion

//#region Event Handles
const handleActivatorClick = () => {
  if (!props.disabled) {
    emit('update:modelValue', true)
  }
}

const handleOverlayClick = (e) => {
  if (e.target === e.currentTarget && !props.persistent) {
    emit('update:modelValue', false)
  }
}

const handleContentClick = () => {
  if (props.closeOnContentClick) {
    emit('update:modelValue', false)
  }
}

const handleEscapeKey = (e) => {
  if (e.key === 'Escape' && !props.persistent) {
    emit('update:modelValue', false)
  }
}
//#endregion

//#region Lifecycle hooks
onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleEscapeKey)
})
//#endregion
</script>

<style lang="scss" scoped>
.dialog {
  display: inline-block;

  &--overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99999;

    &--has-scrim {
      background-color: rgba(0, 0, 0, 0.5);
    }
  }

  &--content {
    position: relative;
    width: 100%;
    margin: 24px;
    border-radius: 4px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  &--fade-enter-active,
  &--fade-leave-active {
    transition: opacity 0.3s ease;
  }

  &--fade-enter-from,
  &--fade-leave-to {
    opacity: 0;
  }
}
</style>
