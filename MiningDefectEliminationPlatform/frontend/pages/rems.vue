<template>
  <rems-chart />
</template>

<script>
import RemsChart from "@/components/Dashboards/RemsChart";

export default {
  components: {
    RemsChart,
  },
  head() {
    return {
      title: "REMS",
    };
  },
};
</script>

<style lang="scss" scoped></style>
