<template>
  <div class="d-flex justify-center align-center">
    <svg
      class="svg-wrapper"
      id="Layer_1"
      data-name="Layer 1"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 409 605.73"
    >
      <title>logo_pass1</title>
      <rect
        class="cls-1"
        x="68"
        y="338"
        width="267"
        height="267"
        rx="11"
        transform="translate(673 270) rotate(90)"
      />
      <circle class="cls-1" cx="362.5" cy="471.5" r="43.5" />
      <circle class="cls-1" cx="43.5" cy="471.5" r="43.5" />
      <rect class="cls-2" x="70" y="71" width="267" height="267" rx="10.39" />
      <circle class="cls-2" cx="365.5" cy="204.5" r="43.5" />
      <circle class="cls-2" cx="203.5" cy="43.5" r="43.5" />
      <circle class="cls-2" cx="203.5" cy="362.5" r="43.5" />
      <path
        class="cls-3"
        d="M68,174.53A45.2,45.2,0,0,1,98.31,163C123,163,143,182.48,143,206.5S123,250,98.31,250A45.27,45.27,0,0,1,69,239.35"
      />
      <path class="cls-3" d="M168.46,605.73a43.5,43.5,0,1,1,68.56,0" />
    </svg>
    <e-title>DEP</e-title>
  </div>
</template>

<script scoped>
export default {};
</script>

<style scoped>
.svg-wrapper {
  margin-right: 10px;
  max-width: 30px;
  transform: rotate(45deg); /* notice the order */
}
.cls-3 {
  fill: var(--v-accent-base) !important;
}
.cls-1 {
  fill: var(--v-warning-base) !important;
}
.cls-2 {
  fill: var(--v-primary-base) !important;
}
</style>
