<template>
  <v-card outlined elevation="0">
    <v-card-title class="att-title">
      Attachments
      <v-spacer />
      <v-btn v-bind="$bind.btn" class="mx-3" @click="addAttachment">
        <v-icon left>mdi-plus</v-icon>
        <span>Attachment</span>
      </v-btn>
    </v-card-title>

    <v-divider />

    <v-card-text v-if="non_deleted_attachment_metadata.length == 0" class="my-2"> No attachments. </v-card-text>

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
      <template #item.id="{ item }">
        <span v-if="item.id">
          {{ item.id }}
        </span>
        <v-tooltip v-else top>
          <template v-slot:activator="{ on, attrs }">
            <v-icon v-bind="attrs" v-on="on"> mdi-progress-clock </v-icon>
          </template>
          <span>Pending</span>
        </v-tooltip>
      </template>
      <template #item.title="{ item }">
        <title-hover-text :main_text="item.title" :sub_text="item.description" />
      </template>
      <template #item.download="{ item }">
        <e-icon-btn
          tooltip="Download"
          :href="$document.download(getFilePath(item))"
          :disabled="!item.id"
          target="_blank"
        >
          mdi-download
        </e-icon-btn>
      </template>
      <template #item.remove="{ item }">
        <e-icon-btn :disabled="!item.id" tooltip="Remove" @click="removeAttachment(item)"> mdi-delete </e-icon-btn>
      </template>
    </e-data-table>

    <!-- DIALOG -->
    <e-attachment-uploader ref="uploader" />
  </v-card>
</template>

<script>
export default {
  props: {
    attachment_metadata: { type: Array, default: () => [] },
  },
  data() {
    return {
      headers: [
        {
          text: "#",
          align: "center",
          value: "id",
          sortable: false,
          divider: true,
          hide: false,
          width: "10",
        },
        { text: "Title", value: "title", width: "120", divider: true },
        {
          text: "Network Drive Link",
          value: "network_drive_link",
          width: "120",
          divider: true,
        },
        { text: "File Name", value: "filename", width: "120", divider: true },
        {
          text: "Size (MB)",
          value: "size",
          formatter: (x) => (x ? this.$format.bytesToMegabytes(x) : ""),
          divider: true,
          width: "10",
        },
        {
          text: "Uploaded By",
          value: "uploaded_by",
          divider: true,
          width: "10",
          formatter: (x) => this.$utils.getUserName(x),
        },
        {
          text: "Upload Date",
          value: "created",
          divider: true,
          width: "10",
          formatter: (x) => this.$format.date(x),
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
    // todo: make this a backend task
    // but keep this logic as when you delete an item, take advantage of frontend logic to show non - deleted items
    non_deleted_attachment_metadata() {
      return this.attachment_metadata.filter((x) => !x.deleted);
    },
  },
  methods: {
    // ---------------------------
    // ATTACHMENT
    // ---------------------------
    addAttachment() {
      this.$refs.uploader.open().then((res) => {
        // promise returns false - on cancel
        if (!res) return;

        // promise returns attach. obj. - on save
        this.$emit("new_attachment", res);
      });
    },
    // ---------------------------
    // DOWNLOAD AND REMOVE
    // ---------------------------
    getFilePath(attachment) {
      return `${this.$enums.document_paths["general_attachments"]}/${attachment.unique_filename}`;
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
          const idx = this.attachment_metadata.findIndex((x) => x.id == attachment.id);
          this.attachment_metadata.splice(idx, 1);
        })
        .catch((err) => console.error(err));
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
