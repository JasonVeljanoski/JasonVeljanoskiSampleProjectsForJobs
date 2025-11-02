<template>
  <div ref="five_why" class="root-five-why">
    <!-- CREATE MODE -->
    <div v-if="create_mode">
      <h2>Create your 5-Why Document</h2>
      <the-five-why-analysis
        :investigation="investigation"
        :unfoil="unfoil"
        @submit="createFiveWhy()"
        @save="saveFiveWhy()"
      />
      <!-- Message for user -->
      <div
        v-if="!is_my_investigation && !$perms.is_admin"
        class="d-flex justify-center"
      >
        <v-icon small left>mdi-information</v-icon> You must be an
        &#160;<b>owner</b>&#160;, &#160;<b>supervisor</b>&#160; or
        &#160;<b>admin</b>&#160; to save
      </div>
    </div>

    <!-- PREVIEW MODE -->
    <div class="d-flex justify-center" v-else>
      <docx-viewer
        ref="docx_viewer"
        title="5-Why Document"
        @edit="editFiveWhy()"
        :editable="is_my_investigation || $perms.is_admin"
        :download_link="five_why_download"
        :download_name="download_name"
        :doc_src="five_why_doc"
        :loading="report_loading"
        refreshable
        downloadable
      >
        <action-table-simple
          class="mx-2 my-2"
          type="five_why"
          :report_id="investigation.five_why.id"
          :investigation_id="investigation.id"
          :actions="investigation.five_why.actions"
          @refresh_report="refreshReport"
        />
        <v-btn
          v-if="preview_mode"
          :disabled="
            !is_my_investigation && !$perms.is_admin && !is_new_root_cause
          "
          color="success"
          class="mx-2 my-2"
          @click="$emit('next')"
        >
          <v-icon left>mdi-arrow-down-left-bold</v-icon>
          Root Cause Details
        </v-btn>
      </docx-viewer>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import pdf from "vue-pdf";
import DocxViewer from "@/components/Utils/Document/DocxViewer";
import TheFiveWhyAnalysis from "@/components/FiveWhy/TheFiveWhyAnalysis";
import DocxPreviewer from "@/components/Utils/Document/DocxPreviewer";
import ActionTableSimple from "@/components/Investigation/Actions/ActionsTableSimple";

export default {
  components: {
    pdf,
    DocxViewer,
    TheFiveWhyAnalysis,
    DocxPreviewer,
    ActionTableSimple,
  },
  props: {
    investigation: { Object },
  },
  data() {
    return {
      unfoil: false,
      file_submitted: false,
      report_loading: false,
      preview_mode: false,
      page_no: 1,
      page_count: 0,
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    five_why_doc() {
      const path = this.$enums.document_paths["five_why"];
      const fname = `five_why_${this.investigation.id}.pdf`;
      return this.$document.download(`${path}/${fname}`);
    },
    five_why_download() {
      const path = this.$enums.document_paths["five_why"];
      const fname = `five_why_${this.investigation.id}.docx`;
      return this.$document.download(`${path}/${fname}`);
    },
    // feature: anyone can make a root cause if it is being created for the first time
    //          users can create root cause on behalf of someone else
    is_new_root_cause() {
      return this.investigation.root_cause_detail.id == null;
    },
    create_mode() {
      return (
        (!this.preview_mode && !this.file_submitted && !this.report_loading) ||
        !this.investigation.five_why.is_complete
      );
    },
    download_name() {
      return this.$document.download_name(
        this.investigation.function_location,
        "5-Why",
        this.investigation.id,
        this.investigation.title,
        "docx"
      );
    },
  },
  mounted() {
    // ---------------------------------
    // FETCH EXISTING 5-WHY (IF ANY)
    // ---------------------------------
    const query = this.$route.query;
    if (Object.keys(query).length !== 0) {
      this.$axios
        .$get("/five_why", {
          params: { investigation_id: this.$route.query.id },
        })
        .then((res) => {
          if (res) {
            // populate five-why
            this.investigation.five_why = res;

            if (!this.investigation.five_why.is_complete) {
              this.unfoil = true;
            }

            // preview mode
            this.preview_mode = true;
          }
        })
        .catch((err) => {
          console.error(err);
        });
    }
  },
  methods: {
    editFiveWhy() {
      this.file_submitted = false;
      this.preview_mode = false;
      this.unfoil = true;
    },
    refreshReport() {
      this.$refs.docx_viewer.refresh();
    },
    // -----------------------------
    // PDF
    // -----------------------------
    saveFiveWhy() {
      // set to not complete
      this.investigation.five_why.is_complete = false;

      this.$axios
        .$put("/five_why", this.investigation)
        .then((res) => {
          this.investigation.five_why = res;
        })
        .catch((err) => console.error(err));
    },
    createFiveWhy() {
      this.report_loading = true;
      this.$emit("scroll_up");

      // set to complete
      this.investigation.five_why.is_complete = true;

      this.$axios
        .$put("/five_why", this.investigation)
        .then((res) => {
          this.$document
            .create_five_why_report(this.investigation.id)
            .then(() => {
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

              this.investigation.five_why = res;
              this.report_loading = false;
              this.preview_mode = true;
              this.file_submitted = true;
              this.$emit("preview");
            })
            .catch((err) => {
              console.error(err);
            });
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.root-five-why {
  max-width: 1200px;
  margin: auto;
}
h2 {
  text-align: center;
  color: var(--v-primary-base);
}
</style>
