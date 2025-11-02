<!-- BaseForm.vue -->
<template>
  <form @submit.prevent="handleSubmit" novalidate>
    <div class="base-form">
      <slot />
    </div>
  </form>
</template>

<script setup>
import { provide, ref } from 'vue'

const formFields = ref(new Set())

provide('form', {
  register: (field) => {
    formFields.value.add(field)
    return () => {
      formFields.value.delete(field)
    }
  },
})

const validate = async () => {
  const validationResults = await Promise.all(
    Array.from(formFields.value).map((field) => field.validateField())
  )
  return validationResults.every((result) => result !== false)
}

const handleSubmit = async () => {
  const isValid = await validate()

  if (isValid) {
    emit('submit')
  }
}

defineExpose({
  validate,
})

const emit = defineEmits(['submit'])
</script>
