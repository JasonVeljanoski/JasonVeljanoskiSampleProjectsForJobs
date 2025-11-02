<template>
  <v-card class="main-wrapper-docx">
    <v-card class="docx-viewer-root" max-width="1200" v-bind="$bind.card">
      <div class="button-rack d-flex">
        <v-btn
          v-if="refreshable"
          :disabled="loading"
          text
          color="white"
          class="icon"
          @click="
            refresh();
            $emit('refresh');
          "
        >
          <v-icon left> mdi-refresh </v-icon>
          Refresh
        </v-btn>
        <v-btn
          v-if="downloadable"
          :href="download_source"
          :download="download_name"
          :disabled="loading"
          text
          target="_blank"
          color="white"
          class="icon"
        >
          <v-icon left> mdi-download </v-icon>
          Download
        </v-btn>
        <v-btn v-if="editable" :disabled="loading" text color="white" class="icon" @click="$emit('edit')">
          <v-icon left> mdi-pencil </v-icon>
          {{ title == "RCA Downloadable Template" ? "Upload New" : "EDIT" }}
        </v-btn>
        <v-btn v-if="reuploadable" :disabled="loading" text color="white" class="icon" @click="$emit('reupload')">
          <v-icon left> mdi-upload </v-icon>
          Upload New
        </v-btn>
        <h2>
          <v-icon color="white" class="mb-1">mdi-microsoft-word</v-icon>
          {{ title }}
        </h2>
      </div>
      <div v-if="loading" class="d-flex align-center justify-center">
        <v-progress-circular :size="120" :width="10" indeterminate color="primary" style="min-height: 600px" />
      </div>
      <template v-else>
        <docx-previewer v-if="show_document" :key="renderKey">
          <pdf v-for="i in page_count" :key="i" :src="doc_source" :page="i" />
        </docx-previewer>
      </template>
    </v-card>
    <slot />
  </v-card>
</template>

<script>
import pdf from "vue-pdf";
import DocxPreviewer from "@/components/Utils/Document/DocxPreviewer";

export default {
  props: {
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
    reuploadable: { type: Boolean },
    loading: { type: Boolean, default: false },
  },
  components: {
    pdf,
    DocxPreviewer,
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
      show_document: false,
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
    loading() {
      if (!this.loading) {
        this.getPageCount();
      }
    },
  },
  mounted() {
    // trigger vue-pdf to re-request pdf instead of using cached value
    const max = 1024;
    let rand = Math.floor(Math.random() * max);
    if (rand == this.renderKey) this.renderKey = rand + 1;
    else this.renderKey = rand;

    this.getPageCount();
  },
  methods: {
    getPageCount() {
      //  example from docs: https://github.com/FranckFreiburger/vue-pdf
      if (this.doc_source) {
        const loadingTask = pdf.createLoadingTask(this.doc_source);

        loadingTask.promise
          .then((pdf) => {
            this.page_count = pdf.numPages;
            this.show_document = true;
          })
          .catch(() => {
            // try one more time...
            loadingTask.promise
              .then((pdf) => {
                this.page_count = pdf.numPages;
                this.show_document = true;
              })
              .catch((err) => {
                console.error(err);
              });
          });
      }
    },
    refresh() {
      this.renderKey += 1;
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.main-wrapper-docx {
  max-width: 1200px;
  width: 100%;
}

.docx-viewer-root {
  margin: auto;
  width: 100%;
  // height: calc(100vh - #{$header-height} - #{$stepper-height} - 80px);
  border-radius: 5px;

  .button-rack {
    background-color: var(--v-primary-base);
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
</style>
