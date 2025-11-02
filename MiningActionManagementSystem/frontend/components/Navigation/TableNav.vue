<template>
  <div>
    <v-btn
      v-for="(tab, index) in tabs"
      :key="index"
      :color="tab.title === currtab.title ? 'primary' : null"
      small
      tile
      text
      @click="changeTab(tab)"
      >{{ tab.title }}</v-btn
    >
  </div>
</template>

<script>
export default {
  props: {
    currtab: {
      type: Object,
    },
    tabs: {
      type: Array,
    },
  },
  data() {
    return {}
  },
  methods: {
    changeTab(item) {
      this.$emit('input', item)
    },
  },
}
</script>

<style></style>
