<template>
  <div>
    <h4>Total Effective Duration</h4>
    <v-text-field
      v-model="total_effective_duration"
      v-bind="$bind.select"
      hide-details="auto"
      disabled
    />

    <template v-if="event_type === $enums.event_types['APLUS']">
      <h4>Total Event Duration</h4>
      <v-text-field
        v-model="total_event_duration"
        v-bind="$bind.select"
        hide-details="auto"
        disabled
        :key="keyNum"
      />

      <h4>Lost Tonnes</h4>
      <v-text-field
        v-model="total_lost_tonnes"
        v-bind="$bind.select"
        hide-details="auto"
        disabled
      />
    </template>
  </div>
</template>

<script>
export default {
  props: {
    event_type: { type: Number },
    aplus_events: { type: Array },
    rems_events: { type: Array },
    inputItem: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      keyNum: 0,
    };
  },
  computed: {
    total_event_duration() {
      if (this.aplus_events.length > 0 || this.inputItem?.type == "aplus")
        return this.$event_metrics.totalAplusEventDuration(
          this.aplus_events,
          true,
          this.inputItem
        );
    },
    total_effective_duration() {
      if (this.aplus_events.length > 0)
        return this.$event_metrics.totalAplusEffectiveDuration(
          this.aplus_events,
          true
        );
      else if (this.rems_events.length > 0 || this.inputItem?.type == "rems")
        if (this.inputItem != null) {
          let hrs = "0.0";
          hrs = parseFloat(this.inputItem.event_duration).toFixed(1).toString();
          return hrs + " hrs";
        }
      return this.$event_metrics.totalRemsEventDuration(this.rems_events, true);
    },
    total_lost_tonnes() {
      if (this.aplus_events.length > 0)
        return this.$event_metrics.totalAplusLostTonnes(
          this.aplus_events,
          true
        );
    },
  },
};
</script>
