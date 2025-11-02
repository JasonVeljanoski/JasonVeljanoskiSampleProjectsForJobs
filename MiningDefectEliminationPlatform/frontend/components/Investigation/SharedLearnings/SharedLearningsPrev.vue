<template>
  <div class="sharedlearning-preview-root">
    <pptx-viewer
      title="Shared Learnings"
      @edit="$emit('edit')"
      :download_link="shared_learnings_download"
      :download_name="download_name"
      :editable="is_my_investigation || $perms.is_admin"
      :doc_src="shared_learnings_doc"
      :loading="loading"
      downloadable
      refreshable
      emailable
      enable_custom_shared_learnings
      :investigation="investigation"
      @email="handleEmail"
    />
    <v-btn
      :disabled="(!is_my_investigation || loading) && !$perms.is_admin"
      class="button-wrapper"
      color="success"
      @click="
        $router.push({
          name: 'investigations',
        })
      "
    >
      <v-icon left>mdi-home</v-icon>
      Redirect Home
    </v-btn>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import PptxViewer from "@/components/Utils/Document/PptxViewer";

export default {
  components: {
    PptxViewer,
  },
  props: {
    investigation: { Object },
    download_name: { String },
    loading: { type: Boolean, default: false },
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    pdf_path() {
      const path = this.$enums.document_paths["shared_learnings"];
      let fname = `shared_learnings_${this.investigation.id}.pdf`;

      if (this.investigation.shared_learning.use_custom_report) {
        fname = this.investigation.shared_learning.custom_report_fname;
      }

      return `${path}/${fname}`;
    },
    pptx_path() {
      let path = this.$enums.document_paths["shared_learnings"];
      let fname = `shared_learnings_${this.investigation.id}.pptx`;

      if (this.investigation.shared_learning.use_custom_report) {
        fname = this.investigation.shared_learning.custom_report_fname;
        if (!fname) return;
        fname = fname.split(".")[0];
        fname += ".pptx";

        // ----

        path = this.$enums.document_paths["general_attachments"];
      }

      return `${path}/${fname}`;
    },
    shared_learnings_doc() {
      return this.$document.download(this.pdf_path);
    },
    shared_learnings_download() {
      return this.$document.download(this.pptx_path);
    },
  },
  methods: {
    // ------------------------------------
    // EMAIL DISTRIBUTION
    // ------------------------------------
    handleEmail(email) {
      // email path depends on whether the user is using a custom report or not
      email.path = `${this.$enums.document_paths.shared_learnings}/shared_learnings_${this.investigation.id}.pptx`;
      if (this.investigation.shared_learning.use_custom_report) {
        email.path = this.$enums.document_paths.general_attachments;

        // replace pdf extension with pptx
        let custom_fname = this.investigation.shared_learning.custom_report_fname.split(".")[0];
        custom_fname += ".pptx";
        email.path += `/${custom_fname}`;
      }

      // ------------------------------------

      const users = email.users;
      this.$axios
        .$post("/email/broadcast_shared_learnings", {
          shared_learnings_id: this.investigation.shared_learning.id,
          path: email.path,
          message: email.message,
          site: this.investigation.site,
          department: this.investigation.department,
          object_type: this.investigation.object_type,
          extra_emails: [...users, ...email.dist_emails],
          download_name: this.download_name,
        })
        .then(() => this.$snackbar.add("Distributing emails..."))
        .catch((err) => console.error(err));
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.sharedlearning-preview-root {
  margin: auto;
  max-width: 1200px;
}

.button-wrapper {
  margin-top: -70px;
  margin-left: 5px;
}
</style>
