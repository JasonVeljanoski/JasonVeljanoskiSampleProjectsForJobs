<template>
  <v-dialog
    v-model="dialog"
    scrollable
    :width="$attrs.width || 'unset'"
    :persistent="persistent"
    v-bind="{ ...$attrs, ...$props }"
    @keydown.esc="persistent ? null : close()"
    v-on="$listeners"
  >
    <v-card :scrollable="scrollable" v-bind="{ ...cardProps }">
      <slot>
        <i>Place Dialog stuff here (already in a v-card)</i>
      </slot>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    persistent: { type: Boolean, default: false },
    scrollable: { type: Boolean, default: false },
    cardProps: { type: Object, default: () => {} },
  },
  data() {
    return {
      dialog: false,
    }
  },
  methods: {
    open() {
      this.dialog = true
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    close(status = false) {
      this.resolve(status)
      this.dialog = false
    },
    cancel() {
      this.resolve(false)
      this.dialog = false
    },
  },
}
</script>

<style></style>
