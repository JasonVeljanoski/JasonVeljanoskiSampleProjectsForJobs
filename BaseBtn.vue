<template>
  <button
    class="base-btn"
    :class="[inheritClass, `base-btn--${size}`, buttonStateClasses]"
    :style="[buttonStyle, active && activeStyle]"
    :disabled="disabled"
  >
    <div v-if="!loading" class="base-btn__content">
      <component
        v-if="iconComponent && props.iconPosition === 'left'"
        :is="iconComponent"
        :style="props.iconStyle"
        class="base-btn__icon"
      />
      <slot />
      <component
        v-if="iconComponent && props.iconPosition === 'right'"
        :is="iconComponent"
        :style="props.iconStyle"
        class="base-btn__icon"
      />
    </div>

    <div v-else class="base-btn__loader">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>
  </button>
</template>

<script setup>
import { computed, defineAsyncComponent, useSlots, useAttrs } from 'vue'
import { logger } from 'twizzdom-common'

const props = defineProps({
  active: { type: Boolean, default: undefined },
  icon: { type: String, default: undefined },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  activeStyle: { type: [Object, String], default: undefined },
  iconStyle: { type: [Object, String], default: undefined },
  iconPosition: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right'].includes(value),
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['small', 'default', 'large'].includes(value),
  },
  color: { type: String, default: undefined },
  outlined: { type: Boolean, default: false },
  text: { type: Boolean, default: false },
})

//#region Classes
const buttonStateClasses = computed(() => ({
  'base-btn--active': props.active && !props.activeStyle,
  'base-btn--disabled': props.disabled,
  'base-btn--loading': props.loading,
  'base-btn--outlined': props.outlined,
  'base-btn--text': props.text,
  'base-btn--icon-only': iconOnly.value,
}))

const attrs = useAttrs()
const inheritClass = computed(() => attrs.class || '')
//#endregion

//#region Icon
const slots = useSlots()
const iconOnly = computed(() => {
  const defaultSlot = slots.default?.()
  const hasText = defaultSlot?.some(
    (node) =>
      (typeof node.children === 'string' && node.children.trim() !== '') ||
      (node.type === 'text' && node.content?.trim() !== '')
  )
  return !hasText && !!props.icon
})

const iconComponent = computed(() => {
  if (!props.icon) return null

  return defineAsyncComponent({
    loader: () => import(`@icons/${props.icon}.svg?component`),
    onError: (error) => {
      logger.error(`Icon ${props.icon} not found:`, {
        error: error,
      })
      return null
    },
  })
})
//#endregion

//#region Style
const buttonStyle = computed(() => {
  const style = {}

  if (props.color) {
    const isVariable = props.color.startsWith('--')
    const colorValue = isVariable ? `var(${props.color})` : props.color

    if (props.outlined) {
      style.color = colorValue
      style['border-color'] = colorValue
    } else if (props.text) {
      style.color = colorValue
    } else {
      style['background-color'] = colorValue
      style.color = '#ffffff'
    }
  } else if (props.outlined) {
    style['border-color'] = 'currentColor'
  }

  return style
})
//#endregion
</script>

<style lang="scss" scoped>
.base-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  vertical-align: middle;
  border: 2px solid transparent;
  border-radius: 10px;
  background-color: #fff;
  color: inherit;
  font-weight: 500;
  line-height: 1;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;

  &:hover:not(.base-btn--disabled) {
    &:not(.base-btn--text):not(.base-btn--outlined) {
      filter: brightness(0.9);
    }
  }

  &--small {
    height: 28px;
    min-width: 50px;
    padding: 0 12px;
    font-size: 12px;
    border-width: 1px;

    &.base-btn--icon-only {
      width: 28px;
      height: 28px;
      min-width: 28px;
      min-height: 28px;
      padding: 0;
    }

    .base-btn__loader .dot {
      width: 4px;
      height: 4px;
    }

    .base-btn__icon {
      width: 14px;
      height: 14px;
    }
  }

  &--default {
    height: 36px;
    min-width: 64px;
    padding: 0 16px;
    font-size: 14px;
    border-width: 1px;

    &.base-btn--icon-only {
      width: 36px;
      height: 36px;
      min-width: 36px;
      min-height: 36px;
      padding: 0;
    }

    .base-btn__loader .dot {
      width: 5px;
      height: 5px;
    }

    .base-btn__icon {
      width: 18px;
      height: 18px;
    }
  }

  &--large {
    height: 50px;
    min-width: 78px;
    padding: 0 24px;
    font-size: 16px;
    // Keeps the default 2px border

    &.base-btn--icon-only {
      width: 50px;
      height: 50px;
      min-width: 50px;
      min-height: 50px;
      padding: 0;
    }

    .base-btn__loader .dot {
      width: 6px;
      height: 6px;
    }

    .base-btn__icon {
      width: 22px;
      height: 22px;
    }
  }

  &__loader {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    height: 100%;

    .dot {
      border-radius: 50%;
      background-color: currentColor;
      animation: dotPulse 1.5s infinite;

      &:nth-child(2) {
        animation-delay: 0.2s;
      }

      &:nth-child(3) {
        animation-delay: 0.4s;
      }
    }
  }

  @keyframes dotPulse {
    0%,
    60%,
    100% {
      transform: scale(1);
      opacity: 1;
    }
    30% {
      transform: scale(1.75);
      opacity: 0.5;
    }
  }

  &__content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    height: 100%;
    line-height: 1;
  }

  &__icon {
    display: flex;
    align-items: center;
    justify-content: center;

    :deep(svg) {
      fill: currentColor;
    }
  }

  &--active {
    filter: brightness(0.85);
  }

  &--disabled {
    opacity: 0.6;
    pointer-events: none;
  }

  &--outlined {
    background-color: transparent !important;

    &:hover:not(.base-btn--disabled) {
      filter: none;
      background-color: rgba(0, 0, 0, 0.04) !important;
    }
  }

  &--text {
    background-color: transparent !important;
    border-color: transparent !important;
    padding: 0 8px !important;
    min-width: 0 !important;

    &:hover:not(.base-btn--disabled) {
      filter: none;
      background-color: rgba(0, 0, 0, 0.04) !important;
    }
  }
}
</style>
