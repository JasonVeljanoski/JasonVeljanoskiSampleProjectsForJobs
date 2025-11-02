<template>
  <div>
    <div v-show="!edit_mode" class="img-wrapper">
      <div class="buttons-r">
        <e-icon-btn icon tooltip="Edit" @click="draw"> mdi-draw </e-icon-btn>
      </div>
      <v-img class="signature" :src="value" />
    </div>
    <div v-show="edit_mode" class="img-wrapper">
      <div class="buttons-l">
        <e-icon-btn icon tooltip="Undo" @click="undo"> mdi-undo </e-icon-btn>
        <e-icon-btn icon tooltip="Remove Signature" @click="clear">
          mdi-eraser
        </e-icon-btn>
      </div>
      <div class="buttons-r">
        <e-icon-btn icon tooltip="Save" @click="save">
          mdi-content-save
        </e-icon-btn>
      </div>
      <vue-signature-pad
        class="signature"
        ref="signaturePad"
        width="100%"
        height="250px"
        :options="{
          onBegin: () => {
            $refs.signaturePad.resizeCanvas();
          },
        }"
      />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    value: { type: String },
    readonly: { type: Boolean, default: false },
  },
  data() {
    return {
      edit_mode: false,
    };
  },

  mounted() {
    // this.$refs.signaturePad.fromDataURL(this.value);
  },
  methods: {
    draw() {
      this.edit_mode = true;

      this.$refs.signaturePad.resizeCanvas();
      this.$refs.signaturePad.clearSignature();
    },
    save() {
      this.edit_mode = false;
      const { data, isEmpty } = this.$refs.signaturePad.saveSignature();

      this.$emit("input", data);
      this.$emit("change", data);
    },
    undo() {
      this.$refs.signaturePad.undoSignature();
      // this.save();
    },
    clear() {
      if (this.$refs.signaturePad) this.$refs.signaturePad.clearSignature();
    },
  },
};
</script>

<style scoped lang="scss">
.img-wrapper {
  border-radius: 5px;
  border: 1px solid;
  position: relative;

  .theme--dark & .signature {
    filter: invert(1);
  }
}

.buttons-l,
.buttons-r {
  display: flex;
  position: absolute;
  z-index: 2;
}

.buttons-l {
  left: 0px;
}
.buttons-r {
  right: 0px;
}
</style>
