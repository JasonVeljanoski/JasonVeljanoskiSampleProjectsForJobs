<template>
  <div
    class="base-btn-toggle"
    :class="{
      'base-btn-toggle--divided': divided,
      'base-btn-toggle--vertical': vertical,
    }"
  >
    <BaseBtn
      v-for="(btn, index) in processedButtons"
      :key="btn.key || index"
      v-bind="btn.props"
      :active="isActive(index)"
      :disabled="disabled"
      @click="updateValue(index)"
    >
      <template v-if="btn.slots?.default">
        <component :is="btn.slots.default" />
      </template>
      <template v-else>
        {{ btn.text }}
      </template>
    </BaseBtn>
  </div>
</template>

<script setup>
import { useSlots, computed } from 'vue'
import BaseBtn from './BaseBtn.vue'

const props = defineProps({
  modelValue: {
    type: [Number, Array],
    default: 0,
  },
  divided: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  mandatory: {
    type: [Boolean, String],
    default: false,
    validator: (value) => {
      return typeof value === 'boolean' || value === 'force'
    },
  },
  vertical: {
    type: Boolean,
    default: false,
  },
  multiple: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const isActive = (index) => {
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.includes(index)
  }
  return props.modelValue === index
}

const updateValue = (index) => {
  if (props.disabled) return

  if (props.multiple) {
    const newValue = Array.isArray(props.modelValue)
      ? [...props.modelValue]
      : []
    const indexPosition = newValue.indexOf(index)

    if (indexPosition === -1) {
      newValue.push(index)
    } else if (!props.mandatory || newValue.length > 1) {
      newValue.splice(indexPosition, 1)
    }

    emit('update:modelValue', newValue)
  } else {
    if (props.mandatory) {
      if (props.mandatory === 'force' || index !== props.modelValue) {
        emit('update:modelValue', index)
      }
    } else {
      emit('update:modelValue', index === props.modelValue ? -1 : index)
    }
  }
}

const slots = useSlots()

const processedButtons = computed(() => {
  if (!slots.default) return []

  const vnodes = slots.default()

  // Handle both direct BaseBtn children and v-for generated buttons
  return vnodes.reduce((acc, vnode) => {
    if (vnode.type && vnode.type.__name === 'BaseBtn') {
      // Direct BaseBtn child
      acc.push({
        props: vnode.props || {},
        slots: vnode.children || {},
        key: vnode.key,
      })
    } else if (Array.isArray(vnode.children)) {
      // Handle v-for generated content
      const children = vnode.children.filter(
        (child) => child.type && child.type.__name === 'BaseBtn'
      )

      acc.push(
        ...children.map((child) => ({
          props: child.props || {},
          slots: child.children || {},
          text: child.children?.default?.(),
          key: child.key,
        }))
      )
    }
    return acc
  }, [])
})
</script>

<style lang="scss" scoped>
.base-btn-toggle {
  display: inline-flex;
  border-radius: 8px;
  padding: 4px !important;

  &--vertical {
    flex-direction: column;

    :deep(.base-btn) {
      border-radius: 0;

      &:first-child {
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
      }

      &:last-child {
        border-top-left-radius: 0;
        border-top-right-radius: 0;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
      }
    }
  }

  &:not(.base-btn-toggle--vertical) {
    :deep(.base-btn) {
      border-radius: 0;

      &:first-child {
        border-top-left-radius: 8px;
        border-bottom-left-radius: 8px;
      }

      &:last-child {
        border-top-right-radius: 8px;
        border-bottom-right-radius: 8px;
      }
    }
  }

  &--divided {
    gap: 4px;

    :deep(.base-btn) {
      border-radius: 8px !important;
    }
  }
}
</style>
