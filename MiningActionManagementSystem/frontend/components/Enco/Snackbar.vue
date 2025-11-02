<template>
  <div class="notification-root">
    <v-alert v-for="item in items" :key="item.id" :type="item.type" dismissible border="left" @input="remove(item)">
      <!-- <span v-html="item.message" /> -->
      <!-- <span v-text="item.message" /> -->
      <span>{{ item.message }}</span>
    </v-alert>
  </div>
</template>

<script>
import { mapGetters, mapMutations } from 'vuex'

export default {
  data() {
    return {
      timers: {},
    }
  },
  computed: {
    ...mapGetters({
      items: 'snackbar/items',
    }),
  },
  watch: {
    items() {
      for (const item of this.items) {
        if (!this.timers[item.id] && item.duration >= 0) {
          this.timers[item.id] = setTimeout(() => this.remove(item), item.duration)
        }
      }
    },
  },
  methods: {
    ...mapMutations({
      remove: 'snackbar/remove',
    }),
  },
}
</script>

<style lang="scss" scoped>
.notification-root {
  position: absolute;
  bottom: 0;
  width: 100%;

  z-index: 9999;

  pointer-events: none;

  > * {
    margin: 4px auto;
    width: fit-content;
    min-width: 600px;
    pointer-events: all;

    ::v-deep .v-alert__icon {
      margin-top: auto;
      margin-bottom: auto;
    }
  }
}

span {
  white-space: pre-wrap;
}
</style>
