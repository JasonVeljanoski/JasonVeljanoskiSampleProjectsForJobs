<template>
  <span v-if="tooltip">
    <v-tooltip bottom :disabled="!tooltip">
      <template #activator="{ on }">
        <v-btn v-bind="{ ...$attrs, ...$props }" v-on="{ ...on, ...$listeners }">
          <slot />
        </v-btn>
      </template>
      <span style="white-space: pre-wrap">{{ tooltip }}</span>
    </v-tooltip>
  </span>
  <v-btn v-else v-bind="$attrs" v-on="$listeners">
    <slot />
  </v-btn>
</template>

<script>
export default {
  props: {
    tooltip: {
      type: String,
      default: null,
    },
  },
}
</script>

<style scoped></style>
