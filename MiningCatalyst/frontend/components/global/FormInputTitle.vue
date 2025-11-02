<template>
  <v-skeleton-loader v-if="loading" type="chip" class="my-2" />
  <span v-else class="d-flex">
    <h3>{{ title }}</h3>
    <span v-if="edit_mode && required" class="star">*</span>
    <v-tooltip v-if="info_text && edit_mode" right>
      <template #activator="{ on }">
        <v-btn icon x-small v-on="on">
          <v-icon>mdi-information-outline</v-icon>
        </v-btn>
      </template>
      <span>{{ info_text }}</span>
    </v-tooltip>
  </span>
</template>

<script>
export default {
  props: {
    loading: { type: Boolean, default: true },
    title: { type: String },
    info_text: { type: String, default: null },
    required: { type: Boolean, default: false },
    edit_mode: { type: Boolean, default: false },
  },
}
</script>

<style lang="scss" scoped>
.star {
  color: var(--v-error-base);
  margin-left: 5px;
}
</style>
