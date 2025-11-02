<template>
  <v-card v-bind="{ ...$props, ...$attrs }" :elevation="0" outlined>
    <v-card-title>{{ title }}</v-card-title>
    <v-card-text>
      <slot />
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "BaseSection",
  props: {
    title: {
      type: String,
      required: false,
      default: "",
    },
  },
};
</script>
