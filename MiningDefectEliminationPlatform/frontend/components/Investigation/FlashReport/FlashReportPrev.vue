<template>
  <div class="flashreport-preview-root">
    <pptx-viewer
      ref="flash_report_pptx"
      title="Flash Report"
      @edit="$emit('edit')"
      :download_link="flash_report_download"
      :download_name="download_name"
      :editable="is_my_investigation || $perms.is_admin"
      :doc_src="flash_report_doc"
      :loading="loading"
      downloadable
      refreshable
      emailable
      :investigation="investigation"
      @email="handleEmail"
    >
      <!-- ACTION -->
      <action-table-simple
        class="mx-2"
        type="flash_report"
        :report_id="investigation.flash_report.id"
        :investigation_id="investigation.id"
        :actions="investigation.flash_report.actions"
        @refresh_report="refreshReport"
      />

      <v-btn
        v-if="!is_flash_report_only"
        :disabled="!is_my_investigation && !$perms.is_admin && !is_new_five_why"
        class="my-2 mx-2"
        color="success"
        @click="$emit('save')"
      >
        <v-icon left>mdi-arrow-down-left-bold</v-icon>
        Conduct Analysis
      </v-btn>
      <v-btn
        v-else
        :disabled="(!is_my_investigation || loading) && !$perms.is_admin"
        class="my-2 mx-2"
        color="success"
        @click="$emit('lastPage')"
      >
        <v-icon left>mdi-home</v-icon>
        Redirect Home
      </v-btn>
    </pptx-viewer>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import PptxViewer from "@/components/Utils/Document/PptxViewer";
import ActionTableSimple from "@/components/Investigation/Actions/ActionsTableSimple";

export default {
  components: {
    PptxViewer,
    ActionTableSimple,
  },
  props: {
    investigation: { Object },
    loading: { type: Boolean, default: false },
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
      email_lists: "lists/getEmailLists",
    }),
    // feature: anyone can make a five why if it is being created for the first time
    //          users can create five whys on behalf of someone else
    is_new_five_why() {
      return this.investigation.five_why.id == null;
    },
    is_flash_report_only() {
      return this.investigation.investigation_type == 3;
    },
    used_report_path() {
      let fname = `flash_report_${this.investigation.id}.pdf`;
      if (this.investigation.flash_report.use_custom_report) {
        fname = this.investigation.flash_report.custom_report_fname;
      }

      const path = this.$enums.document_paths["flash_report"];
      return `${path}/${fname}`;
    },
    flash_report_doc() {
      return this.$document.download(this.used_report_path);
    },
    flash_report_download() {
      let fname = `flash_report_${this.investigation.id}.pptx`;
      let path = this.$enums.document_paths["flash_report"];
      if (this.investigation.flash_report.use_custom_report) {
        fname = this.investigation.flash_report.custom_report_fname;
        if (!fname) return;
        fname = fname.split(".")[0];
        fname += ".pptx";

        // ----

        path = this.$enums.document_paths["general_attachments"];
      }

      return this.$document.download(`${path}/${fname}`);
    },
    download_name() {
      return this.$document.download_name(
        this.investigation.function_location,
        "Flash_Report",
        this.investigation.id,
        this.investigation.title
      );
    },
  },
  methods: {
    // ------------------------------------
    // REPORT
    // ------------------------------------
    refreshReport() {
      this.$refs.flash_report_pptx.refresh();
    },
    // ------------------------------------
    // EMAIL DISTRIBUTION
    // ------------------------------------
    handleEmail(email) {
      email.path = `${this.$enums.document_paths.flash_report}/flash_report_${this.investigation.id}.pptx`;
      const users = email.users;
      this.$axios
        .$post("/email/broadcast_flash_report", {
          flash_report_id: this.investigation.flash_report.id,
          path: email.path,
          message: email.message,
          site: this.investigation.site,
          department: this.investigation.department,
          object_type: this.investigation.object_type,
          extra_emails: [...users, ...email.dist_emails],
          download_name: this.download_name,
        })
        .then(() => this.$snackbar.add(`Distributing emails...`))
        .catch((err) => console.error(err));
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.flashreport-preview-root {
  margin: auto;
  max-width: 1200px;
}
</style>
