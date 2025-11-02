<template>
  <v-tooltip v-bind="{ ...$attrs, ...$props }" bottom max-width="300" v-on="$listeners">
    <template #activator="{ on, attrs }">
      <span v-bind="attrs" v-on="on">{{ main_text }}</span>
    </template>
    <slot>{{ sub_text }}</slot>
  </v-tooltip>
</template>

<script>
export default {
  name: 'ActionsTable',
  props: {
    main_text: { type: String },
    sub_text: { type: String },
  },
}
</script>
