<template>
  <div v-if="value.general_improvement">
    <!-- COLUMNS -->
    <div class="grid">
      <div v-for="(col, ii) in columns" :key="ii">
        <div v-for="(item, jj) in col" :key="jj">
          <div v-show="item.input_view == input_view">
            <!-- FIELD TITLE -->
            <form-input-title
              :title="item.text"
              :loading="loading"
              :edit_mode="is_edit"
              :required="item.required"
              :info_text="item?.info_text"
            />

            <!-- WRITE COMPONENT -->
            <component
              :is="item.write_component.component"
              v-if="is_edit"
              v-model="value.general_improvement[item.value]"
              v-bind="{ ...$bind.generic, ...item.write_component.props }"
              :all_items="item.write_component.props?.items"
              :rules="item.write_component.props?.rules"
            />

            <!-- READ COMPONENT -->
            <div v-else>
              <component
                :is="item.read_component.component"
                v-if="item?.read_component?.component"
                :value="item.read_component.value ?? value[item.value]"
                v-bind="{ ...$bind.generic, ...item.read_component.props }"
              />
              <v-text-field
                v-else
                :value="applyFormatter(value.general_improvement[item.value], item.read_component?.formatter)"
                v-bind="$bind.readonly_input"
                hide-details
                v-on="$listeners"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TEXT -->
    <div v-show="input_view == 2">
      <form-input-title
        title="Estimate Notes"
        :loading="loading"
        :edit_mode="is_edit"
        info_text="Brief description of how the estimated benefit of the initiative was reached"
        required
      />
      <v-textarea
        v-model="value.general_improvement.benefit_estimate_notes"
        v-bind="bind_options"
        :rules="[$form.required(value.general_improvement?.benefit_estimate_notes)]"
        no-resize
        rows="5"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import { VAutocomplete } from 'vuetify/lib'
import CommaInput from '@/components/enco/CommaInput.vue'
import EnumIcon from '@/components/enco/EnumIcon.vue'
import EnumIcons from '@/components/utils/EnumIcons.vue'
import TodoBox from '@/components/utils/TodoBox.vue'

export default {
  props: {
    value: { type: Object },
    input_view: { type: Number, default: 1 },
    is_edit: { type: Boolean, default: false },
  },
  computed: {
    ...mapGetters({
      triggers: 'enums/getTriggers',
      primary_drivers: 'enums/getPrimaryDrivers',
      secondary_drivers: 'enums/getSecondaryDrivers',
      cost_benefit_categories: 'enums/getCostBenefitCategories',
    }),
    loading() {
      return this.value === null
    },
    bind_options() {
      return this.is_edit ? this.$bind.generic : this.$bind.readonly_input
    },

    columns() {
      return {
        1: [
          {
            text: 'Parent Initiative',
            value: 'parent_initiative_id',
            required: false,
            info_text: 'The existing initiative that this initiative is a part of',
            input_view: 0,
            write_component: {
              component: TodoBox,
              props: { tooltip: 'How do we want this?' },
            },
            read_component: {
              component: TodoBox,
              props: { tooltip: 'How do we want this?' },
            },
          },
          {
            text: 'Change Request',
            value: 'change_request',
            required: false,
            info_text: 'Change request number for this initiative',
            input_view: 1,
            write_component: {
              component: TodoBox,
              props: { tooltip: 'How do we want this?' },
            },
            read_component: {
              component: TodoBox,
              props: { tooltip: 'How do we want this?' },
            },
          },
          {
            text: 'Primary Driver',
            value: 'primary_driver_id',
            required: false,
            info_text: 'Primary driver for pursuing this initiative',
            input_view: 2,
            write_component: {
              component: VAutocomplete,
              props: {
                items: this.primary_drivers,
                itemText: 'label',
                itemValue: 'id',
                clearable: true,
                rules: [],
              },
            },
            read_component: {
              component: EnumIcon,
              value: this.value.general_improvement?.primary_driver,
              props: { style: { maxWidth: ' 200px' } },
            },
          },
          {
            text: 'Secondary Driver',
            value: 'secondary_driver_id',
            required: false,
            info_text: 'Secondary driver for pursuing iniaitive',
            input_view: 2,
            write_component: {
              component: VAutocomplete,
              props: {
                items: this.secondary_drivers,
                itemText: 'label',
                itemValue: 'id',
                clearable: true,
                rules: [
                  (v) =>
                    v == null ||
                    v != this.value.general_improvement.primary_driver_id ||
                    'Cannot select the same driver as primary',
                ],
              },
            },
            read_component: {
              component: EnumIcon,
              value: this.value.general_improvement?.secondary_driver,
              props: { style: { maxWidth: ' 200px' } },
            },
          },
          {
            text: 'Tonnes',
            value: 'tonnes',
            required: false,
            info_text: 'Total tonnes expected to be added due to initiative',
            input_view: 2,
            write_component: {
              component: CommaInput,
              props: { clearable: true, hideDetails: true, rules: [] },
            },
            read_component: {
              formatter: (value) => {
                return value ? `${this.$format.commarize(value)}` : 'No Value'
              },
            },
          },
        ],
        2: [
          {
            text: 'Triggers',
            value: 'trigger_ids',
            required: true,
            info_text: 'Indicator of why the initiative is being undertaken',
            input_view: 0,
            write_component: {
              component: VAutocomplete,
              props: {
                items: this.triggers,
                itemText: 'label',
                itemValue: 'id',
                multiple: true,
                clearable: true,
                rules: [() => this.$form.arr_non_empty(this.value.general_improvement?.trigger_ids)],
              },
            },
            read_component: {
              component: EnumIcons,
              value: this.value.general_improvement?.triggers,
            },
          },
          {
            text: 'Notification',
            value: 'notification',
            required: false,
            info_text: 'Notifications related to execution of this project',
            input_view: 1,
            write_component: {
              component: TodoBox,
              props: { tooltip: 'Where do I get this data from?' },
            },
            read_component: {
              component: TodoBox,
              props: { tooltip: 'Where do I get this data from?' },
            },
          },
          {
            text: 'Safety',
            value: 'safety',
            required: false,
            info_text: 'Number of safety events due to problem',
            input_view: 2,
            write_component: {
              component: CommaInput,
              props: { clearable: true, hideDetails: true, rules: [] },
            },
            read_component: {
              formatter: (value) => {
                return value ? `${this.$format.commarize(value)}` : 'No Value'
              },
            },
          },
          {
            text: 'Availability (hrs)',
            value: 'availability',
            required: false,
            info_text: 'Total availability (in hours) lost that the problem initiative is addressing',
            input_view: 2,
            write_component: {
              component: CommaInput,
              props: { clearable: true, hideDetails: true, rules: [] },
            },
            read_component: {
              formatter: (value) => {
                return value ? `${this.$format.commarize(value)}` : 'No Value'
              },
            },
          },
          {
            text: 'Events',
            value: 'events',
            required: false,
            info_text: 'Total number of events that the problem initiative is addressing',
            input_view: 2,
            write_component: {
              component: CommaInput,
              props: { clearable: true, hideDetails: true, rules: [] },
            },
            read_component: {
              formatter: (value) => {
                return value ? `${this.$format.commarize(value)}` : 'No Value'
              },
            },
          },
        ],
        3: [
          {
            text: 'Cost Benefit Category',
            value: 'cost_benefit_category_id',
            required: true,
            info_text: 'Indicates whether the indicated cost saving is expected to impact CAPEX or OPEX budgets',
            input_view: 2,
            write_component: {
              component: VAutocomplete,
              props: {
                items: this.cost_benefit_categories,
                itemText: 'label',
                itemValue: 'id',
                clearable: true,
                rules: [() => this.$form.required(this.value.general_improvement?.cost_benefit_category_id)],
              },
            },
            read_component: {
              component: EnumIcon,
              value: this.value.general_improvement?.cost_benefit_category,
              props: { style: { maxWidth: ' 100px' } },
            },
          },
          {
            text: 'Benefit Frequency',
            value: 'benefit_frequency',
            required: true,
            input_view: 2,
            info_text: 'How often the benefit will be seen',
            write_component: {
              component: TodoBox,
              props: { tooltip: 'What is this? What set list do I use?' },
            },
            read_component: {
              component: TodoBox,
              props: { tooltip: 'What is this? What set list do I use?' },
            },
          },
          {
            text: 'Work Order',
            value: 'workorder',
            required: false,
            info_text: 'Work orders from input notification numbers',
            input_view: 1,
            write_component: {
              component: TodoBox,
              props: { tooltip: 'Where do I get this data from? Does this auto-populate from Notis selected?' },
            },
            read_component: {
              component: TodoBox,
              props: { tooltip: 'Where do I get this data from? Does this auto-populate from Notis selected?' },
            },
          },
        ],
      }
    },
  },
  created() {
    if (this.value.general_improvement === null) {
      this.$axios.$get('/initiative/general_improvement', { params: { id: -1 } }).then((res) => {
        this.value.general_improvement = res
      })
    }
  },
  methods: {
    applyFormatter(value, formatter) {
      if (formatter) return formatter ? formatter(value) : value
      return value ?? 'No Value'
    },
  },
}
</script>

<style lang="scss" scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-gap: 1rem;
}
</style>
