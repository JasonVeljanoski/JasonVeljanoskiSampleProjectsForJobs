<template>
  <div>
    <v-dialog v-model="dialog" v-bind="{ ...$bind.dialog }" fullscreen>
      <template v-slot:activator="{ on, attrs }">
        <v-text-field
          v-bind="{ ...attrs, ...$bind.textfield }"
          :rules="imgRules"
          :disabled="imgDisabled"
          multiple
          small-chips
          readonly
          dense
          prepend-inner-icon="mdi-image"
          hide-details="auto"
          prepend-icon=""
          @click:clear="images.length = 0"
          v-on="on"
        />
        <div class="d-flex">
          <v-spacer />
          {{ format_bytes }}
        </div>
      </template>
      <div class="dialog-container">
        <v-image-input
          v-model="tmp_img"
          :image-quality="1"
          :imageWidth="window_width"
          :imageHeight="window_height"
          :successIconStyle="{ color: 'var(--v-primary-base) !important' }"
          :uploadIconStyle="{ color: 'var(--v-primary-base) !important' }"
          successIcon="mdi-upload"
          uploadIcon="mdi-upload"
          image-format="png"
          clearIcon="mdi-close"
          flipHorizontallyIcon="mdi-flip-horizontal"
          flipVerticallyIcon="mdi-flip-vertical"
          rotateClockwiseIcon="mdi-rotate-right"
          rotateCounterClockwiseIcon="mdi-rotate-left"
          fullWidth
          clearable
          imageMinScaling="contain"
          @file-info="onFileInfo($event)"
        />
        <div class="add-img">
          <v-btn v-bind="$bind.btn" @click="addImage()">
            <v-icon left>mdi-plus</v-icon>
            add image
          </v-btn>
        </div>
      </div>
    </v-dialog>

    <!-- PREVIEW IMAGES  -->
    <div class="img-wrapper mt-4">
      <div v-for="(img, ii) in images" :key="ii" class="img-item" :style="imageStyle">
        <v-img :src="img" />
        <e-icon-btn x-small @click="removeImage(ii)" class="remove-img"> mdi-close </e-icon-btn>
      </div>
    </div>
  </div>
</template>

<script>
import VImageInput from "vuetify-image-input/a-la-carte";

export default {
  components: {
    VImageInput,
  },
  props: {
    images: { type: Array },
    imgRules: { type: Array },
    imgDisabled: { type: Boolean, default: false },
    imageStyle: { type: Object },
  },
  data() {
    return {
      dialog: false,
      tmp_img: null,
      images_meta: [],
      tmp_meta: null,
    };
  },
  computed: {
    total_bytes() {
      let sizeBytes = 0;
      for (let meta of this.images_meta) sizeBytes += meta.size;
      return sizeBytes;
    },
    format_bytes() {
      const bytes = this.total_bytes;
      return bytes == 0 ? null : (bytes / (1024 * 1024)).toFixed(2) + "MB";
    },
    window_width() {
      return window.innerWidth * 0.8;
    },
    window_height() {
      return this.window_width * 0.5625;
    },
  },
  methods: {
    exceedsFileSize() {
      const FIFTY_MB = 50 * 1024 * 1024;
      if (this.total_bytes > FIFTY_MB) {
        const message = "The file(s) exceed the maximum file size of 50MB.";
        this.$snackbar.add(message, "warning");

        return true;
      }
      return false;
    },
    onFileInfo(file_info) {
      const file_type = file_info.type;
      if (file_type.startsWith("image/")) {
        this.tmp_meta = file_info;
      } else {
        this.images.length = 0;

        const message = "Incorrect File Type! Please import images only.";
        this.$snackbar.add(message, "error");
      }
    },
    addImage() {
      if (this.tmp_img && this.tmp_meta) {
        this.images.push(this.tmp_img);
        this.images_meta.push(this.tmp_meta);

        if (this.exceedsFileSize()) {
          this.images.pop();
          this.images_meta.pop();
        }
        this.dialog = false;
      }
      this.tmp_img = null;
      this.tmp_meta = null;
    },
    removeImage(ii) {
      this.images.splice(ii, 1);
      this.images_meta.splice(ii, 1);
    },
  },
};
</script>

<style lang="scss" scoped>
.remove {
  cursor: pointer;
  margin-left: 10px;

  &:hover {
    color: var(--v-error-base);
    text-decoration: underline;
  }
}

.add-img {
  text-align: right;
}

.dialog-container {
  background-color: var(--v-background-base);
  overflow: hidden;
  padding: 10px;
}

.img-wrapper {
  display: flex;
  justify-content: space-evenly;
}

.img-item {
  display: flex;
  border-radius: 10px;
  overflow: hidden;
  max-width: 300px;
  margin: 5px;
}

.remove-img {
  position: relative;
  margin-left: -27px;
  margin-top: 7px;
  background-color: var(--v-accent-base);

  &:hover {
    opacity: 0.4;
  }
}
</style>
