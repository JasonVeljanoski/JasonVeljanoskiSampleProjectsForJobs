<template>
  <div>
    <v-card outlined elevation="0" max-width="1200" class="mx-auto">
      <v-card-title>
        Distribution List
        <v-spacer />
        <v-btn outlined class="mr-4" v-bind="$bind.btn" color="primary" @click="previewData(true)">
          <v-icon left>mdi-book-open</v-icon>
          Preview Data
        </v-btn>
        <v-btn v-bind="$bind.btn" color="primary" @click="openFileUploader">
          <v-icon left>mdi-plus</v-icon>
          Add New
        </v-btn>
      </v-card-title>

      <v-divider />
      <v-card-text v-if="non_deleted_attachment_metadata.length == 0" class="my-2">
        No distribution lists.
      </v-card-text>

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
        <template #item.is_active_list="{ item }">
          <div class="d-flex justify-center">
            <v-checkbox
              v-model="item.is_active_list"
              :value="item.is_active_list"
              @change="updateSelected(item.id, $event)"
            />
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

    <!-- DIALOG -->
    <v-dialog scrollable v-model="preview" width="800" persistent>
      <v-card height="500" width="100%" class="pb-1">
        <v-card-title>
          Preview Data
          <v-spacer />
          <e-btn @click="switchViewFunc()" class="ml-auto" :tooltip="switchView ? 'Collapse' : 'Expand'" icon>
            <v-icon>{{ switchView ? "mdi-eye-off" : "mdi-eye" }}</v-icon>
          </e-btn>
          <e-btn @click="previewData(false)" icon>
            <v-icon>mdi-close</v-icon>
          </e-btn>
        </v-card-title>
        <v-divider v-if="preview_response !== null" />

        <v-card-text v-if="preview_tree.length != 0" class="pa-0">
          <v-treeview :items="preview_tree" :key="render_key" :open-all="switchView" dense />
        </v-card-text>
        <v-card-text v-else class="my-2"> No distribution list is selected </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  components: {},
  data() {
    return {
      render_key: 0,
      attachment_metadata: [],
      showAdd: false,
      preview: false,
      switchView: false,
      preview_response: null,
      preview_tree: [],
      headers: [
        { text: "Selected", value: "is_active_list", width: 10, divider: true },
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
    switchViewFunc() {
      this.switchView = !this.switchView;
      this.render_key++;
    },
    convertJSONToTree(obj) {
      return Object.keys(obj).map((key, index) => {
        const value = obj[key];
        const children = typeof value === "object" ? this.convertJSONToTree(value) : [];
        const isLeaf = children?.length === 0;

        if (isLeaf) return { id: key, name: value };
        else return { id: key, name: key, children };
      });
    },
    async previewData(isON) {
      if (isON) {
        await this.$axios
          .$get("/static/email_distribution_list")
          .then((res) => {
            const leng = Object.keys(res)?.length;

            if (leng != 0 && res != null) {
              this.preview_response = res;
              this.preview_tree = this.convertJSONToTree(res);
            }
          })
          .catch((err) => console.error(err));
      }
      this.preview = isON;
    },
    getAttachments() {
      this.$axios.$get("/dashboard/distribution_list_attachments").then((res) => {
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
      if (flag == false) this.preview_tree = [];

      this.$axios
        .$$patch("/dashboard/selected_distribution_list", null, {
          params: { id: id, flag: flag },
        })
        .then(() => {
          // reset
          for (let ii = 0; ii < this.attachment_metadata.length; ii++)
            this.attachment_metadata[ii].is_active_list = false;

          // -----

          // set
          const indx = this.attachment_metadata.findIndex((x) => x.id == id);
          if (indx > -1) this.attachment_metadata[indx].is_active_list = flag;

          // -----

          // message
          this.$snackbar.add("Distribution List updated successfully");
        })
        .catch((err) => {
          // reset
          for (let ii = 0; ii < this.attachment_metadata.length; ii++)
            this.attachment_metadata[ii].is_active_list = false;
          this.$snackbar.add("File must be a csv that fits the exact format for a dashboard upload", "error");
          console.error(err);
        });
    },
  },
};
</script>

<style lang="scss" scoped></style>
