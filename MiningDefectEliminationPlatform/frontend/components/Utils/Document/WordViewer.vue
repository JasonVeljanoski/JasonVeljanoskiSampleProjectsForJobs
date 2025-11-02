<template>
  <v-card
    :max-width="max_width"
    :elevation="0"
    outlined
    class="ml-auto mr-auto"
  >
    <!-- HEADER BANNER -->
    <v-card-title color="primary">
      <span class="d-flex align-center docx-title">
        <v-icon left class="mb-1">mdi-microsoft-word</v-icon>
        {{ title }}
      </span>

      <v-spacer />

      <template v-for="(item, ii) in banner_items">
        <template v-if="item.visible">
          <v-btn
            v-if="!minimal"
            :disabled="loading"
            :href="item.href"
            text
            @click="item.click"
          >
            <v-icon left>{{ item.icon }}</v-icon>
            {{ item.text }}
          </v-btn>
          <e-icon-btn
            v-else
            :tooltip="item.text"
            :disabled="loading"
            :href="item.href"
            text
            @click="item.click"
          >
            {{ item.icon }}
          </e-icon-btn>
        </template>
      </template>
    </v-card-title>

    <!-- LOADING -->
    <div v-if="loading" class="d-flex align-center justify-center">
      <v-progress-circular
        :size="120"
        :width="10"
        indeterminate
        color="primary"
        style="min-height: 600px"
      />
    </div>

    <!-- DOCX -->
    <div
      v-if="!loading && page_count"
      :key="renderKey"
      :style="{ height: height + 'px' }"
      class="docx-sheets"
    >
      <pdf v-for="i in page_count" :key="i" :src="doc_src" :page="i" />
    </div>

    <!-- FOCUS DIALOG -->
    <v-dialog v-model="dialog" width="600">
      <word-viewer
        :show_refresh="show_refresh"
        :show_download="show_download"
        :download_link="download_link"
        :doc_src="doc_src"
        :max_width="600"
        :loading="loading"
        :title="title"
      />
    </v-dialog>
  </v-card>
</template>

<script>
import pdf from "vue-pdf";

export default {
  name: "word-viewer",
  props: {
    // banner item flags
    show_refresh: { type: Boolean },
    show_download: { type: Boolean },
    show_edit: { type: Boolean },
    show_reupload: { type: Boolean },
    show_focus: { type: Boolean },

    // document
    download_link: { type: String },
    doc_src: { type: String },

    // style
    max_width: { type: Number, default: 1200 },
    minimal: { type: Boolean, default: false },

    // other
    loading: { type: Boolean, default: false },
    title: {
      type: String,
      default: "",
    },
  },
  components: {
    pdf,
  },
  data() {
    return {
      dialog: false,
      renderKey: 0,
      page_no: 1,
      page_count: 0,
      banner_items: [
        {
          visible: this.show_refresh,
          icon: "mdi-refresh",
          text: "Refresh",
          click: () => {
            this.renderKey += 1;
            this.$emit("refresh");
          },
        },
        {
          visible: this.show_download,
          href: this.download_link,
          icon: "mdi-download",
          text: "Download",
          click: () => {},
        },
        {
          visible: this.show_reupload,
          icon: "mdi-upload",
          text: "Upload New",
          click: () => {
            this.$emit("reupload");
          },
        },
        {
          visible: this.show_edit,
          icon: "mdi-pencil",
          text: "Edit",
          click: () => {
            this.$emit("edit");
          },
        },
        {
          visible: this.show_focus,
          icon: "mdi-arrow-expand-all",
          text: "Focus",
          click: () => {
            this.dialog = !this.dialog;
          },
        },
      ],
    };
  },
  computed: {
    height() {
      // A4 aspect ratio - 1:1.4142
      const ratio = 1.4142; // what looks good
      return this.max_width * ratio;
    },
  },
  mounted() {
    this.getPageCount();
  },
  // Solve bug in vue-pdf https://github.com/FranckFreiburger/vue-pdf/issues/327
  errorCaptured() {
    return false;
  },
  methods: {
    getPageCount() {
      //  example from docs: https://github.com/FranckFreiburger/vue-pdf
      if (this.doc_src) {
        const loadingTask = pdf.createLoadingTask(this.doc_src);
        loadingTask.promise.then((pdf) => {
          this.page_count = pdf.numPages;
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.docx-title {
  font-size: 16px;
}
.docx-sheets {
  background: var(--v-accent-base);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 1em;

  > * {
    background: white;
    margin-bottom: 0.5cm;
    box-shadow: 0 0 0.5cm rgba(0, 0, 0, 0.5);
  }
}
</style>
