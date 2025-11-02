<template>
  <v-chip :color="color">
    <v-icon left>{{ icon }}</v-icon>
    <b>{{ text }}</b>
  </v-chip>
</template>

<script>
export default {
  props: {
    value: { type: Number, default: false },
  },
  computed: {
    text() {
      return this.$enums.feedback_status[this.value];
    },
    icon() {
      if (this.text == this.$enums.feedback_status[1])
        return "mdi-package-variant";
      else if (this.text == this.$enums.feedback_status[2])
        return "mdi-package-variant-minus";
      else if (this.text == this.$enums.feedback_status[3])
        return "mdi-package-variant-closed-check";
      else if (this.text == this.$enums.feedback_status[4])
        return "mdi-package-variant-closed-check";
      else if (this.text == this.$enums.feedback_status[5])
        return "mdi-package-variant-closed-check";
    },
    color() {
      if (this.text == this.$enums.feedback_status[1]) return "primary";
      else if (this.text == this.$enums.feedback_status[2]) return "warning";
      else if (this.text == this.$enums.feedback_status[3]) return "success";
      else if (this.text == this.$enums.feedback_status[4]) return "success";
      else if (this.text == this.$enums.feedback_status[5]) return "success";
    },
  },
};
</script>

<style></style>
