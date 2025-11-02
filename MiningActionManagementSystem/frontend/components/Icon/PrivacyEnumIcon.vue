<template>
  <v-tooltip bottom>
    <template #activator="{ on, attrs }">
      <v-icon v-bind="attrs" :color="color" v-on="on">{{ icon }}</v-icon>
    </template>
    <span>{{ text }}</span>
  </v-tooltip>
</template>

<script>
export default {
  props: {
    value: { type: Number, default: false },
  },
  computed: {
    text() {
      return this.$enums.privacy[this.value]
    },
    color() {
      if (this.text == this.$enums.privacy[1]) return ''
      else if (this.text == this.$enums.privacy[3]) return ''
    },
    icon() {
      if (this.text == this.$enums.privacy[1]) return 'mdi-lock-open-variant-outline'
      else if (this.text == this.$enums.privacy[3]) return 'mdi-lock-outline'
    },
  },
}
</script>

<style></style>
