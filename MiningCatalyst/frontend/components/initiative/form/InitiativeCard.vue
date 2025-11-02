<template>
  <v-card height="100%" class="d-flex flex-column">
    <!-- TITLE -->
    <v-card-title>
      <slot name="card:header">{{ title }}</slot>
    </v-card-title>

    <v-divider />

    <slot name="card:banner" />

    <!-- BODY -->
    <div class="body-wrapper flex-grow-1">
      <v-card-text>
        <v-form ref="form">
          <slot name="card:body" />
        </v-form>
        <v-spacer />
      </v-card-text>
    </div>

    <v-divider />

    <!-- ACTIONS -->
    <div class="align-end mt-auto">
      <v-card-actions>
        <slot name="card:footer" />
      </v-card-actions>
    </div>
  </v-card>
</template>

<script>
export default {
  props: {
    title: { type: String },
  },
}
</script>
