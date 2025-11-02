<template>
  <v-btn-toggle
    group
    mandatory
    outlined
    dense
    class="d-flex justify-center"
    active-class="primary--text"
    @change="tabChange"
  >
    <v-btn v-for="tab in navbar_buttons" :key="tab.idx" :value="tab.idx">
      <span>{{ tab.title }}</span>
      <v-icon :color="value == tab.idx ? 'primary' : ''" right>
        {{ tab.icon }}
      </v-icon>
    </v-btn>
  </v-btn-toggle>
</template>

<script>
export default {
  props: {
    items: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      value: 0,
    }
  },
  computed: {
    navbar_buttons() {
      return this.items.filter((x) => x.show)
    },
  },
  mounted() {
    this.$emit('change', 0)
  },
  methods: {
    tabChange(e) {
      this.value = e
      this.$emit('change', this.value)
    },
  },
}
</script>

<style lang="scss" scoped></style>
