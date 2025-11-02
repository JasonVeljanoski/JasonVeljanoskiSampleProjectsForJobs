<template>
  <v-dialog
    :value="value"
    v-bind="{ ...$attrs, ...$props }"
    :fullscreen="fullscreen || is_mobile"
    persistent
    width="1200"
    scrollable
    v-on="$listeners"
  >
    <v-card :tile="fullscreen || is_mobile">
      <!-- TITLE -->
      <v-card-title>
        <slot name="card:header">{{ title }}</slot>
        <v-spacer />
        <e-icon-btn v-if="!is_mobile" @click="toggleFullscreen">
          {{ fullscreen_icon }}
        </e-icon-btn>
        <e-icon-btn @click="$emit('close')"> mdi-close </e-icon-btn>
      </v-card-title>

      <!-- <v-divider class="mb-4" /> -->

      <!-- BODY -->
      <v-card-text>
        <slot name="card:body" />
      </v-card-text>

      <!-- <v-divider /> -->

      <!-- ACTIONS -->
      <v-card-actions>
        <slot name="card:footer" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  props: {
    value: { type: Boolean, default: false },
    title: { type: String },
  },
  data() {
    return {
      fullscreen: false,
    }
  },
  computed: {
    ...mapGetters({
      is_mobile: 'theme/getIsMobile',
    }),
    fullscreen_icon() {
      return this.fullscreen ? 'mdi-arrow-collapse' : 'mdi-arrow-expand'
    },
  },
  methods: {
    toggleFullscreen() {
      this.fullscreen = !this.fullscreen
    },
  },
}
</script>
