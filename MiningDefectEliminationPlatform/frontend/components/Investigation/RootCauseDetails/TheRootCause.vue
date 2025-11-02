<template>
  <div>
    <v-card v-bind="$bind.card" width="1200" class="investigation-card ml-auto mr-auto">
      <v-card-title>Root Cause Details</v-card-title>
      <v-divider />
      <span class="body-wrapper">
        <!-- LOADING -->
        <v-card-text>
          <div v-if="loading" class="d-flex align-center justify-center">
            <v-progress-circular :size="120" :width="10" indeterminate color="primary" style="min-height: 600px" />
          </div>

          <template v-else>
            <!-- ROOT CAUSE MAIN AREA -->
            <root-cause-form ref="form" :investigation="investigation" />
            <v-divider class="mt-4" />
            <flow-chart :investigation="investigation" :loading="loading" />

            <!-- ACTIONS -->
            <action-table-simple
              v-if="investigation.investigation_type != 1"
              type="root_cause_detail"
              :investigation_id="investigation.id"
              :actions="investigation.root_cause_detail.actions"
              :report_id="investigation.root_cause_detail.id"
            />

            <v-divider v-if="is_rca" class="my-4" />

            <!-- UPLOAD DOCUMENT SECTION -->
            <word-viewer
              ref="word_viewer"
              v-if="!edit_complete_rca && completed_rca_exists && is_rca"
              title="Completed RCA Document"
              :download_link="rca_download"
              :doc_src="rca_completed_doc"
              :max_width="500"
              show_reupload
              show_download
              show_refresh
              show_focus
              minimal
              @reupload="
                edit_complete_rca = true;
                tmp_doc = null;
              "
            />
            <v-form
              v-show="edit_complete_rca || !completed_rca_exists || !is_rca"
              ref="close_out_form"
              class="close-out-wrapper"
              lazy-validation
            >
              <template v-if="investigation.investigation_type == 2">
                <span class="d-flex">
                  <h4>Upload Completed RCA Document</h4>
                  <small class="ml-2">(This task can be completed later)</small>
                </span>

                <v-file-input
                  v-model="tmp_doc"
                  v-bind="$bind.textfield"
                  single
                  prepend-inner-icon="mdi-attachment"
                  prepend-icon=""
                  accept=".docx, .pdf"
                  @change="validateFileInput"
                />
                <v-btn
                  v-if="completed_rca_exists"
                  :disabled="upload_file_loading"
                  class="my-2"
                  color="success"
                  @click="
                    edit_complete_rca = false;
                    tmp_doc = null;
                  "
                >
                  Preview Existing Doc
                </v-btn>
              </template>
            </v-form>
          </template>
        </v-card-text>
      </span>

      <v-divider />

      <v-card-actions>
        <v-btn :disabled="!is_my_investigation && !$perms.is_admin" color="success" @click="rootCauseValidation">
          <v-icon left>mdi-content-save</v-icon>
          Save Root Cause Details
        </v-btn>
        <div v-if="!is_my_investigation && !$perms.is_admin && !is_new_root_cause" class="ml-4">
          <v-icon small left>mdi-information</v-icon> You must be an &#160;<b>owner</b>&#160;,
          &#160;<b>supervisor</b>&#160; or &#160;<b>admin</b>&#160; to save
        </div>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import DocxViewer from "@/components/Utils/Document/DocxViewer";
import WordViewer from "@/components/Utils/Document/WordViewer";
import pdf from "vue-pdf";
import ImageInput from "@/components/Utils/ImageInput";
import RootCauseForm from "@/components/Investigation/RootCauseDetails/RootCauseForm";
import FlowChart from "@/components/Investigation/RootCauseDetails/FlowChart";
import ActionTableSimple from "@/components/Investigation/Actions/ActionsTableSimple";

export default {
  components: {
    DocxViewer,
    WordViewer,
    pdf,
    ImageInput,
    RootCauseForm,
    FlowChart,
    ActionTableSimple,
  },
  props: {
    investigation: { Object },
  },
  data() {
    return {
      upload_file_loading: false,
      loading: false,
      tmp_doc: null,
      edit_complete_rca: false,
      completed_rca_exists: false,
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    rca_completed_doc() {
      const path = this.$enums.document_paths.rca;
      // we have .docx file name and need .pdf version to preview on frontend
      let fname = this.investigation.root_cause_detail.complete_rca_fname.split(".");

      if (!fname) return null;

      fname.pop();
      fname = fname.join(".") + ".pdf";

      return this.$document.download(`${path}/${fname}`);
    },
    rca_download() {
      const path = this.$enums.document_paths["rca"];
      const fname = this.investigation.root_cause_detail.complete_rca_fname; // `completed_rca_${this.investigation.id}.docx`;

      return this.$document.download(`${path}/${fname}`);
    },
    is_rca() {
      return this.investigation.investigation_type == 2;
    },
    // feature: anyone can make a root cause if it is being created for the first time
    //          users can create root cause on behalf of someone else
    is_new_root_cause() {
      return this.investigation.root_cause_detail.id == null;
    },
  },
  watch: {
    completed_rca_exists(newVal) {
      if (newVal) {
        this.edit_complete_rca = false;
      }
    },
  },
  mounted() {
    this.doesCompleteRcaExist();
  },
  methods: {
    // -----------------------------
    // FILES
    // -----------------------------
    doesCompleteRcaExist() {
      const path = `${this.$enums.document_paths.rca}/${this.investigation.root_cause_detail.complete_rca_fname}`;
      this.$axios.$get(`/document/exists/${path}`).then((res) => {
        this.completed_rca_exists = res;
      });
    },
    validateFileInput() {
      // get file ext (handle no extension file types and other edge cases)
      // src: https://stackoverflow.com/questions/190852/how-can-i-get-file-extensions-with-javascript
      let file_ext = "";
      if (this.tmp_doc) {
        file_ext = this.tmp_doc.name.split(".");
        if (file_ext.length === 1 || (file_ext[0] === "" && file_ext.length === 2)) {
          file_ext = "";
        } else {
          file_ext = file_ext.pop();
        }
      }

      // check file ext
      const whitelist = ["docx", "pdf"];
      if (whitelist.includes(file_ext)) {
        this.$snackbar.add(`${this.tmp_doc.name} is ready to upload`);
      } else {
        this.$nextTick(() => {
          this.tmp_doc = null;
        });

        if (file_ext != "") this.$snackbar.add(`Invalid File Type (${file_ext})\nOnly accepts .docx or .pdf`, "error");
      }
    },
    // -----------------------------
    // RCA DOCUMENT
    // -----------------------------
    uploadRCA() {
      this.upload_file_loading = true;

      // get file ext (handle no extension file types and other edge cases)
      // src: https://stackoverflow.com/questions/190852/how-can-i-get-file-extensions-with-javascript
      let file_ext = "";
      if (this.tmp_doc) {
        file_ext = this.tmp_doc.name.split(".");
        if (file_ext.length === 1 || (file_ext[0] === "" && file_ext.length === 2)) {
          file_ext = "";
        } else {
          file_ext = file_ext.pop();
        }
      }

      // ----------------------------------------

      const form_data = new FormData();
      form_data.append("file", this.tmp_doc);
      form_data.append("old_filename", this.investigation.root_cause_detail.complete_rca_fname);
      form_data.append("root_cause_detail_id", this.investigation.root_cause_detail.id);
      form_data.append("investigation_id", this.investigation.id);

      this.$axios
        .$post("/document/upload_complete_rca", form_data)
        .then((res) => {
          this.investigation.root_cause_detail.complete_rca_fname = res;
          // const filename = `completed_rca_${this.investigation.id}.${file_ext}`;
          const filename = this.investigation.root_cause_detail.complete_rca_fname;
          const path = this.$enums.document_paths["rca"];

          this.$axios
            .$post(`/document/generate_pdf`, null, {
              params: {
                filename: filename,
                document_path: path,
              },
            })
            .then(() => {
              this.upload_file_loading = false;
              this.completed_rca_exists = true;
            })
            .catch((err) => {
              console.error(err);
            });
        })
        .catch((err) => {
          console.error(err);
        });
    },
    // -----------------------------
    // VALIDATE
    // -----------------------------
    rootCauseValidation() {
      if (!this.completed_rca_exists && !this.$refs.close_out_form.validate()) {
        // scroll to top if failed validation
        this.$emit("scroll_up");
        this.$snackbar.add("Validation failed in at least one field.", "warning");
      }
      if (this.$refs.form.$refs.form.validate()) {
        if (this.investigation.root_cause_detail.actions.length == 0 && this.investigation.investigation_type != 1) {
          // scroll to top if failed validation
          this.$emit("scroll_up");

          // validation message
          this.$snackbar.add("You must create at least one action to continue!", "warning");
        } else {
          this.$axios
            .$put("/investigation/create_update/root_cause_detail", this.investigation.root_cause_detail)
            .then((res) => {
              this.investigation.root_cause_detail.id = res.id;
              this.investigation.root_cause_detail.actions = res.actions;

              if (this.tmp_doc) this.uploadRCA();

              // ---------------------------------------------

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

              // ---------------------------------------------

              // steps
              this.$emit("next");
            })
            .catch((err) => {
              console.error(err);
            });
        }
      } else {
        // scroll to top if failed validation
        this.$emit("scroll_up");
        this.$snackbar.add("Validation failed in at least one field.", "warning");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.close-out-wrapper {
  margin: auto;
  max-width: 400px;
}
</style>
