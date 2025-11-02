<template>
  <v-card outlined elevation="0">
    <v-card-title class="att-title"> Attachments </v-card-title>

    <v-divider />

    <v-card-text
      v-if="non_deleted_attachment_metadata.length == 0"
      class="my-2"
    >
      No attachments.
    </v-card-text>

    <e-data-table
      v-else
      :headers="headers"
      :items="non_deleted_attachment_metadata"
      fixed-header
      :options="{
        itemsPerPage: 4,
        sortBy: ['created'],
        sortDesc: [true],
      }"
      :footer-props="{
        'items-per-page-options': [],
      }"
    >
      <template #item.download="{ item }">
        <e-icon-btn
          tooltip="Download"
          :href="$document.download(getFilePath(item))"
          target="_blank"
        >
          mdi-download
        </e-icon-btn>
      </template>
      <template #item.remove="{ item }">
        <e-icon-btn tooltip="Remove" @click="removeAttachment(item)">
          mdi-delete
        </e-icon-btn>
      </template>
    </e-data-table>
  </v-card>
</template>

<script>
export default {
  props: {
    attachment_metadata: { type: Array, default: () => [] },
  },
  data() {
    return {
      showAdd: false,
      files: [],
      headers: [
        { text: "Name", value: "filename", divider: true },
        { text: "Extension", value: "extension", divider: true },
        {
          text: "Uploaded By",
          value: "uploaded_by",
          divider: true,
          formatter: (x) => this.$utils.getUserName(x),
        },
        {
          text: "Upload Date",
          value: "created",
          divider: true,
          formatter: (x) => this.$format.date(x),
        },
        {
          text: "Size",
          value: "size",
          formatter: (x) => this.$format.formatBytes(x),
          divider: true,
        },
        {
          text: "Download",
          value: "download",
          width: "10",
          divider: true,
          sortable: false,
          align: "center",
        },
        {
          text: "Remove",
          value: "remove",
          width: "10",
          sortable: false,
          align: "center",
        },
      ],
    };
  },
  computed: {
    non_deleted_attachment_metadata() {
      return this.attachment_metadata.filter((x) => !x.deleted);
    },
  },
  methods: {
    getFilePath(attachment) {
      return `${this.$enums.document_paths["general_attachments"]}/${attachment.unique_filename}`;
    },
    openFileUploader() {
      this.$refs.uploader.open().then((resp) => {
        if (!resp) return;

        this.files = resp;
        for (const file of this.files) {
          this.addAttachment(file);
        }
      });
    },
    removeAttachment(attachment) {
      if (!confirm("Are you sure you want to remove this attachment?")) {
        return;
      }

      const path = this.getFilePath(attachment);

      this.$axios
        .$post(`document/remove/${path}`, null, {
          params: {
            attachment_id: attachment.id,
          },
        })
        .then(() => {
          const idx = this.attachment_metadata.findIndex(
            (x) => x.id == attachment.id
          );
          this.attachment_metadata.splice(idx, 1);
        })
        .catch((err) => console.error(err));
    },
  },
  watch: {
    showAdd() {
      if (this.showAdd && this.$refs.form) this.$refs.form.reset();
    },
  },
};
</script>

<style lang="scss" scoped>
.attachments {
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  gap: 1em;
  overflow-y: auto;
}

.att-title {
  font-size: 16px;
}
</style>
