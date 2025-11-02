<template>
  <div class="flash-report-root">
    <v-card
      v-bind="$bind.card"
      width="1200"
      class="investigation-card ml-auto mr-auto"
    >
      <v-card-title v-if="investigation.flash_report.id">
        Edit Flash Report
      </v-card-title>
      <v-card-title v-else>Create New Flash Report</v-card-title>
      <v-divider />
      <span class="body-wrapper">
        <v-card-text>
          <v-form ref="form" class="root-form-flash-report">
            <h4>Event Title</h4>

            <v-textarea
              ref="fr_title"
              v-model="investigation.flash_report.event_title"
              v-bind="$bind.select"
              :rules="[
                $form.required(investigation.flash_report.event_title),
                $form.length(investigation.flash_report.event_title, 60),
                !limitExceeded('fr_title') || warning_limit_text,
              ]"
              hide-details="auto"
              rows="1"
              counter="60"
              no-resize
              dense
              required
            />

            <div class="grid-box">
              <div class="form-box">
                <h4>Event Description</h4>
                <v-textarea
                  ref="fr_desc"
                  v-model="investigation.flash_report.event_description"
                  v-bind="$bind.textarea"
                  :rules="[
                    $form.required(
                      investigation.flash_report.event_description
                    ),
                    $form.length(
                      investigation.flash_report.event_description,
                      850
                    ),
                    !limitExceeded('fr_desc') || warning_limit_text,
                  ]"
                  hide-details="auto"
                  counter="850"
                  rows="8"
                  no-resize
                  dense
                  required
                  :style="render_styles"
                />

                <h4>Additional / Other Business Impacts</h4>
                <small class="ml-2">(optional)</small>

                <v-textarea
                  ref="fr_business_impact"
                  v-model="investigation.flash_report.business_impact"
                  v-bind="$bind.textarea"
                  :rules="[
                    $form.length(
                      investigation.flash_report.business_impact,
                      150
                    ),
                    !limitExceeded('fr_business_impact') || warning_limit_text,
                  ]"
                  hide-details="auto"
                  counter="150"
                  rows="2"
                  no-resize
                  dense
                  required
                  :style="(render_styles, { width: '810px' })"
                />
                <h4>Immediate Action Taken</h4>
                <v-textarea
                  ref="fr_immediate_action"
                  v-model="investigation.flash_report.immediate_action_taken"
                  v-bind="$bind.textarea"
                  :rules="[
                    $form.required(
                      investigation.flash_report.immediate_action_taken
                    ),
                    $form.length(
                      investigation.flash_report.immediate_action_taken,
                      250
                    ),
                    !limitExceeded('fr_immediate_action') || warning_limit_text,
                  ]"
                  hide-details="auto"
                  counter="250"
                  rows="4"
                  dense
                  no-resize
                  :style="(render_styles, { width: '795px' })"
                />
                <span class="d-flex">
                  <h4>Add Potential Root Cause</h4>
                  <small class="ml-2">(max: 2)</small>
                </span>

                <v-textarea
                  ref="fr_root_cause"
                  v-model="tmp_root_cause"
                  v-bind="$bind.textarea"
                  :rules="[
                    $form.length(tmp_root_cause, 150),
                    $form.arr_len_lim(
                      investigation.flash_report.potential_root_causes,
                      2
                    ),
                    $form.arr_non_empty(
                      investigation.flash_report.potential_root_causes
                    ),
                    !limitExceeded('fr_root_cause') || warning_limit_text,
                  ]"
                  :disabled="
                    investigation.flash_report.potential_root_causes === 2
                  "
                  hide-details="auto"
                  counter="150"
                  rows="2"
                  no-resize
                  dense
                  :style="(render_styles, { width: '795px' })"
                />
                <v-btn
                  :disabled="
                    investigation.flash_report.potential_root_causes.length >=
                      2 ||
                    tmp_root_cause == null ||
                    tmp_root_cause.length > 150
                  "
                  v-bind="$bind.btn"
                  @click="addRootCause()"
                >
                  Add
                </v-btn>
                <ul class="mb-2 ml-n7 mr-n2">
                  <li
                    v-for="(cause, i) in investigation.flash_report
                      .potential_root_causes"
                    :key="i"
                  >
                    <div class="root-cause">
                      <div>
                        {{ cause }}
                      </div>
                      <e-icon-btn @click="removeRootCause(i)" tooltip="Remove">
                        mdi-close
                      </e-icon-btn>
                    </div>
                  </li>
                </ul>
              </div>
              <div class="form-box">
                <div>
                  <h4 style="text-align: center">
                    {{ investigation.site }},{{ investigation.department }},
                    {{ $format.date(investigation.event_datetime) }}
                  </h4>
                  <span class="d-flex">
                    <h4>Images</h4>
                    <small class="ml-2">(required: 1)</small>
                  </span>
                  <image-input
                    :images="investigation.flash_report.files"
                    :img-disabled="investigation.flash_report.files.length >= 1"
                    :img-rules="[
                      $form.arr_fixed_len(investigation.flash_report.files, 1),
                    ]"
                  />
                  <h4 style="text-align: center">
                    {{ investigation.function_location }}
                  </h4>
                  <h4>Equipment:</h4>
                  <h4 style="font-weight: 400">
                    {{ investigation.equipment_description }} ({{
                      investigation.object_type
                    }})
                  </h4>
                  <h4>Object Part:</h4>
                  <h4 style="font-weight: 400">
                    {{ investigation.object_part_description }}
                  </h4>
                  <h4>Damage Code:</h4>
                  <h4 style="font-weight: 400">
                    {{ investigation.damage_code }}
                  </h4>
                </div>
              </div>
            </div>

            <v-divider class="my-2" />

            <div class="grid-box mt-4">
              <div class="form-box">
                <h4>Event Date/Time</h4>
                <e-date-time
                  v-model="investigation.event_datetime"
                  :time="true"
                  v-bind="$bind.textfield"
                  hide-details="auto"
                  disabled
                  dense
                />

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

                <h4>Investigation Type</h4>
                <v-text-field
                  v-bind="$bind.textfield"
                  :value="
                    $enums.investigation_types[investigation.investigation_type]
                  "
                  :rules="[$form.required(investigation.investigation_type)]"
                  hide-details
                  disabled
                  dense
                />
              </div>
              <div class="form-box">
                <h4>
                  Inventory Levels Sufficient to Mitigate other Similar Events?
                </h4>
                <v-radio-group
                  v-model="
                    investigation.flash_report.sufficient_inventory_levels
                  "
                  style="margin: 0"
                >
                  <v-radio :value="true" label="Yes" />
                  <v-radio :value="false" label="No / Unsure" />
                </v-radio-group>
              </div>
            </div>
          </v-form>

          <v-spacer class="my-4" />

          <action-table-simple
            type="flash_report"
            :investigation_id="investigation.id"
            :actions="investigation.flash_report.actions"
            :report_id="investigation.flash_report.id"
          />
        </v-card-text>
      </span>

      <v-divider />
      <v-card-actions>
        <div class="ml-auto mr-auto mt-2" style="width: 1200px">
          <v-btn
            :disabled="
              (!is_my_investigation &&
                !$perms.is_admin &&
                !is_new_flash_report) ||
              loading
            "
            color="success"
            @click="$emit('save')"
          >
            <v-icon>mdi-content-save</v-icon>
            Save Flash Report
          </v-btn>
        </div>

        <!-- Message for user -->
        <div
          v-if="
            !is_my_investigation && !$perms.is_admin && !is_new_flash_report
          "
          class="d-flex justify-center"
        >
          <v-icon small left>mdi-information</v-icon> You must be an
          &#160;<b>owner</b>&#160;, &#160;<b>supervisor</b>&#160; or
          &#160;<b>admin</b>&#160; to save
        </div>
      </v-card-actions>
    </v-card>

    <div ref="solution-scroll" />
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import ImageInput from "@/components/Utils/ImageInput";
import ActionTableSimple from "@/components/Investigation/Actions/ActionsTableSimple";

export default {
  components: {
    ImageInput,
    ActionTableSimple,
  },
  props: {
    investigation: { Object },
  },
  data() {
    return {
      loading: false,
      tmp_root_cause: null,
      window_width: window.innerWidth,
      initial_client_heights: {
        fr_title: 0,
        fr_desc: 0,
        fr_business_impact: 0,
        fr_immediate_action: 0,
        fr_root_cause: 0,
      },
      client_heights: {
        fr_title: 0,
        fr_desc: 0,
        fr_business_impact: 0,
        fr_immediate_action: 0,
        fr_root_cause: 0,
      },
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    is_aplus() {
      return (
        this.investigation &&
        this.investigation.event_type === this.$enums.event_types["APLUS"]
      );
    },
    // feature: anyone can make a flash report if it is being created for the first time
    //          users can create flash reports on behalf of someone else
    is_new_flash_report() {
      return this.investigation.flash_report.id == null;
    },
    render_styles() {
      return { width: "820px", fontSize: "12pt" };
    },
    warning_limit_text() {
      return "Text input number of lines limit exceeded. Generated Flash Report may have overlapping text if not addressed";
    },
  },
  mounted() {
    this.getDefaultFieldHeights();

    this.$nextTick(() => {
      window.addEventListener("resize", this.onResize);
    });
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.onResize);
  },
  methods: {
    // -----------------------------
    // FORM
    // -----------------------------
    onResize() {
      this.window_width = window.innerWidth;
    },
    getDefaultFieldHeights() {
      const fr_title = this.$refs.fr_title.$el.querySelector("textarea");
      const fr_desc = this.$refs.fr_desc.$el.querySelector("textarea");
      const fr_business_impact =
        this.$refs.fr_business_impact.$el.querySelector("textarea");
      const fr_immediate_action =
        this.$refs.fr_immediate_action.$el.querySelector("textarea");
      const fr_root_cause =
        this.$refs.fr_root_cause.$el.querySelector("textarea");

      const ro = new ResizeObserver(() => {
        this.client_heights.fr_title = fr_title.scrollHeight;
        this.client_heights.fr_desc = fr_desc.scrollHeight;
        this.client_heights.fr_business_impact =
          fr_business_impact.scrollHeight;
        this.client_heights.fr_immediate_action =
          fr_immediate_action.scrollHeight;
        this.client_heights.fr_root_cause = fr_root_cause.scrollHeight;
      });

      ro.observe(fr_title);
      ro.observe(fr_desc);
      ro.observe(fr_business_impact);
      ro.observe(fr_immediate_action);
      ro.observe(fr_root_cause);

      // set initial heights
      this.initial_client_heights.fr_title = fr_title.clientHeight;
      this.initial_client_heights.fr_desc = fr_desc.clientHeight;
      this.initial_client_heights.fr_business_impact =
        fr_business_impact.clientHeight;
      this.initial_client_heights.fr_immediate_action =
        fr_immediate_action.clientHeight;
      this.initial_client_heights.fr_root_cause = fr_root_cause.clientHeight;
    },
    limitExceeded(field) {
      // turn-feature off for phone view (as it woint work)
      if (this.window_width > 930)
        return this.client_heights[field] > this.initial_client_heights[field];
      return false;
    },
    updateLoading(flag) {
      this.loading = flag;
    },
    // -----------------------------
    // ROOT CAUSES
    // -----------------------------
    addRootCause() {
      this.investigation.flash_report.potential_root_causes.push(
        this.tmp_root_cause
      );

      // clear
      this.$refs.fr_root_cause.reset();
      this.tmp_root_cause = null;
    },
    removeRootCause(index) {
      this.investigation.flash_report.potential_root_causes.splice(index, 1);
    },
    // -----------------------------
    // EVENTS
    // -----------------------------
    formatTotal(total) {
      if (!total) total = 0;
      return total.toFixed(1);
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.grid-box {
  display: grid;
  gap: 0 26px;
  grid-template-columns: repeat(2, 1fr);
}
.form-box {
  // max-width: 400px;
  width: 100%;
}

.v-textarea {
  * {
    overflow-y: auto;
  }
}

ul,
li {
  list-style-type: none;
}

.root-cause {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border: solid 1px var(--v-accent-base);
  border-radius: 5px;
  margin: 5px;
}
</style>
