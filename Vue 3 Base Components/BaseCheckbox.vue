<template>
  <div class="base-checkbox">
    <label
      class="base-checkbox--wrapper"
      :class="{ 'base-checkbox--disabled': disabled }"
    >
      <input
        type="checkbox"
        class="base-checkbox--input"
        :disabled="disabled"
        :checked="modelValue"
        @change="$emit('update:modelValue', $event.target.checked)"
      />
      <span class="base-checkbox--checkmark" :style="checkboxStyle"></span>
      <span v-if="label" class="base-checkbox--label">{{ label }}</span>
      <slot v-else></slot>
    </label>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  color: { type: String, default: undefined },
  disabled: { type: Boolean, default: null },
  label: { type: String, default: undefined },
})

const emit = defineEmits(['update:modelValue'])

const checkboxStyle = computed(() => {
  const style = {}

  if (props.color) {
    const isVariable = props.color.startsWith('--')
    style['--checkbox-color'] = isVariable ? `var(${props.color})` : props.color
  }

  return style
})
</script>

<style lang="scss" scoped>
.base-checkbox {
  display: inline-block;

  &--wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
    cursor: pointer;
    user-select: none;
  }

  &--input {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;

    &:checked ~ .base-checkbox--checkmark {
      background-color: var(--checkbox-color, #000);
      border-color: var(--checkbox-color, #000);

      &:after {
        display: block;
      }
    }
  }

  &--checkmark {
    position: relative;
    height: 18px;
    width: 18px;
    background-color: transparent;
    border: 2px solid #999;
    border-radius: 4px;
    transition: all 0.2s;

    &:after {
      content: '';
      position: absolute;
      display: none;
      left: 5px;
      top: 1px;
      width: 5px;
      height: 10px;
      border: solid white;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg);
    }
  }

  &--label {
    margin-left: 8px;
    font-size: 14px;
    text-wrap: nowrap;
  }

  &--disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }

  &--wrapper:hover .base-checkbox--checkmark {
    border-color: var(--checkbox-color, #666);
  }
}
</style>
