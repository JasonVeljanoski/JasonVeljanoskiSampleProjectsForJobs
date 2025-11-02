<template>
  <div v-if="investigation.steps_completed >= 2">
    <div v-if="!prev_flash_report" class="scroll-area forgiveness">
      <flash-report-form ref="flash_report_form" :investigation="investigation" @save="flashReportValidation()" />
    </div>
    <div v-else class="scroll-area forgiveness">
      <flash-report-prev
        ref="flash-report-prev"
        :investigation="investigation"
        :loading="loading || update_loading"
        @edit="preview_flashreport = false"
        @save="$emit('scroll_down')"
        @lastPage="$emit('last_page')"
      />
    </div>
  </div>
</template>

<script>
import FlashReportForm from "@/components/Investigation/FlashReport/FlashReportForm";
import FlashReportPrev from "@/components/Investigation/FlashReport/FlashReportPrev";

export default {
  name: "CreateFlashReport",
  components: {
    FlashReportForm,
    FlashReportPrev,
  },
  props: {
    investigation: { type: Object },
    previewMode: { type: Boolean },
    loading: { type: Boolean, default: false },
  },
  data() {
    return {
      update_loading: false,
      preview_flashreport: false,
      preview_init: true,
    };
  },
  computed: {
    prev_flash_report() {
      if (this.previewMode && this.preview_init) {
        this.preview_flashreport = true;
        this.preview_init = false;
      }
      return this.preview_flashreport;
    },
  },
  methods: {
    // -----------------------------
    // PUSH NOTIFICATION
    // -----------------------------
    warningMessage(message) {
      this.$snackbar.add(message, "warning");
    },
    flashReportValidation() {
      if (this.$refs.flash_report_form.$refs.form.validate()) {
        if (this.investigation.flash_report.actions.length == 0) {
          // scroll to top if failed validation
          this.$emit("scroll_up");

          // validation message
          this.warningMessage("You must create at least one action to continue!");
        } else {
          // scroll to top and wait until flash report is generated
          this.$emit("scroll_up");
          this.update_loading = true;
          this.preview_flashreport = true;

          this.$axios
            .$put("/flash_report/create_update", this.investigation.flash_report)
            .then((res) => {
              this.investigation.flash_report = res;

              // create flash report .pptx and pdf
              // this.createFlashReportDoc()
              this.$document
                .create_flash_report(this.investigation.id)
                .then(() => {
                  this.update_loading = false;

                  // ---------------------------------------------

                  if (this.investigation.shared_learning.id) {
                    this.$emit("shared_learning_loading", true);
                    this.$document
                      .create_shared_learnings_report(this.investigation.id)
                      .then(() => {
                        this.$emit("shared_learning_loading", false);
                      })
                      .catch((err) => {
                        console.error(err);
                      });
                  }

                  // ---------------------------------------------

                  const STEPS_COMPLETED = 3;
                  this.$axios
                    .$patch("/investigation/save_steps", null, {
                      params: {
                        investigation_id: this.investigation.id,
                        steps_completed: STEPS_COMPLETED,
                      },
                    })
                    .then(() => {
                      if (this.investigation.steps_completed < STEPS_COMPLETED)
                        this.investigation.steps_completed = STEPS_COMPLETED;
                    })
                    .catch((err) => {
                      console.error(err);
                    });

                  // ---------------------------------------------
                })
                .catch((err) => {
                  console.error(err);
                });
            })
            .catch((err) => {
              console.error(err);
            });
        }
      } else {
        // scroll to top if failed validation
        this.$emit("scroll_up");

        this.warningMessage("Validation failed in at least one field.");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.scroll-area {
  padding-top: calc(#{$stepper-height} + 10px);
  // height: calc(100vh - #{$header-height} - 24px);

  scroll-snap-align: none;
}

.forgiveness {
  padding-bottom: 0px;
}

.title {
  text-align: center;
  width: 100%;
  font-size: 14px !important;
  margin-bottom: -26px;
}

.progress {
  width: 100%;
}

.sticky {
  position: fixed;
  width: 100%;
  top: #{$header-height};
  z-index: 5;
}

.footer {
  margin: 10px;
  position: fixed;
  bottom: 0;
  right: 0;
  background-color: var(--v-primary-base);
}

.stepper {
  cursor: pointer;

  &:hover {
    background-color: rgba(0, 0, 0, 0.03);
  }
}

.modal {
  position: fixed;
  z-index: 10;
  padding-top: 100px;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.25);
  overflow: hidden;
}
</style>
