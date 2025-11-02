<template>
  <v-autocomplete
    ref="input"
    v-bind="{ ...$attrs, ...$props }"
    :item-value="'item-value' in $attrs ? $attrs.itemValue : 'id'"
    :item-text="getItemText"
    :prepend-inner-icon="'prepend-inner-icon' in $attrs ? $attrs.prependInnerIcon : 'mdi-account'"
    v-on="$listeners"
  >
    <template #selection="data">
      <v-chip
        v-bind="data.attrs"
        :input-value="data.selected"
        close-icon="mdi-close"
        :close="'multiple' in $attrs"
        outlined
        @click="data.select"
        @click:close="remove(data.item)"
      >
        {{ data.item.name }}
      </v-chip>
    </template>

    <template #item="data">
      <v-list-item-content>
        <v-list-item-title class="item-title" v-text="data.item.name" />
        <v-list-item-subtitle class="item-subtitle" v-text="data.item.email" />
      </v-list-item-content>
    </template>
  </v-autocomplete>
</template>

<script>
export default {
  computed: {
    value() {
      return this.$attrs.value
    },
    items() {
      return this.$attrs.items
    },
  },
  methods: {
    getItemText(item) {
      return `${item.email} ${item.name}`
    },
    remove(item) {
      const index = this.value.indexOf(item.id)
      if (index >= 0) this.value.splice(index, 1)
    },
  },
}
</script>

<style lang="scss" scoped>
.item-title {
  font-size: 12pt !important;
}
.item-subtitle {
  font-size: 10pt !important;
}
</style>
