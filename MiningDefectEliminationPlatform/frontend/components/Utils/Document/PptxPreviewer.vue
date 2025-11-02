<template>
  <div>
    <slot />
  </div>
</template>

<script>
export default {
  name: "PptxPreviewer",
  // Solve bug in vue-pdf https://github.com/FranckFreiburger/vue-pdf/issues/327
  errorCaptured() {
    return false;
  },
};
</script>

<style lang="scss" scoped></style>
