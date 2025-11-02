<template>
  <div
    v-cloak
    @drop.prevent="drop"
    @dragover.prevent="dragover = true"
    @dragenter.prevent="dragover = true"
    @dragleave.prevent="dragover = false"
    class="hover"
  >
    <v-file-input
      :class="{ dragover: dragover }"
      :multiple="multiple"
      :show-size="1024"
      outlined
      dense
      class="file-input"
      placeholder="Drag and drop or click to upload."
      hide-details="auto"
      prepend-icon=""
      append-inner-icon="mdi-close"
      @change="addFiles"
      @click:clear="clearAll"
      @dragenter.prevent="dragover = true"
      @dragleave.prevent="dragover = false"
    >
      <template v-slot:selection="{ index, text }">
        <span v-if="index == 0" class="placeholder_text">
          Drag and drop or click to upload.
        </span>
      </template>
    </v-file-input>
    <p style="text-align: right" :class="{ error_text: exceeded_file_limit }">
      {{ file_limit_text }}
    </p>
    <div class="chip-wrapper">
      <v-chip
        v-for="(item, ii) in files"
        :key="ii"
        close
        @click:close="remove(ii)"
      >
        {{ item.name }} ({{ $format.formatBytes(item.size) }})
      </v-chip>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    files: { type: Array, default: () => [] },
    attachment_metadata: { type: Array, default: () => [] },
    multiple: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      file_blacklist: [
        ".",
        ".exe",
        ".scr",
        ".vbs",
        ".js",
        ".xml",
        ".docm",
        ".xps",
        ".iso",
        ".img",
        ".arj",
        ".lzh",
        ".r01",
        ".r14",
        ".r18",
        ".r25",
        ".tar",
        ".ace",
        ".jar",
        ".rtf",
        ".pub",
      ],
      dragover: false,
      MAX_FILE_SIZE_MB: 50,
    };
  },
  computed: {
    current_bytes() {
      let total = 0;
      for (let meta of this.attachment_metadata) total += meta.size;
      return total;
    },
    file_bytes() {
      let bytes = 0;
      for (let file of this.files) bytes += file.size;
      return bytes;
    },
    exceeded_file_limit() {
      const bytes = this.file_bytes;
      const mega_bytes = bytes / 1024 ** 2;
      const current_mega_bytes = this.current_bytes / 1024 ** 2;
      const res = current_mega_bytes + mega_bytes > this.MAX_FILE_SIZE_MB;

      this.$emit("has_exceeded_file_lim", res);
      return res;
    },
    file_limit_text() {
      let bytes = this.file_bytes;
      if (this.exceeded_file_limit)
        return `Limit of ${this.MAX_FILE_SIZE_MB}MB exceeded`;

      return this.$format.formatBytes(bytes);
    },
  },
  methods: {
    addFiles(files) {
      if (!files) return;

      // IF MULTIPLE IS SELECTED
      if (this.multiple) {
        for (let file of files) {
          let ext_split = file.name.split(".");
          let ext = ext_split[ext_split.length - 1];

          if (
            this.file_blacklist.includes(`.${ext}`) ||
            ext_split.length <= 1
          ) {
            let message =
              "This module does not accept the following file type:\n";
            message += file.name;
            this.$snackbar.add(message, "warning");
          } else {
            this.files.push(file);
          }
        }
      }
      // IF SINGLE FILE ONLY ALLOWED
      else {
        if (files.length > 1) {
          this.$snackbar.add(
            "Only one file can be uploaded at a time.",
            "warning"
          );
        } else {
          let ext_split = file.name.split(".");
          let ext = ext_split[ext_split.length - 1];

          if (
            this.file_blacklist.includes(`.${ext}`) ||
            ext_split.length <= 1
          ) {
            let message =
              "This module does not accept the following file type:\n";
            message += file.name;
            this.$snackbar.add(message, "warning");
          } else {
            this.files.push(file);
          }
        }
      }
    },
    remove(ii) {
      this.files.splice(ii, 1);
    },
    clearAll() {
      this.files.splice(0, this.files.length);
    },
    drop(event) {
      this.dragover = false;
      let files = [];
      for (const file of event.dataTransfer.files) files.push(file);
      this.addFiles(files);
    },
  },
};
</script>

<style lang="scss" scoped>
.chip-wrapper {
  // max-height: 100px;
  // overflow-y: auto;
}

.placeholder_text {
  color: rgb(188, 188, 188);
}

.error_text {
  color: var(--v-error-base);
}
.img-chips {
  margin: auto;
  max-height: 150px;
  overflow-y: scroll;
}

::v-deep .dragover::after {
  content: "";
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  position: absolute;
  pointer-events: none;

  background: rgba(grey, 0.3);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-input {
  ::v-deep .v-input__slot {
    // height: 100px;
  }

  // ::v-deep .v-input__slot::before {
  //   border-style: none !important;
  // }

  // ::v-deep .v-file-input__text {
  //   display: none;
  // }

  // ::v-deep .v-text-field__prefix {
  //   width: 100%;
  //   font-style: italic;
  //   text-align: center;
  // }
}
</style>
