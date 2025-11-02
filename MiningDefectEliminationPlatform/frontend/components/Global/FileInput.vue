<template>
  <div v-cloak @drop.prevent="addDropFiles" @dragover.prevent>
    <v-file-input
      v-model="inner_value"
      v-bind="{ ...$attrs, ...$props }"
      :counter="inner_value.length > 0"
      :accept="file_whitelist"
      :show-size="1000"
      outlined
      multiple
      dense
      placeholder="Drag and drop or click to upload."
      prepend-inner-icon="mdi-paperclip"
      hide-details="auto"
      prepend-icon=""
      @change="change"
    >
      <template v-slot:selection="{ index, text }">
        <v-chip v-if="index < 2" close @click:close="remove(index)">
          {{ text }}
        </v-chip>
        <span v-else-if="index === 2"> +{{ value.length - 2 }} File(s) </span>
      </template>
    </v-file-input>
  </div>
</template>

<script>
export default {
  inheritAttrs: false,
  props: {
    value: { type: Array },
  },
  data() {
    return {
      inner_value: [...this.value],
      file_whitelist: [
        ".pdf",
        ".docx",
        ".doc",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
        ".csv",
        ".mp3",
        ".mp4",
      ],
    };
  },
  methods: {
    remove(index) {
      this.inner_value.splice(index, 1);
      this.change();
    },
    addDropFiles(event) {
      for (const file of event.dataTransfer.files) this.inner_value.push(file);

      this.change();
    },
    change() {
      this.$emit("input", this.inner_value);
      this.$emit("change", this.inner_value);
    },
  },
};
</script>

<style lang="scss" scoped>
.error_text {
  color: var(--v-error-base);
}
.img-chips {
  margin: auto;
  max-height: 150px;
  overflow-y: scroll;
}
.file_uploader_root {
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
      height: 70px;
      border-radius: 5px;
      opacity: 0.3;
    }

    ::v-deep .v-input__slot::before {
      border-style: none !important;
    }

    ::v-deep .v-file-input__text {
      display: none;
    }

    ::v-deep .v-text-field__prefix {
      width: 100%;
      font-style: italic;
      text-align: center;
    }
  }
}
</style>
