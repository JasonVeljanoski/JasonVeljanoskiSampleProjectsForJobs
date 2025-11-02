<template>
  <div>
    <v-chip v-if="value" :color="color" label class="chip">
      <v-icon v-if="icon" left>{{ icon }}</v-icon>
      <b style="color: white">{{ label }}</b>
    </v-chip>

    <div v-else class="reader_text">No Value</div>
  </div>
</template>

<script>
export default {
  props: {
    value: { type: Object },
  },
  computed: {
    color() {
      return this.value?.color || 'primary'
    },
    icon() {
      return this.value?.icon
    },
    label() {
      return this.value?.label
    },
  },
}
</script>

<style lang="scss" scoped>
.chip {
  min-width: 100px;
  display: flex;
  justify-content: center;
  border-radius: 5px !important;
}
</style>
