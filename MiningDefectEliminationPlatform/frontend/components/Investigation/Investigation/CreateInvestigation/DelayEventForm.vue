<template>
  <!--   
    REMS SAMPLE IDS
    '63C5F5A9-94C5-4268-93C6-631B7EA51370', 
    '63c5f5a9-94c5-4268-93c6-631b7ea51370'
    '92BBF1D2-22E1-4381-AD50-A17B83246B0B', 
    '2D45D4A8-E34C-48FD-ACAE-C2BD520A4E09'
 -->
  <div v-if="investigation">
    <!-- TOGGLE APLUS / REMS -->
    <div class="my-2" align="center" justify="center">
      <v-btn-toggle
        v-show="!loading"
        v-model="investigation.event_type"
        mandatory
        dense
        color="primary"
        @change="resetSelectedEvents()"
      >
        <v-btn :value="$enums.event_types['APLUS']">APLUS</v-btn>
        <v-btn :value="$enums.event_types['REMS']">REMS</v-btn>
      </v-btn-toggle>
    </div>
    <span class="d-flex">
      <h4>Delay Accounting Event ID(s)</h4>
      <small class="ml-2">(optional)</small>
    </span>

    <div class="d-flex align-center">
      <!-- IF APLUS TOGGLE -->
      <v-combobox
        v-if="is_aplus"
        v-model="investigation.aplus_delay_event_ids"
        v-bind="$bind.select"
        :readonly="loading"
        :clearable="!loading"
        multiple
        append-icon=""
        type="number"
        @change="updateAplusDelay"
        @click:clear="resetMetrics"
      />

      <!-- IF REMS TOGGLE -->
      <v-combobox
        v-if="is_rems"
        v-model="investigation.rems_delay_event_ids"
        v-bind="$bind.select"
        :readonly="loading"
        :clearable="!loading"
        multiple
        append-icon=""
        type="text"
        @click:clear="resetMetrics"
      />

      <!-- QUERY ICON BTN -->
      <e-icon-btn
        v-if="!loading"
        color="primary"
        tooltip="fetch event info"
        :disabled="loading"
        @click="fetchEventDetails"
      >
        mdi-database-search
      </e-icon-btn>
      <e-icon-btn
        v-else
        color="warning"
        tooltip="cancel request"
        @click="cancelRequest"
      >
        mdi-cancel
      </e-icon-btn>
    </div>

    <!-- DISPLAY METRICS -->
    <div v-if="loading" class="d-flex justify-center my-4">
      <v-progress-circular
        indeterminate
        :color="is_aborting ? 'warning' : 'primary'"
      />
    </div>
    <div v-else>
      <h4>Total Event Duration</h4>
      <v-text-field
        :value="formatTotal(investigation.total_event_duration)"
        v-bind="$bind.select"
        disabled
        hide-details="auto"
      />
      <template v-if="is_aplus">
        <h4>Total Effective Duration</h4>
        <v-text-field
          :value="formatTotal(investigation.total_effective_duration)"
          v-bind="$bind.select"
          disabled
          hide-details="auto"
        />
        <h4>Lost Tonnes</h4>
        <v-text-field
          :value="formatTotal(investigation.total_tonnes_lost)"
          v-bind="$bind.select"
          disabled
          hide-details="auto"
        />
      </template>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    investigation: { type: Object },
  },
  data() {
    return {
      loading: false,
      controller: null,
      is_aborting: false,
    };
  },
  computed: {
    is_rems() {
      return (
        this.investigation &&
        this.investigation.event_type === this.$enums.event_types["REMS"]
      );
    },
    is_aplus() {
      return (
        this.investigation &&
        this.investigation.event_type === this.$enums.event_types["APLUS"]
      );
    },
  },
  watch: {
    loading() {
      this.$emit("loading", this.loading);
    },
  },
  methods: {
    resetMetrics() {
      this.investigation.total_tonnes_lost = 0.0;
      this.investigation.total_effective_duration = 0.0;
      this.investigation.total_event_duration = 0.0;
    },
    cancelRequest() {
      this.controller.abort();
      this.is_aborting = true;
      this.$snackbar.add("Cancelling request...", "info");
    },
    formatTotal(total) {
      if (total) return total.toFixed(1);
      return 0.0;
    },
    updateAplusDelay() {
      // combobox naturally gives array of strings, we want integers!
      this.investigation.aplus_delay_event_ids =
        this.investigation.aplus_delay_event_ids.map((str) => +str);
    },
    resetSelectedEvents() {
      this.investigation.aplus_delay_event_ids = [];
      this.investigation.rems_delay_event_ids = [];
      this.investigation.total_tonnes_lost = 0.0;
      this.investigation.total_effective_duration = 0.0;
      this.investigation.total_event_duration = 0.0;
    },
    fetchEventDetails() {
      this.is_aborting = false;

      if (this.is_rems && this.investigation.rems_delay_event_ids.length > 0) {
        this.loading = true;

        this.investigation.rems_delay_event_ids =
          this.investigation.rems_delay_event_ids.map((x) => x.toUpperCase());

        this.controller = new AbortController();

        this.$axios
          .$post(
            "/incident/rems_event_details",
            this.investigation.rems_delay_event_ids,
            {
              signal: this.controller.signal,
            }
          )
          .then((res) => {
            if (!this.controller.signal.aborted) {
              this.investigation.total_event_duration = res.duration;
            } else {
              this.$snackbar.add("Request cancelled", "info");
            }
            this.loading = false;
          })
          .catch((err) => {
            this.cancelRequest();
            console.error(err);
          });
      } else if (
        this.is_aplus &&
        this.investigation.aplus_delay_event_ids.length > 0
      ) {
        this.loading = true;

        this.controller = new AbortController();

        this.investigation.aplus_delay_event_ids =
          this.investigation.aplus_delay_event_ids.filter((x) => x);
        if (this.investigation.aplus_delay_event_ids.length == 0) return;

        this.$axios
          .$post(
            "/incident/aplus_event_details",
            this.investigation.aplus_delay_event_ids,
            {
              signal: this.controller.signal,
            }
          )
          .then((res) => {
            if (!this.controller.signal.aborted) {
              this.investigation.total_tonnes_lost = res.TonnesLoss;
              this.investigation.total_event_duration = res.EventDuration;
              this.investigation.total_effective_duration =
                res.EffectiveDuration;
            } else {
              this.$snackbar.add("Request cancelled", "info");
            }

            this.loading = false;
          })
          .catch((err) => {
            this.cancelRequest();
            console.error(err);
          });
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
