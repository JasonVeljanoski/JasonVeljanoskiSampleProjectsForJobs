<template>
  <div :key="renderKey" class="rca-root">
    <docx-viewer
      title="RCA Downloadable Template"
      :download_link="rca_download"
      :download_name="download_name"
      :doc_src="rca_doc"
      refreshable
      downloadable
      @refresh="renderKey += 1"
    />
    <v-btn
      :disabled="!is_my_investigation && !$perms.is_admin && !is_new_root_cause"
      color="success"
      @click="$emit('next')"
    >
      <v-icon left>mdi-arrow-down-left-bold</v-icon>
      Root Cause Details
    </v-btn>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import pdf from "vue-pdf";
import DocxViewer from "@/components/Utils/Document/DocxViewer";

export default {
  props: {
    investigation: { type: Object },
  },
  components: {
    pdf,
    DocxViewer,
  },
  data() {
    return {
      renderKey: 0,
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    rca_doc() {
      const path = this.$enums.document_paths["rca"];
      const fname = `rca_${this.investigation.id}.pdf`;
      return this.$document.download(`${path}/${fname}`);
    },
    rca_download() {
      const path = this.$enums.document_paths["rca"];
      const fname = `rca_${this.investigation.id}.docx`;
      return this.$document.download(`${path}/${fname}`);
    },
    // feature: anyone can make a root cause if it is being created for the first time
    //          users can create root cause on behalf of someone else
    is_new_root_cause() {
      return this.investigation.root_cause_detail.id == null;
    },
    download_name() {
      return this.$document.download_name(
        this.investigation.function_location,
        "RCA",
        this.investigation.id,
        this.investigation.title,
        "docx"
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.rca-root {
  max-width: 1200px;
  margin: auto;
}
</style>
