<template>
  <v-card min-width="320">
    <!-- TITLE -->
    <v-card-title>Applied Filters</v-card-title>

    <!-- BODY -->
    <span class="body-wrapper">
      <template v-if="!rules_len">
        <v-divider />
        <v-card-text>No rules applied.</v-card-text>
      </template>
      <v-list v-else>
        <div v-for="({ preferred_text, combine, rules }, header) in filters" :key="header">
          <template v-if="rules.length">
            <v-divider />
            <v-subheader style="color: var(--v-primary-base)">
              <b>{{ prettyText(preferred_text || header) }}</b>
            </v-subheader>
            <v-divider />
            <div v-for="(rule, ii) in rules" :key="ii">
              <v-list-item dense>
                <v-list-item-content>
                  <v-list-item-title>{{ listText(rule) }}</v-list-item-title>
                </v-list-item-content>
                <v-list-item-icon class="d-flex align-center">
                  <e-icon-btn color="error" @click="removeRule(rules, ii)">mdi-delete</e-icon-btn>
                </v-list-item-icon>
              </v-list-item>
              <div v-if="ii < rules.length - 1" class="text-divider">{{ combine.toUpperCase() }}</div>
            </div>
          </template>
        </div>
      </v-list>
    </span>
    <v-divider />

    <!-- ACTIONS -->
    <v-card-actions>
      <cancel-btn @click="clearFilters()">Clear</cancel-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: {
    filters: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    rules_len() {
      return Object.values(this.filters).reduce((acc, { rules }) => acc + rules.length, 0)
    },
  },
  methods: {
    removeRule(rules, ii) {
      rules.splice(ii, 1)

      this.$emit('reload')
    },
    listText(rule) {
      let res = ''
      if (rule) res = `${this.prettyText(rule.type)}`
      if (rule.value) {
        res += ` "${rule.format_value ? rule.format_value : rule.value}"`
      }
      return res
    },
    prettyText(text) {
      text = text.replace(/_/g, ' ')
      return text.replace(/(?:^|\s)\S/g, (x) => x.toUpperCase())
    },
    clearFilters() {
      for (const key in this.filters) {
        this.filters[key].rules = []
      }
      this.$emit('reload')
    },
  },
}
</script>

<style lang="scss" scoped>
.text-divider {
  --text-divider-gap: 1rem;
  display: flex;
  align-items: center;
  font-size: 0.9375rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 8pt;
}

.text-divider::before,
.text-divider::after {
  content: '';
  height: 1px;
  background-color: var(--v-accent-base);
  flex-grow: 1;
}

.text-divider::before {
  margin-right: var(--text-divider-gap);
}

.text-divider::after {
  margin-left: var(--text-divider-gap);
}

::v-deep .v-sheet.v-list {
  padding: 0;
}
</style>
