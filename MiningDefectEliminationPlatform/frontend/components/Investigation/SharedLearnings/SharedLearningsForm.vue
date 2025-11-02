<template>
  <v-card
    v-if="investigation.steps_completed >= 0"
    v-bind="$bind.card"
    width="1200"
    class="investigation-card ml-auto mr-auto"
  >
    <v-card-title v-if="investigation.shared_learning.id"> Edit Shared Learnings Report </v-card-title>
    <v-card-title v-else>Create New Shared Learnings Report</v-card-title>
    <v-divider />
    <span class="body-wrapper">
      <v-card-text>
        <v-form ref="form" class="root-form-report">
          <h4>Event Title</h4>
          <v-textarea
            ref="sl_title"
            v-model="investigation.shared_learning.event_title"
            v-bind="$bind.select"
            :rules="[
              $form.required(investigation.shared_learning.event_title),
              $form.length(investigation.shared_learning.event_title, 60),
              !limitExceeded('sl_title') || warning_limit_text,
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
                ref="sl_desc"
                v-model="investigation.shared_learning.event_description"
                v-bind="$bind.textarea"
                :rules="[
                  $form.required(investigation.shared_learning.event_description),
                  $form.length(investigation.shared_learning.event_description, 850),
                  !limitExceeded('sl_desc') || warning_limit_text,
                ]"
                hide-details="auto"
                counter="850"
                rows="7"
                no-resize
                dense
                required
                :style="render_styles"
              />
              <h4>Reason</h4>
              <v-textarea
                ref="sl_reason"
                v-model="investigation.shared_learning.reason"
                v-bind="$bind.textarea"
                :rules="[
                  $form.required(investigation.shared_learning.reason),
                  $form.length(investigation.shared_learning.reason, 250),
                  !limitExceeded('sl_reason') || warning_limit_text,
                ]"
                hide-details="auto"
                counter="250"
                rows="5"
                no-resize
                dense
                required
                :style="render_styles"
              />
            </div>
            <div class="d-flex align-center">
              <div style="max-width: 350px">
                <v-img :src="investigation.flash_report.files[0]" />
                (Flash Report image will render here)
              </div>
            </div>
          </div>
          <div class="form-box">
            <h4>Shared Learnings</h4>
            <small v-if="limitExceeded('sl_shared_learning')" style="color: var(--v-error-base)">
              {{ warning_limit_text }}
            </small>
            <v-textarea
              ref="sl_shared_learning"
              v-model="investigation.shared_learning.shared_learning"
              v-bind="$bind.textarea"
              :rules="[
                $form.required(investigation.shared_learning.shared_learning),
                $form.length(investigation.shared_learning.shared_learning, 250),
                !limitExceeded('sl_shared_learning') || warning_limit_text,
              ]"
              hide-details="auto"
              counter="250"
              rows="5"
              no-resize
              dense
              required
              :style="render_styles"
            />
          </div>

          <v-divider class="my-2" />

          <span class="d-flex">
            <h4>Initiative Image</h4>
            <small class="ml-2">(optional)</small>
          </span>
          <image-input
            :images="investigation.shared_learning.initiative_images"
            :img-disabled="investigation.shared_learning.initiative_images.length >= 1"
          />
        </v-form>
      </v-card-text>
    </span>
    <v-divider />
    <v-card-actions>
      <v-btn
        :disabled="!is_my_investigation && !$perms.is_admin && !is_new_shared_learning"
        v-bind="$bind.btn"
        color="success"
        style="width: 250px"
        @click="save"
      >
        <v-icon left>mdi-content-save</v-icon>
        Save Shared Learnings
      </v-btn>
      <!-- Message for user -->
      <div v-if="!is_my_investigation && !$perms.is_admin && !is_new_shared_learning" class="ml-4">
        <v-icon small left>mdi-information</v-icon> You must be an &#160;<b>owner</b>&#160;,
        &#160;<b>supervisor</b>&#160; or &#160;<b>admin</b>&#160; to save
      </div>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";
import ImageInput from "@/components/Utils/ImageInput";

export default {
  components: {
    ImageInput,
  },
  props: {
    investigation: { Object },
  },
  data() {
    return {
      window_width: window.innerWidth,
      initial_client_heights: {
        sl_title: 0,
        sl_desc: 0,
        sl_reason: 0,
        sl_shared_learning: 0,
      },
      client_heights: {
        sl_title: 0,
        sl_desc: 0,
        sl_reason: 0,
        sl_shared_learning: 0,
      },
    };
  },
  mounted() {
    if (!this.investigation.shared_learning.event_title) {
      this.investigation.shared_learning.event_title = this.investigation.flash_report.event_title;
    }
    if (!this.investigation.shared_learning.event_description) {
      this.investigation.shared_learning.event_description = this.investigation.flash_report.event_description;
    }

    this.getDefaultFieldHeights();

    this.$nextTick(() => {
      window.addEventListener("resize", this.onResize);
    });
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.onResize);
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    render_styles() {
      return { width: "790px", fontSize: "12pt" };
    },
    warning_limit_text() {
      return "Text input number of lines limit exceeded. Generated Shared Learnings document may have overlapping text if not addressed";
    },
  },
  methods: {
    save() {
      if (this.$refs.form.validate()) {
        this.$emit("save");
      }
    },
    // feature: anyone can make a root cause if it is being created for the first time
    //          users can create root cause on behalf of someone else
    is_new_shared_learning() {
      return this.investigation.shared_learning.id == null;
    },
    // -----------------------------
    // FORM
    // -----------------------------
    onResize() {
      this.window_width = window.innerWidth;
    },
    getDefaultFieldHeights() {
      const sl_title = this.$refs.sl_title.$el.querySelector("textarea");
      const sl_desc = this.$refs.sl_desc.$el.querySelector("textarea");
      const sl_reason = this.$refs.sl_reason.$el.querySelector("textarea");
      const sl_shared_learning = this.$refs.sl_shared_learning.$el.querySelector("textarea");

      const ro = new ResizeObserver(() => {
        this.client_heights.sl_title = sl_title.scrollHeight;
        this.client_heights.sl_desc = sl_desc.scrollHeight;
        this.client_heights.sl_reason = sl_reason.scrollHeight;
        this.client_heights.sl_shared_learning = sl_shared_learning.scrollHeight;
      });

      ro.observe(sl_title);
      ro.observe(sl_desc);
      ro.observe(sl_reason);
      ro.observe(sl_shared_learning);

      // set initial heights
      this.initial_client_heights.sl_title = sl_title.clientHeight;
      this.initial_client_heights.sl_desc = sl_desc.clientHeight;
      this.initial_client_heights.sl_reason = sl_reason.clientHeight;
      this.initial_client_heights.sl_shared_learning = sl_shared_learning.clientHeight;
    },
    limitExceeded(field) {
      if (this.window_width > 930) return this.client_heights[field] > this.initial_client_heights[field];
      return false;
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.root-form-report {
  display: grid;
  gap: 0 32px;
  grid-template-columns: repeat(1, 1fr);
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

.grid-box {
  display: grid;
  gap: 0 26px;
  grid-template-columns: repeat(2, 1fr);
}
</style>
