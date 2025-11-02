<template>
  <v-form ref="form" class="root-cause-details" lazy-validation>
    <div class="form-box">
      <h4>Cause</h4>
      <v-autocomplete
        v-model="investigation.root_cause_detail.cause_code"
        v-bind="$bind.select"
        :items="filtered_cause_codes"
        :rules="[$form.required(investigation.root_cause_detail.cause_code)]"
        required
        dense
        hide-details="auto"
      />
      <h4>Failure Category</h4>
      <v-textarea
        v-model="investigation.root_cause_detail.cause_category"
        v-bind="$bind.select"
        :rules="[$form.required(investigation.root_cause_detail.cause_category)]"
        hide-details="auto"
        rows="1"
        disabled
        no-resize
        dense
        required
      />
    </div>
    <div class="form-box">
      <h4>Root Cause Description</h4>
      <v-textarea
        v-model="investigation.root_cause_detail.description"
        v-bind="$bind.select"
        :rules="[$form.required(investigation.root_cause_detail.description)]"
        hide-details="auto"
        rows="6"
        dense
        required
      />
    </div>
    <div class="form-box">
      <h4>Additional Contributing Factors</h4>
      <v-textarea
        v-model="investigation.root_cause_detail.additional_contribution_factors"
        v-bind="$bind.textarea"
        :rules="[$form.required(investigation.root_cause_detail.additional_contribution_factors)]"
        hide-details="auto"
        rows="6"
        dense
        required
      />
    </div>
  </v-form>
</template>

<script>
export default {
  props: {
    investigation: { Object },
  },
  data() {
    return {
      filtered_cause_codes: [],
    };
  },
  mounted() {
    this.getCauses();

    this.investigation.root_cause_detail.investigation_id = this.investigation.id;
  },
  methods: {
    getCauses() {
      // check if catalog_profiles is populated. i.e. another object type has been selected
      let items = [];
      if (this.investigation.catalog_profiles.length > 0) {
        items = this.investigation.catalog_profiles;
      } else {
        const function_location = this.investigation.catalog_profile;
        const equipment_description = this.investigation.equipment_description;
        if (function_location == null || equipment_description == null) return;
        items = [this.investigation.catalog_profile];
      }

      this.$axios
        .$post("/incident/causes_by_catalog_profiles", items)
        .then((res) => {
          this.filtered_cause_codes = res;
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.root-cause-details {
  display: grid;
  gap: 0 26px;
  grid-template-columns: repeat(3, 1fr);
}

.form-box {
  max-width: 400px;
  width: 100%;
}

.v-textarea {
  * {
    overflow-y: auto;
  }
}

h3 {
  color: var(--v-primary-base);
  margin-bottom: 5px;
  font-weight: 400;
}
</style>
