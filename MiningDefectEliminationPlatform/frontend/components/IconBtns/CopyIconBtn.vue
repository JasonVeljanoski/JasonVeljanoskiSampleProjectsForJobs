<template>
  <div>
    <e-icon-btn v-bind="{ ...$props, ...$attrs }" :tooltip="tooltip" @click="handleCopy">
      {{ icon_text }}
    </e-icon-btn>
    <div v-if="id" style="font-size: 10px; font-weight: 500; margin-top: -8px">#{{ id }}</div>
  </div>
</template>

<script>
export default {
  name: "CopyIconBtn",
  props: {
    id: {
      type: Number,
      required: false,
    },
    title: {
      type: String,
      required: false,
      default: "",
    },
  },
  data() {
    return {
      is_copied: false,
    };
  },
  computed: {
    icon_text() {
      return this.is_copied ? "mdi-clipboard-check-outline" : "mdi-content-paste";
    },
    tooltip() {
      return this.is_copied ? "Copied" : "Copy";
    },
  },
  methods: {
    handleCopy() {
      this.is_copied = true;
      setTimeout(() => (this.is_copied = false), 1500);

      this.$emit("copy");
    },
  },
};
</script>
