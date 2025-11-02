<template>
  <v-chip :color="color">
    <b>{{ value }}</b>
  </v-chip>
</template>

<script>
export default {
  props: {
    value: { type: String, default: false },
  },
  computed: {
    color() {
      if (!this.value) return;

      if (this.value.toLowerCase() == "low") return "success";
      else if (this.value.toLowerCase() == "medium") return "warning";
      else if (this.value.toLowerCase() == "high") return "error";
    },
  },
};
</script>

<style lang="scss" scoped>
h3 {
  margin-right: 5px;
}
</style>
