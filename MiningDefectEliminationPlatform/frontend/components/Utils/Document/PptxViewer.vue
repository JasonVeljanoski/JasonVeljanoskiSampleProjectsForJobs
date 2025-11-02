<template>
  <v-card class="docx-viewer-root" max-width="1200" v-bind="$bind.card">
    <div class="button-rack d-flex">
      <v-btn v-if="refreshable" text :disabled="loading" color="white" class="icon" @click="refresh">
        <v-icon left> mdi-refresh </v-icon>
        Refresh
      </v-btn>
      <v-btn
        v-if="downloadable"
        :href="download_source"
        :download="download_name"
        :disabled="loading"
        text
        color="white"
        class="icon"
      >
        <v-icon left> mdi-download </v-icon>
        Download
      </v-btn>
      <v-btn v-if="editable" :disabled="loading" text color="white" class="icon" @click="$emit('edit')">
        <v-icon left> mdi-pencil </v-icon>
        Edit
      </v-btn>
      <v-btn v-if="emailable" :disabled="loading" text color="white" class="icon" @click="handleDistribute">
        <v-icon left> mdi-email </v-icon>
        Distribute
      </v-btn>
      <h2>
        <v-icon color="white" class="mb-1">mdi-microsoft-powerpoint</v-icon>
        {{ title }}
      </h2>
      <v-spacer />
      <upload-custom-flash-report-helper
        v-if="enable_custom_flash_report"
        :disabled="loading"
        :investigation="investigation"
        @loading="loading_pdf = $event"
      />

      <upload-custom-shared-learnings-helper
        v-if="enable_custom_shared_learnings"
        :disabled="loading"
        :investigation="investigation"
        @loading="loading_pdf = $event"
      />
    </div>
    <div v-if="loading || loading_pdf" class="d-flex align-center justify-center">
      <v-progress-circular :size="120" :width="10" indeterminate color="primary" style="min-height: 600px" />
    </div>
    <pptx-previewer v-else :key="renderKey">
      <pdf :src="doc_source" :page="page_no" @num-pages="page_count = $event" @page-loaded="page_no = $event" />
    </pptx-previewer>
    <div class="btn-wrapper">
      <v-pagination
        v-model="page_no"
        :length="page_count"
        :total-visible="10"
        color="orange"
        prev-icon="mdi-chevron-left"
        next-icon="mdi-chevron-right"
      />
    </div>
    <slot />

    <!-- DIALOGS -->
    <email-dialog
      ref="email_dialog"
      :site="investigation && investigation.hasOwnProperty('site') && investigation.site ? investigation.site : ''"
      :department="
        investigation && investigation.hasOwnProperty('department') && investigation.department
          ? investigation.department
          : ''
      "
      :object_type="
        investigation && investigation.hasOwnProperty('object_type') && investigation.object_type
          ? investigation.object_type
          : ''
      "
    />
  </v-card>
</template>

<script>
import pdf from "vue-pdf";
import PptxPreviewer from "@/components/Utils/Document/PptxPreviewer";
import EmailDialog from "@/components/Utils/Document/EmailDialog";
import UploadCustomFlashReportHelper from "@/components/Investigation/FlashReport/UploadCustomHelper.vue";
import UploadCustomSharedLearningsHelper from "@/components/Investigation/SharedLearnings/UploadCustomHelper.vue";

export default {
  components: {
    pdf,
    PptxPreviewer,
    EmailDialog,
    UploadCustomFlashReportHelper,
    UploadCustomSharedLearningsHelper,
  },
  props: {
    investigation: { type: Object },
    download_link: { type: String },
    download_name: { type: String },
    doc_src: { type: String },
    title: {
      type: String,
      required: false,
      default: "",
    },
    refreshable: { type: Boolean },
    downloadable: { type: Boolean },
    editable: { type: Boolean },
    emailable: { type: Boolean },
    loading: { type: Boolean, default: false },
    enable_custom_flash_report: { type: Boolean, default: false },
    enable_custom_shared_learnings: { type: Boolean, default: false },
  },
  // Solve bug in vue-pdf https://github.com/FranckFreiburger/vue-pdf/issues/327
  errorCaptured() {
    return false;
  },
  data() {
    return {
      renderKey: 0,
      page_no: 1,
      page_count: 0,
      loading_pdf: false,
    };
  },
  computed: {
    // render key is required so string changes to trigger vue-pdf
    // to re-request pdf instead of using cached value
    doc_source() {
      return `${this.doc_src}?render_key=${this.renderKey}`;
    },
    download_source() {
      return `${this.download_link}?render_key=${this.renderKey}`;
    },
  },
  watch: {
    page_count() {
      // reset page_no if it exceeds page_count
      if (this.page_no > this.page_count) this.page_no = 1;
    },
  },
  mounted() {
    // trigger vue-pdf to re-request pdf instead of using cached value
    const max = 1024;
    let rand = Math.floor(Math.random() * max);
    if (rand == this.renderKey) this.renderKey = rand + 1;
    else this.renderKey = rand;
  },
  methods: {
    refresh() {
      this.renderKey += 1;
    },
    handleDistribute() {
      this.$refs.email_dialog
        .open()
        .then((res) => {
          // cancel
          if (res == false) return;
          this.$emit("email", res);
        })
        .error((err) => console.error(err))
        .finally((err) => console.error(err));
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.docx-viewer-root {
  margin: auto;
  width: 100%;
  border-radius: 5px;

  .button-rack {
    background-color: var(--v-orange-base);
  }

  .icon {
    z-index: 1;
  }

  h2 {
    width: 100%;
    position: absolute;
    text-align: center;
    color: white;
    font-weight: 400;
    z-index: 0;
  }
}

$header-height: 64px;
$stepper-height: 72px;

.preview-root {
  margin: auto;
  margin-bottom: 130px;
  width: 100%;
  border-radius: 5px;
}
</style>
