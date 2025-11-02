<template>
  <div class="d-flex justify-center align-center">
    <div class="svg-wrapper">
      <v-img
        :src="`/magnify.png`"
        style="cursor: pointer"
        max-height="70"
        max-width="150"
        @click="$router.push('/')"
      />
    </div>
    <e-title>DEP</e-title>
  </div>
</template>

<script scoped>
export default {};
</script>

<style scoped>
.svg-wrapper {
  margin-right: 5px;
  max-width: 40px;
}

.cls-1 {
  fill: var(--v-warning-base);
}
.cls-2 {
  fill: var(--v-primary-base);
}
.cls-3 {
  fill: var(--v-secondary-base);
}
</style>
