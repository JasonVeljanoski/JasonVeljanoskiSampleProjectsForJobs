<template>
  <v-card
    v-if="investigation.steps_completed >= 0"
    v-bind="$bind.card"
    width="1200"
    class="investigation-card ml-auto mr-auto"
  >
    <v-card-title>Create New Investigation</v-card-title>
    <v-divider />
    <span class="body-wrapper">
      <v-card-text>
        <div v-if="loading" class="d-flex align-center justify-center">
          <v-progress-circular
            :size="120"
            :width="10"
            indeterminate
            color="primary"
            style="min-height: 600px"
          />
        </div>
        <create-investigation-form
          v-show="!loading"
          ref="new_investigation_form"
          :investigation="investigation"
          @save="createInvestigationValidation"
        />
      </v-card-text>
    </span>
    <v-divider />
    <v-card-actions>
      <e-btn
        v-if="!is_new_investigation"
        :disabled="
          loading || (!is_owner_supervisor_or_admin && !is_new_investigation)
        "
        class="mt-2"
        color="success"
        @click="triggerSave(true)"
      >
        <v-icon left>mdi-content-save</v-icon>
        Save Investigation
      </e-btn>
      <e-btn
        :disabled="
          loading || (!is_owner_supervisor_or_admin && !is_new_investigation)
        "
        class="mt-2"
        color="success"
        tooltip="Owners and Supervisors will receive an email"
        @click="triggerSave"
        :outlined="!is_new_investigation"
      >
        <v-icon left>mdi-content-save-move</v-icon>
        Save & Email
      </e-btn>

      <!-- Message for user -->
      <div
        v-if="!is_owner_supervisor_or_admin && !is_new_investigation"
        class="ml-4"
      >
        <v-icon small left>mdi-information</v-icon> You must be an
        &#160;<b>owner</b>&#160;, &#160;<b>supervisor</b>&#160; or
        &#160;<b>admin</b>&#160; to save
      </div>
    </v-card-actions>
  </v-card>
</template>

<script>
import CreateInvestigationForm from "@/components/Investigation/Investigation/CreateInvestigation/CreateInvestigationForm";

export default {
  name: "CreateInvestigation",
  components: {
    CreateInvestigationForm,
  },
  props: {
    investigation: { type: Object },
  },
  data() {
    return {
      loading: false,
      rems_item: null,
    };
  },
  computed: {
    current_step() {
      return this.investigation.steps_completed + 1;
    },
    // --------------------
    // FLAGS
    // --------------------
    is_new_investigation() {
      return this.investigation.id == null;
    },
    is_owner_supervisor_or_admin() {
      // admins can edit anything
      if (this.$perms.is_admin) return true;

      // owners and supervisor logic
      const uid = this.$auth.user.id;
      const res =
        this.investigation.owner_ids.includes(uid) ||
        uid === this.investigation.supervisor_id;

      this.$store.dispatch("user/changeIsMyInvestigation", res);

      return res;
    },
  },
  methods: {
    // -----------------------------
    // SUB-COMPONENT
    // -----------------------------
    triggerSave(noEmail = false) {
      this.$refs.new_investigation_form.emitSave(noEmail);
    },
    // -----------------------------
    // DOCUMENT
    // -----------------------------
    createRcaPDF() {
      const filename = `rca_${this.investigation.id}.docx`;
      const path = this.$enums.document_paths["rca"];

      this.$axios
        .$post(`/document/generate_pdf`, null, {
          params: {
            filename: filename,
            document_path: path,
          },
        })
        .then(() => {})
        .catch((err) => {
          console.error(err);
        });
    },
    createRcaDoc() {
      let fname = `rca_${this.investigation.id}.docx`;
      this.$axios
        .$post("/document/create_rca", null, {
          params: {
            filename: fname,
            site: this.investigation.site,
            department: this.investigation.department,
          },
        })
        .then(() => {
          this.createRcaPDF();
        })
        .catch((err) => {
          console.error(err);
        });
    },
    doesCompleteRcaExist() {
      const path = `${this.$enums.document_paths.rca}/${this.investigation.root_cause_detail.complete_rca_fname}`;
      return this.$axios.$get(`/document/exists/${path}`).then((res) => {
        return res;
      });
    },
    // -----------------------------
    // FLASH REPORT
    // -----------------------------
    initFlashReportFormValues() {
      // investigation id should always exist
      // that is to say that you must create an investigation before you get here
      this.investigation.flash_report.investigation_id = this.investigation.id;

      // -----------------------------
      // POPULATE WHAT YOU CAN FROM PREV FORMS
      // only if null (you do NOT want to overwrite existing work!)
      // -----------------------------

      // title
      if (this.investigation.flash_report.event_title == null) {
        this.investigation.flash_report.event_title = this.investigation.title;
      }

      let total_effective_duration =
        this.investigation.total_effective_duration || 0.0;
      if (total_effective_duration)
        total_effective_duration = total_effective_duration.toFixed(1);
      else total_effective_duration = 0.0;
      let total_tonnes_lost = this.investigation.total_tonnes_lost || 0.0;
      if (total_tonnes_lost) total_tonnes_lost = total_tonnes_lost.toFixed(1);
      else total_tonnes_lost = 0.0;

      // description
      const flash_rep_description =
        this.investigation.flash_report.event_description;
      if (!flash_rep_description) {
        const description = `At ${this.$format.time(
          this.investigation.event_datetime
        )} on ${this.$format.date(this.investigation.event_datetime)}, ${
          this.investigation.description
        }. Event had an Effective Duration of ${total_effective_duration} hours and ${total_tonnes_lost} tonnes. `;
        this.investigation.flash_report.event_description = description;
      }
    },
    // -----------------------------
    // VALIDATION HELPERS
    // -----------------------------
    async checkIfInvestigationExist(value) {
      const url = "/snowflake/check_event_ids";
      await this.$axios.$post(url, value).then(async (res) => {
        if (res.length > 0) {
          let error_text = `The event id${res.length > 1 ? "s" : ""} ${res.join(
            ", "
          )} already ${
            res.length > 1 ? "have" : "has"
          } an investigation. Please remove ${
            res.length > 1 ? "them" : "it"
          } from your Delayed Accounting Event list.`;

          this.$snackbar.add(error_text, "warning", 7);

          // set error
          return false;
        } else {
          // no error
          return true;
        }
      });
    },
    async createInvestigationValidation(payload) {
      // let aplus_delay_event_ids = payload.investigation.aplus_delay_event_ids;

      if (
        this.investigation.date_closed == null &&
        this.investigation.status == 3
      ) {
        this.$snackbar.add(
          "You must populate the Date Closed field for Closed investigations",
          "warning"
        );
      } else if (this.$refs.new_investigation_form.$refs.form.validate()) {
        this.loading = true;

        // ---------------------------

        const form_data = new FormData();

        // ---------------------------
        // handle attachments + its metadata (sending attachments through pydantic sucks...)

        const attachments = payload.attachments;
        let files_metadatas = [];
        for (let attachment of attachments) {
          files_metadatas.push({
            title: attachment.title,
            description: attachment.description,
            network_drive_link: attachment.network_drive_link,
          });

          form_data.append("files", attachment.file);
        }

        let investigation = payload.investigation;
        investigation.genertal_attachments_metas = files_metadatas;
        form_data.append("investigation", JSON.stringify(investigation));

        // ----------------------------

        if (
          this.investigation.investigation_type == 2 &&
          this.investigation.status == 3
        ) {
          const does_completed_rca_exist = await this.doesCompleteRcaExist();
          if (!does_completed_rca_exist) {
            this.$snackbar.add(
              "You must upload a completed RCA document before you can close an investigation",
              "warning"
            );
            this.loading = false;
            return;
          }
        }

        // ----------------------------

        this.$axios
          .$put("/investigation/create_update", form_data)
          .then(async (res) => {
            this.investigation.id = res.id;
            this.investigation.created = res.created;
            this.investigation.updated = res.updated;
            this.investigation.general_attachments = res.general_attachments;

            this.initFlashReportFormValues();

            if (this.investigation.investigation_type == 2) {
              await this.createRcaDoc();

              // delete five why and its actions (if exists)
              if (this.investigation?.five_why?.id)
                this.$axios
                  .$delete("/five_why", {
                    params: {
                      id: this.investigation.five_why.id,
                    },
                  })
                  .catch((err) => console.error(err));
            } else if (this.investigation.investigation_type == 1) {
              this.investigation.five_why.event_datetime =
                this.investigation.event_datetime;
            }

            // --------------------------------------------------

            // recreate flash report in case delay event metrics have changed in create investigation form
            if (this.investigation.flash_report.id) {
              this.$emit("flash_report_loading", true);
              this.$document
                .create_flash_report(this.investigation.id)
                .then(() => {
                  this.$emit("flash_report_loading", false);
                })
                .catch((err) => {
                  console.error(err);
                });
            }

            // --------------------------------------------------

            if (this.investigation.shared_learning.id) {
              this.$emit("shared_learning_loading", true);
              this.$document
                .create_shared_learnings_report(this.investigation.id)
                .then(() => {
                  this.loading = false;
                  this.$emit("shared_learning_loading", false);
                })
                .catch((err) => {
                  console.error(err);
                });
            } else {
              this.loading = false;
            }

            // --------------------------------------------------

            if (this.$nuxt.$route.name === "investigation") {
              // next page
              this.$emit("scroll_down");

              // update router with ?id=investigation_id
              this.$router.push({
                path: "/investigation",
                query: { id: this.investigation.id },
              });
            }

            // --------------------------------------------------

            // emit
            this.$emit("created");

            // ---------------------------------------------

            const STEPS_COMPLETED = 1;
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
      } else {
        // scroll to top if failed validation
        this.$emit("scroll_up");

        const message = "Validation failed in at least one field.";
        this.$snackbar.add(message, "warning");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

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

.investigation-card {
  margin-top: calc(#{$stepper-height} + 10px);
}
</style>
