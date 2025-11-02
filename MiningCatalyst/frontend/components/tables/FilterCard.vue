<template>
  <v-card v-if="value" outlined>
    <template v-if="is_sortable">
      <v-subheader>Sorting</v-subheader>
      <v-divider />
      <v-list dense>
        <v-list-item-group v-model="sorting" color="primary">
          <v-list-item :value="false">
            <v-list-item-icon>
              <v-icon>{{ sort_asc.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ sort_asc.text }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-divider />
          <v-list-item :value="true">
            <v-list-item-icon>
              <v-icon>{{ sort_desc.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ sort_desc.text }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>

      <v-divider />
    </template>

    <v-subheader>Filtering</v-subheader>

    <v-divider />

    <v-card-text>
      <v-select v-model="value.combine" :items="combine_types" v-bind="field_props" mandatory />
    </v-card-text>

    <v-divider />

    <v-card-text>
      <span v-for="(rule, ii) in value.rules" :key="ii" class="rule-wrapper">
        <v-select
          v-model="rule.type"
          :items="filtered_constraint_types"
          v-bind="field_props"
          placeholder="Filter Method"
        />
        <component
          :is="input_component.component"
          v-if="showInput(rule)"
          v-model="rule.value"
          autofocus
          v-bind="input_component.props"
          placeholder="Filter Value"
          @change="changeRule(rule)"
        />

        <v-btn text block color="error" x-small @click="removeRule(ii)">
          <v-icon left>mdi-delete</v-icon>
          Rule
        </v-btn>
        <v-divider />
      </span>

      <v-btn elevation="0" @click="addRule">
        <v-icon left>mdi-plus</v-icon>
        Rule
      </v-btn>
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-spacer />
      <save-btn @click="$emit('save')"> Apply </save-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { VCheckbox, VTextField, VSelect, VAutocomplete } from 'vuetify/lib'

import DateField from '@/components/enco/DateField.vue'

export default {
  props: {
    value: Object,
    header: Object,
    options: Object,
  },
  data() {
    return {
      filters: {},
      // sorting: undefined,
      field_props: {
        dense: true,
        outlined: true,
        'hide-details': true,
      },
      field_types: {
        string: {
          sort_asc: { icon: 'mdi-sort-alphabetical-ascending', text: 'A-Z' },
          sort_desc: { icon: 'mdi-sort-alphabetical-descending', text: 'Z-A' },
        },
        number: {
          sort_asc: { icon: 'mdi-sort-numeric-ascending', text: 'Low to High' },
          sort_desc: { icon: 'mdi-sort-numeric-descending', text: 'High to Low' },
        },
        date: {
          sort_asc: { icon: 'mdi-sort-clock-ascending', text: 'Earliest to Latest' },
          sort_desc: { icon: 'mdi-sort-clock-descending', text: 'Latest to Earliest' },
        },
        boolean: {
          sort_asc: { icon: 'mdi-sort-bool-ascending-variant', text: 'False to True' },
          sort_desc: { icon: 'mdi-sort-bool-descending-variant', text: 'True to False' },
        },
        select: {
          sort_asc: { icon: 'mdi-sort-ascending', text: 'Sort ASC' },
          sort_desc: { icon: 'mdi-sort-descending', text: 'Sort DESC' },
        },
      },

      constraint_types: [
        {
          value: 'starts_with',
          text: 'Starts With',
          types: ['string', 'number'],
          check: (value, constraint) => `${value}`.startsWith(constraint.value),
        },
        {
          value: 'ends_with',
          text: 'Ends With',
          types: ['string', 'number'],
          check: (value, constraint) => `${value}`.endsWith(constraint.value),
        },
        {
          value: 'contains',
          text: 'Contains',
          types: ['string'],
          check: (value, constraint) => `${value}`.includes(constraint.value),
        },
        {
          value: 'does_not_contain',
          text: 'Does Not Contain',
          types: ['string', 'number'],
          check: (value, constraint) => !`${value}`.includes(constraint.value),
        },
        {
          value: 'equals',
          text: 'Equals',
          types: ['string', 'number', 'select'],
          check: (value, constraint) => value === constraint.value,
        },
        {
          value: 'date_equals',
          text: 'Equals',
          types: ['date'],
          check: (value, constraint) => value === constraint.value,
        },
        {
          value: 'does_not_equal',
          text: 'Does Not Equal',
          types: ['string', 'number', 'select'],
          check: (value, constraint) => value !== constraint.value,
        },
        {
          value: 'is_greater_than',
          text: 'Is Greater Than',
          types: ['number'],
          check: (value, constraint) => value > constraint.value,
        },
        {
          value: 'is_less_than',
          text: 'Is Less Than',
          types: ['number'],
          check: (value, constraint) => value < constraint.value,
        },
        {
          value: 'is_after',
          text: 'Is After',
          types: ['date'],
          check: (value, constraint) => value > constraint.value,
        },
        {
          value: 'is_before',
          text: 'Is Before',
          types: ['date'],
          check: (value, constraint) => value < constraint.value,
        },
        // ------------------------------------------
        {
          value: 'is_true',
          text: 'Is True',
          types: ['boolean'],
          input: false,
          check: (value, constraint) => value === true,
        },
        {
          value: 'is_false',
          text: 'Is False',
          types: ['boolean'],
          input: false,
          check: (value, constraint) => value === false,
        },
        // ------------------------------------------
        {
          value: 'is_empty',
          text: 'Is Empty',
          types: 'All',
          input: false,
          check: (value, constraint) => value === null || value === undefined || value === '',
        },
        {
          value: 'is_not_empty',
          text: 'Is Not Empty',
          types: 'All',
          input: false,
          check: (value, constraint) => value !== null && value !== undefined && value !== '',
        },
      ],

      input_types: ['v-text-field', 'v-select', 'v-autocomplete', 'v-checkbox', 'dates'],
    }
  },
  computed: {
    // -----------------------------------
    // Filter Helpers
    // -----------------------------------
    combine_types() {
      // sanity check
      if ('or_only' in this.header.filters && 'and_only' in this.header.filters)
        console.warn('Both "or_only" and "and_only" are set in the header. "or_only" will be used.')

      if ('or_only' in this.header.filters) {
        return [{ text: 'Match Any', value: 'or' }]
      }
      if ('and_only' in this.header.filters) {
        return [{ text: 'Match All', value: 'and' }]
      }

      return [
        {
          text: 'Match All',
          value: 'and',
        },
        {
          text: 'Match Any',
          value: 'or',
        },
      ]
    },
    filtered_constraint_types() {
      return this.constraint_types.filter((x) => x.types === 'All' || x.types.includes(this.filters.field_type))
    },
    constraint_type_dict() {
      return this.constraint_types.reduce((acc, x) => {
        acc[x.value] = x
        return acc
      }, {})
    },
    input_component() {
      let {
        field_type = 'string',
        items = null,
        autocomplete = null,

        field_props = {},
      } = this.filters

      let props = {
        ...this.field_props,
        ...field_props,
      }

      let component = null

      if (field_type === 'boolean') {
        component = VCheckbox
      } else if (field_type === 'date') {
        component = DateField
      } else if (field_type === 'select') {
        if (autocomplete) component = VAutocomplete
        else component = VSelect
      } else {
        component = VTextField
      }

      if (items) props.items = items

      return {
        component,
        props,
      }
    },
    // -----------------------------------
    // Sorting Helpers
    // -----------------------------------
    is_sortable() {
      if ('sortable' in this.header) return this.header.sortable
      return true
    },
    sort_asc() {
      return this.field_types[this.filters.field_type].sort_asc
    },
    sort_desc() {
      return this.field_types[this.filters.field_type].sort_desc
    },
    sorting: {
      get() {
        const indx = this.options.sortBy.indexOf(this.header.value)
        if (indx > -1) {
          return this.options.sortDesc[indx]
        }
        return undefined
      },
      set(val) {
        const indx = this.options.sortBy.indexOf(this.header.value)

        if (val == undefined) {
          if (indx > -1) {
            this.options.sortBy.splice(indx, 1)
            this.options.sortDesc.splice(indx, 1)
          }
          return
        }

        if (indx > -1) {
          this.options.sortDesc.splice(indx, 0, val)
        } else {
          this.options.sortBy.push(this.header.value)
          this.options.sortDesc.push(val)
        }
      },
    },
  },
  created() {
    if (!this.field_types[this.filters.field_type]) {
      console.warn('Invalid field type', this.filters.field_type)
      this.filters.field_type = 'string'
    }

    if (!this.value) {
      let combine = 'or'

      if ('and_only' in this.filters) combine = 'and'

      this.$emit('input', {
        combine,
        rules: [],
      })
    }

    this.$nextTick(() => {
      if ('preferred_text' in this.filters) {
        this.value.preferred_text = this.filters.preferred_text
      }
      if ('formatter' in this.filters) {
        this.value.formatter = this.filters.formatter
      } else {
        this.filters.formatter = () => null
      }
    })

    // -------
    this.filters = this.header.filters
  },
  methods: {
    addRule() {
      this.value.rules.push({
        type: this.filtered_constraint_types[0]?.value,
        value: null,
      })
    },
    changeRule(rule) {
      if (this.value?.formatter) rule.format_value = this.value.formatter(rule.value)
    },
    removeRule(index) {
      this.value.rules.splice(index, 1)
    },
    // ---------
    showInput(constraint) {
      if (this.filters.field_type == 'boolean') return false

      const type = this.constraint_type_dict[constraint.type]

      if (type && type.input === false) return false

      return !!this.input_component
    },
  },
}
</script>

<style lang="scss" scoped>
.v-card {
  width: 250px;
}

.v-card__text {
  display: flex;
  flex-direction: column;

  gap: 8px;
}

.rule-wrapper {
  display: flex;
  flex-direction: column;

  gap: 8px;
}
</style>
