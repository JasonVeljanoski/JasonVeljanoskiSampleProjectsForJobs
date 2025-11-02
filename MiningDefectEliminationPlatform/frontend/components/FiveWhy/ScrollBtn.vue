<template>
  <div class="scroll-root">
    <div class="connector-single" />

    <v-btn
      v-bind="$bind.btn"
      :disabled="disable"
      @click="
        $emit('click');
        elementScroll('scrollToMe');
      "
    >
      <slot />
      <v-icon right>mdi-chevron-down</v-icon>
    </v-btn>

    <div v-if="unfoil || disable" class="connector-single" />

    <div ref="scrollToMe" />
  </div>
</template>

<script>
export default {
  props: {
    unfoil: { type: Boolean, default: false },
  },
  data() {
    return {
      disable: false,
    };
  },
  methods: {
    elementScroll(ref_name) {
      this.$utils.scrollToElement(ref_name, this);
    },
  },
};
</script>

<style lang="scss" scoped>
.scroll-root {
  display: flex;
  align-items: center;
  flex-direction: column;
}

.connector-single {
  height: 20px;
  width: 1px;
  display: block;
  background-color: var(--v-accent-base);
}
</style>
