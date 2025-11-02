<template>
  <v-menu
    v-bind="{ ...$attrs, ...$props }"
    open-on-hover
    :close-on-content-click="false"
    bottom
    max-width="500"
    v-on="$listeners"
  >
    <template #activator="{ on, attrs }">
      <span v-bind="attrs" v-on="on">{{ title }}</span>
    </template>
    <v-card outline>
      <v-card-text>
        <slot>{{ subtitle }}</slot>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
export default {
  name: 'HoverTitle',
  props: {
    title: { type: String },
    subtitle: { type: String },
  },
}
</script>
