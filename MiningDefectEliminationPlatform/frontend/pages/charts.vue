<template>
  <aplus-chart />
</template>

<script>
import AplusChart from "@/components/Dashboards/AplusChart";

export default {
  components: {
    AplusChart,
  },
  head() {
    return {
      title: "APLUS",
    };
  },
};
</script>

<style lang="scss" scoped></style>
