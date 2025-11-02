<template>
  <div
    class="base-text-field"
    :class="{
      'base-text-field--error': error || computedErrorMessages.length > 0,
      'base-text-field--disabled': disabled,
      'base-text-field--loading': loading,
      'base-text-field--inside-label': labelPosition === 'inside',
    }"
    :style="computedStyles"
  >
    <label
      v-if="label && labelPosition === 'float'"
      class="base-text-field__label"
    >
      {{ label }}
    </label>

    <div class="base-text-field__input-wrapper">
      <span
        v-if="label && labelPosition === 'inside'"
        class="base-text-field__inside-label"
      >
        {{ label }}
      </span>

      <input
        ref="input"
        v-bind="$attrs"
        :value="props.modelValue"
        :type="type"
        :disabled="disabled"
        :placeholder="placeholder"
        class="base-text-field__input"
        @input="updateValue"
      />

      <div ref="appendedInnerItems" class="base-text-field__appended-items">
        <span
          data-testid="append-inner-button"
          @click="emit('click:appendInnerIcon')"
        >
          <div v-if="$slots.appendInner" class="item">
            <slot name="appendInner" />
          </div>
          <component
            v-else-if="appendInnerIconComponent"
            :is="appendInnerIconComponent"
            class="item"
          />
        </span>

        <span
          v-if="clearable && modelValue"
          data-testid="clear-button"
          class="item close-icon"
          @click="clearInput"
        >
          <CloseIcon />
        </span>
      </div>
    </div>

    <div v-if="loading" class="base-text-field__progress" />

    <div
      v-if="computedErrorMessages.length > 0"
      class="base-text-field__error-messages"
      data-testid="error-messages"
    >
      <div
        v-for="(message, index) in computedErrorMessages"
        :key="index"
        class="base-text-field__error-message"
      >
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, ref, defineAsyncComponent, nextTick } from 'vue'
import CloseIcon from '@icons/close.svg?component'
import { logger, debounce } from 'twizzdom-common'
import { useFormField } from '@/composables/useFormField'
import { useFormValidation } from '@/composables/useFormValidation'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: undefined,
  },
  type: {
    type: String,
    default: undefined,
  },
  label: {
    type: String,
    default: undefined,
  },
  labelPosition: {
    type: String,
    default: 'float',
    validator: (value) => ['float', 'inside'].includes(value),
  },
  placeholder: {
    type: String,
    default: undefined,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: [Boolean, null],
    default: null,
  },
  maxWidth: {
    type: [String, Number],
    default: undefined,
  },
  minWidth: {
    type: [String, Number],
    default: undefined,
  },
  width: {
    type: [String, Number],
    default: undefined,
  },
  error: {
    type: Boolean,
    default: false,
  },
  errorMessages: {
    type: [String, Array],
    default: () => [],
  },
  rules: {
    type: Array,
    default: () => [],
  },
  appendInnerIcon: {
    type: String,
    default: undefined,
  },
})

defineOptions({
  inheritAttrs: false,
})

const emit = defineEmits({
  'update:modelValue': (value) => true,
  error: (hasError) => typeof hasError === 'boolean',
  'click:appendInnerIcon': null,
  'click:clear': null,
})

//#region v-model
const clearInput = () => {
  emit('update:modelValue', '')
  emit('click:clear')
  debouncedValidateField()
}
//#endregion

//#region Validation
const { validateField, computedErrorMessages } = useFormValidation(props, emit)
useFormField(validateField)
//#endregion

//#region Width
const formatDimension = (value) => {
  // append px to numbers
  if (typeof value === 'number') {
    return `${value}px`
  }

  // if it's a string, check if it already has a unit
  const hasUnit = value.match(/^[0-9]+(%|px|em|rem|vh|vw)$/)
  if (hasUnit) {
    return value
  }

  // if it's just a number as string, append px
  const isNumeric = /^\d+$/.test(value)
  if (isNumeric) {
    return `${value}px`
  }

  return value
}

const computedStyles = computed(() => ({
  width: props.width ? formatDimension(props.width) : undefined,
  maxWidth: props.maxWidth ? formatDimension(props.maxWidth) : undefined,
  minWidth: props.minWidth ? formatDimension(props.minWidth) : undefined,
}))
//#endregion

//#region Icons
const appendInnerIconComponent = computed(() => {
  if (!props.appendInnerIcon) return null

  return defineAsyncComponent({
    loader: () => import(`@icons/${props.appendInnerIcon}.svg?component`),
    onError: (error) => {
      logger.error(`Icon ${props.icon} not found:`, {
        error: error,
      })
      return null
    },
  })
})

// update right-padding so input text does not overflow
const appendedInnerItems = ref(null)
const input = ref(null)
const updatePadding = async () => {
  await nextTick()
  if (appendedInnerItems.value && input.value) {
    const width = appendedInnerItems.value.offsetWidth
    if (width > 0) input.value.style.paddingRight = `${width + 16}px`
  }
}

const DEBOUNCE_TIMEOUT = 150
const debouncedUpdatePadding = debounce(updatePadding, DEBOUNCE_TIMEOUT)
const debouncedValidateField = debounce(validateField, DEBOUNCE_TIMEOUT)
const updateValue = (event) => {
  emit('update:modelValue', event.target.value)
  debouncedValidateField()
  debouncedUpdatePadding()
}
//#endregion
</script>

<style lang="scss" scoped>
.base-text-field {
  position: relative;
  width: 100%;

  &__label {
    display: block;
    margin-bottom: 4px;
    font-size: 12px;
  }

  &__inside-label {
    position: absolute;
    top: 4px;
    left: 12px;
    font-size: 10px;
    color: rgba(0, 0, 0, 0.6);
    pointer-events: none;
  }

  &__input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  &__input {
    .base-text-field--inside-label & {
      padding: 17px 12px 8px;
    }

    white-space: nowrap;
    overflow-x: auto;

    width: 100%;
    border: 1px solid rgba(0, 0, 0, 0.25);
    outline: none;
    transition: border-color 0.2s;
    border-radius: 8px;

    &:focus,
    &:hover {
      border-color: rgba(0, 0, 0, 0.8);
    }

    &::placeholder {
      color: rgba(0, 0, 0, 0.4);
      font-weight: normal;
    }
  }

  &__appended-items {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    gap: 8px;
    color: rgba(0, 0, 0, 0.4);

    .item {
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 17px;
      min-height: 17px;

      svg {
        width: 17px;
        height: 17px;
      }

      :deep(*:not(svg)) {
        color: inherit;
      }

      &:hover {
        color: rgba(0, 0, 0, 0.8);
      }
    }

    .close-icon {
      margin-right: 8px;
    }
  }

  &__progress {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    overflow: hidden;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 50%;
      height: 100%;
      background-color: var(--holmwoods-blue);
      animation: slide 1s infinite;
    }
  }

  @keyframes slide {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(200%);
    }
  }

  &__error-messages {
    margin-top: 4px;
    margin-left: 4px;
    font-size: 12px;
    color: var(--error);
  }

  &--error {
    .base-text-field__input {
      border-color: var(--error);

      &:focus {
        border-color: var(--error);
      }
    }

    .base-text-field__label {
      color: var(--error);
    }

    .base-text-field__inside-label {
      color: var(--error);
    }
  }

  &--disabled {
    opacity: 0.6;
    pointer-events: none;
  }
}
</style>
