<template>
  <v-card outlined elevation="0" max-width="1200" class="mx-auto">
    <v-card-title>
      Dashboard Edit
      <v-spacer />
      <v-btn v-bind="$bind.btn" color="primary" @click="openFileUploader">
        <v-icon left>mdi-plus</v-icon>
        Add New
      </v-btn>
    </v-card-title>

    <v-divider />
    <v-card-text v-if="non_deleted_attachment_metadata.length == 0" class="my-2"> No dashboards. </v-card-text>

    <e-data-table
      v-else
      :headers="headers"
      :items="non_deleted_attachment_metadata"
      fixed-header
      :options="{
        itemsPerPage: 20,
        sortBy: ['created'],
        sortDesc: [true],
      }"
      :footer-props="{
        'items-per-page-options': [],
      }"
    >
      <template #item.is_active="{ item }">
        <div class="d-flex justify-center">
          <v-checkbox v-model="item.is_active" :value="item.is_active" @change="updateSelected(item.id, $event)" />
        </div>
      </template>
      <template #item.download="{ item }">
        <e-icon-btn tooltip="Download" :href="$document.download(getFilePath(item))" target="_blank">
          mdi-download
        </e-icon-btn>
      </template>
      <template #item.remove="{ item }">
        <e-icon-btn tooltip="Remove" @click="removeAttachment(item)"> mdi-delete </e-icon-btn>
      </template>
    </e-data-table>

    <!-- DIALOG -->
    <e-attachment-uploader ref="uploader" />
  </v-card>
</template>

<script>
export default {
  components: {},
  data() {
    return {
      attachment_metadata: [],
      showAdd: false,
      headers: [
        { text: "Selected", value: "is_active", width: 10, divider: true },
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
      if (this.attachment_metadata) return this.attachment_metadata.filter((x) => !x.deleted);
      return [];
    },
  },
  watch: {
    showAdd() {
      if (this.showAdd && this.$refs.form) this.$refs.form.reset();
    },
  },
  mounted() {
    this.getAttachments();
  },
  methods: {
    getAttachments() {
      this.$axios.$get("/dashboard/dashboard_attachments").then((res) => {
        this.attachment_metadata = res;
      });
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
        .$post("/dashboard/distribution_list", form_data)
        .then((res) => {
          this.attachment_metadata.push(res);
        })
        .catch((err) => {
          console.error(err);
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
          const idx = this.attachment_metadata.findIndex((x) => x.id == attachment.id);
          this.attachment_metadata.splice(idx, 1);
        })
        .catch((err) => console.error(err));
    },
    updateSelected(id, flag) {
      flag ||= false;

      this.$axios
        .$$patch("/dashboard/selected", null, {
          params: { id: id, flag: flag },
        })
        .then(() => {
          // reset
          for (let ii = 0; ii < this.attachment_metadata.length; ii++) this.attachment_metadata[ii].is_active = false;

          // -----

          // set
          const indx = this.attachment_metadata.findIndex((x) => x.id == id);
          if (indx > -1) this.attachment_metadata[indx].is_active = flag;

          // -----

          // message
          this.$snackbar.add("Dashboard uploaded successfully");
        })
        .catch((err) => {
          // reset
          for (let ii = 0; ii < this.attachment_metadata.length; ii++) this.attachment_metadata[ii].is_active = false;
          this.$snackbar.add("File must be a csv that fits the exact format for a dashboard upload", "error");
          console.error(err);
        });
    },
  },
};
</script>

<style lang="scss" scoped></style>
