<template>
  <Teleport to="body">
    <TransitionGroup name="snackbar">
      <div
        v-for="item in snackbarQueue"
        :key="item.id"
        :class="['base-snackbar', `base-snackbar--${item.type}`]"
      >
        {{ item.text }}
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { SnackbarTypeEnum } from '@/enums/SnackbarTypeEnum'

const snackbarQueue = ref([])

const addSnackbar = (text, type = SnackbarTypeEnum.Info, delay = 3000) => {
  const id = Date.now()

  // simple validation of type
  if (!Object.values(SnackbarTypeEnum).includes(type)) {
    type = SnackbarTypeEnum.Info
  }

  const snackbar = { id, text, type }
  snackbarQueue.value.push(snackbar)

  setTimeout(() => {
    snackbarQueue.value = snackbarQueue.value.filter((item) => item.id !== id)
  }, delay)
}

defineExpose({ addSnackbar })
</script>

<style lang="scss" scoped>
.base-snackbar {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 4px;
  color: white;
  font-size: 14px;
  z-index: 9999;

  & + .base-snackbar {
    transform: translateX(-50%) translateY(-100%);
    margin-bottom: 10px;
  }

  &--info {
    background-color: var(--holmwoods-blue);
  }

  &--success {
    background-color: var(--success);
  }

  &--error {
    background-color: var(--error);
  }
}

.snackbar-enter-active,
.snackbar-leave-active {
  transition: all 0.3s ease;
}

.snackbar-enter-from,
.snackbar-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(100%);
}
</style>
