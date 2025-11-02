<template>
  <v-combobox
    v-bind="{ ...$attrs, ...$props, ...$bind.textfield }"
    multiple
    clearable
    :type="field_type"
    v-on="$listeners"
  >
    <template v-slot:append>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon color="primary" dark v-bind="attrs" v-on="on">
            mdi-information
          </v-icon>
        </template>
        <span>
          Select a recent event or enter a new one by typing and pressing enter
        </span>
      </v-tooltip>
    </template>
  </v-combobox>
</template>

<script>
export default {
  props: {
    event_type: { type: Number },
  },
  data() {
    return {
      event_detail_ids: [],
      rems_event_detail_ids: [],
    };
  },
  computed: {
    field_type() {
      if (this.event_type === this.$enums.event_types["APLUS"]) return "number";
    },
  },
  mounted() {},
  methods: {},
};
</script>

<style lang="scss" scoped>
ul,
li {
  list-style-type: none;
}

.root-cause {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border: solid 1px var(--v-accent-base);
  border-radius: 5px;
  margin: 5px;
}
</style>
