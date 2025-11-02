<template>
  <v-menu v-model="menu" offset-y min-width="200" :close-on-content-click="false" left>
    <template #activator="{ on, attrs }">
      <v-btn v-bind="attrs" v-on="on" text color="white" :disabled="disabled" tooltip="Upload Custom Document">
        <v-icon left> mdi-upload </v-icon>
        Upload
      </v-btn>
    </template>
    <v-card dense outlined min-width="400">
      <v-card-title>
        <v-checkbox
          v-model="investigation.shared_learning.use_custom_report"
          :disabled="loading || non_deleted_attachment_metadata.length === 0"
          label="Use as Displayed Report"
          class="mt-0 pt-0 mr-4"
          hide-details="auto"
          @change="updateSelected"
        />
        <v-spacer />

        <v-btn v-bind="$bind.btn" :disabled="loading" @click="openFileUploader">
          <v-icon left>mdi-upload</v-icon>{{ upload_text }}
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-card v-if="non_deleted_attachment_metadata.length" elevation="0">
          <e-data-table
            :headers="headers"
            :items="non_deleted_attachment_metadata"
            hide-default-header
            hide-default-footer
          >
            <template #item.action="{ item }">
              <div class="d-flex">
                <e-icon-btn
                  tooltip="Download"
                  :href="$document.download(getFilePath(item))"
                  :disabled="!item.id || loading"
                  target="_blank"
                  small
                >
                  mdi-download
                </e-icon-btn>
                <e-icon-btn
                  small
                  :disabled="!item.id || loading"
                  tooltip="Remove"
                  @click="removeAttachmentProcess(item)"
                >
                  mdi-delete
                </e-icon-btn>
              </div>
            </template>
          </e-data-table>
        </v-card>
        <span v-else>No custom documents.</span>
      </v-card-text>
    </v-card>

    <!-- DIALOG -->
    <e-attachment-uploader ref="uploader" accept=".pptx" hide_form />
  </v-menu>
</template>

<script>
export default {
  props: {
    investigation: {
      type: Object,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      menu: false,
      attachment_metadata: [],
      loading: false,
      headers: [
        { text: "File Name", value: "filename", cellClass: "nowarap" },
        {
          text: "Uploaded By",
          value: "uploaded_by",
          width: "10",
          formatter: (x) => this.$utils.getUserName(x),
        },
        {
          text: "Upload Date",
          value: "created",
          width: "10",
          formatter: (x) => this.$format.date(x),
        },
        {
          text: "Action",
          value: "action",
          width: "10",
          sortable: false,
          align: "center",
          cellClass: "nowarap",
        },
      ],
    };
  },
  computed: {
    non_deleted_attachment_metadata() {
      return this.attachment_metadata.filter((x) => !x.deleted);
    },
    upload_text() {
      return this.non_deleted_attachment_metadata.length ? "Replace" : "Upload";
    },
  },
  mounted() {
    this.getAllAttachements();
  },
  methods: {
    open() {
      this.menu = true;
    },
    getFilePath(attachment) {
      return `${this.$enums.document_paths["general_attachments"]}/${attachment.unique_filename}`;
    },
    openFileUploader() {
      this.$refs.uploader.open().then((res) => {
        if (!res) return;
        this.handleNewAttachment(res);
      });
    },
    handleNewAttachment(attachment) {
      const form_data = new FormData();

      const files_metadata = {
        title: attachment.title,
        description: attachment.description,
        network_drive_link: attachment.network_drive_link,
      };
      form_data.append("metadata", JSON.stringify(files_metadata));
      form_data.append("attachment", attachment.file);

      // ----------------------------

      this.$axios
        .$post("/shared_learning/upload", form_data, {
          params: {
            shared_learning_id: this.investigation.shared_learning.id,
          },
        })
        .then((res) => {
          this.removeAll();
          this.attachment_metadata.push(res);
        })
        .catch((err) => {
          console.error(err);
        });
    },
    removeAll() {
      for (let i = 0; i < this.attachment_metadata.length; i++) {
        if (!this.attachment_metadata[i].deleted) {
          this.removeAttachment(this.attachment_metadata[i]);
        }

        this.investigation.shared_learning.use_custom_report = false;
      }
    },
    removeAttachmentProcess(attachment) {
      if (!confirm("Are you sure you want to remove this attachment?")) {
        return;
      }

      this.removeAttachment(attachment);
    },
    removeAttachment(attachment) {
      const path = this.getFilePath(attachment);

      this.$axios
        .$post(`document/remove/${path}`, null, {
          params: {
            attachment_id: attachment.id,
          },
        })
        .then(() => {
          this.updateSelected(false);
          const idx = this.attachment_metadata.findIndex((x) => x.id == attachment.id);
          this.attachment_metadata.splice(idx, 1);
        })
        .catch((err) => console.error(err));
    },
    getAllAttachements() {
      this.$axios
        .$get("/shared_learning/attachments", {
          params: {
            shared_learning_id: this.investigation.shared_learning.id,
          },
        })
        .then((res) => {
          this.attachment_metadata = res;
        })
        .catch((err) => console.error(err));
    },
    updateSelected(flag) {
      if (this.non_deleted_attachment_metadata.length == 0) return;

      this.loading = true;
      this.$emit("loading", this.loading);

      // first item as only accepts one file
      let filename = this.non_deleted_attachment_metadata[0].unique_filename;

      this.$axios
        .$$patch("/shared_learning/selected", null, {
          params: {
            shared_learning_id: this.investigation.shared_learning.id,
            filename,
            flag,
          },
        })
        .then(() => {
          this.investigation.shared_learning.use_custom_report = flag;
          // remove extension from filename
          filename = filename.split(".")[0];
          filename = `${filename}.pdf`;
          this.investigation.shared_learning.custom_report_fname = flag ? filename : null;

          this.loading = false;
          this.$emit("loading", this.loading);
        })
        .catch((err) => console.error(err));
    },
  },
};
</script>

<style lang="scss" scoped></style>
