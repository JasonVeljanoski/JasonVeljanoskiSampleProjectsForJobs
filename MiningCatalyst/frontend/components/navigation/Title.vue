<template>
  <span class="title">
    <h1 v-for="(word, ii) in title.split(' ')" :key="ii">
      {{ word }}
    </h1>
  </span>
</template>

<script>
export default {
  computed: {
    title() {
      try {
        return this.$slots.default[0].text || ''
      } catch {
        return ''
      }
    },
  },
}
</script>

<style lang="scss" scoped>
.title {
  white-space: nowrap;
  display: flex;
  gap: 0.5ch;
}

.title > * {
  font-family: system-ui;
  &::first-letter {
    color: #418fde !important;
    font-weight: bold;
  }
}
</style>
