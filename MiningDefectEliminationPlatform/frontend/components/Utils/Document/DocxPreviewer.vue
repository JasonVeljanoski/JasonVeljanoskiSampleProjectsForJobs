<template>
  <div class="dox-prev-root">
    <slot />
  </div>
</template>

<script>
export default {
  name: "DocxPreviewer",
  // Solve bug in vue-pdf https://github.com/FranckFreiburger/vue-pdf/issues/327
  errorCaptured() {
    return false;
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;
.dox-prev-root {
  background: var(--v-accent-base);
  height: calc(100vh - #{$header-height} - #{$stepper-height} - 80px);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 2em;
  > * {
    background: white;
    display: block;
    margin: 0 auto;
    margin-bottom: 0.5cm;
    box-shadow: 0 0 0.5cm rgba(0, 0, 0, 0.5);
    // max-width: 80%;
    max-width: 1000px;
  }
}
</style>
