<template>
  <div>
    {{ formatted_value }}
    <e-icon-btn v-if="has_completed_rca" right color="warning" tooltip="Completed RCA document still required">
      mdi-alert
    </e-icon-btn>
  </div>
</template>

<script>
export default {
  props: {
    value: { type: Number, default: false },
    has_completed_rca: { type: Boolean, default: false },
  },
  computed: {
    formatted_value() {
      return this.$enums.investigation_types[this.value];
    },
  },
};
</script>

<style></style>
