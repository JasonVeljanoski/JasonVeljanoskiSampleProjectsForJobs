<template>
  <div class="root">
    <e-enum-icon v-for="v in value" :key="v.id" :value="v" :style="{ width: width }" />
  </div>
</template>

<script>
export default {
  props: {
    value: { type: Array },
    width: { type: String, default: '230px' },
  },
}
</script>

<style lang="scss" scoped>
.root {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
