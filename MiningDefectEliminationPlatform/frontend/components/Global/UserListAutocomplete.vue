<template>
  <v-autocomplete
    v-bind="{ ...$attrs, ...$props }"
    prepend-inner-icon="mdi-account"
    v-on="$listeners"
    :search-input.sync="searchInput"
    @input="searchInput = null"
  >
    <template #selection="data">
      <v-chip
        v-if="data.index < 2"
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

      <span v-else-if="data.index === 2" class="text-overline mx-2">
        <v-tooltip right>
          <template #activator="{ on, attrs }">
            <span v-on="on">+{{ value.length - 2 }} User(s)</span>
          </template>
          <div v-for="(item, i) in value.slice(2)" :key="i">
            <span v-if="isNaN(item)">{{ item }}</span>
            <span v-else>{{ $utils.getUserName(item) }}</span>
          </div>
        </v-tooltip>
      </span>
    </template>

    <template #item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title class="item-title" v-text="data.item.name" />
          <v-list-item-subtitle class="item-subtitle" v-text="data.item.email" />
        </v-list-item-content>
      </template>
    </template>
  </v-autocomplete>
</template>

<script>
export default {
  data() {
    return {
      searchInput: null,
    };
  },
  computed: {
    value() {
      return this.$attrs.value;
    },
    items() {
      return this.$attrs.items;
    },
  },
  methods: {
    remove(item) {
      const index = this.value.indexOf(item.id);
      if (index >= 0) this.value.splice(index, 1);
    },
  },
};
</script>

<style lang="scss" scoped>
.item-title {
  font-size: 12pt !important;
}
.item-subtitle {
  font-size: 10pt !important;
}
</style>
