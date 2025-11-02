<template>
  <div class="scroll-container">
    <the-investigation-process :key="renderKey" />
  </div>
</template>

<script>
import TheInvestigationProcess from "@/components/Investigation/TheInvestigationProcess";

export default {
  name: "NewInvestigation",
  components: {
    TheInvestigationProcess,
  },
  head() {
    return {
      title: "Investigation",
    };
  },
  data() {
    return {
      renderKey: 0,
    };
  },
  beforeRouteUpdate(to, from, next) {
    this.renderKey++;
    next();
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;

.scroll-container {
  height: calc(100vh - #{$header-height} - 24px);
  overflow: auto;

  scroll-snap-type: y mandatory;
}
</style>
