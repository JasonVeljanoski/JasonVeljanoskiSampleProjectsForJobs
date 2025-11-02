<template>
  <v-form ref="form">
    <div class="grid">
      <div>
        <editable-input
          v-show="input_view === 0"
          ref="edit_input_parent_initiative_id"
          title="Parent Initiative"
          info_text="The existing initiative that this initiative is a part of"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          :required="false"
          @edit:update="updateEdit('parent_initiative_id')"
          @edit:setup="setupEdit('parent_initiative_id')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <todo-box tooltip="How do we want this?" />
            <!-- <div class="reader_text">{{ value.parent_initiative_id ?? 'No Value' }}</div> -->
          </template>

          <template #input:writer>
            <todo-box tooltip="How do we want this?" />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 2"
          ref="edit_input_primary_driver_id"
          title="Primary Driver"
          info_text="Primary driver for pursuing this initiative"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          :input_view="2"
          @edit:update="updateEdit('primary_driver_id')"
          @edit:setup="setupEdit('primary_driver_id')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <enum-icon :value="value.primary_driver" style="max-width: 180px" />
          </template>

          <template #input:writer>
            <v-autocomplete
              v-model="edit_value.primary_driver_id"
              v-bind="$bind.generic"
              :items="primary_drivers"
              :rules="[
                (v) => v == null || v != value.secondary_driver_id || 'Cannot select the same driver as secondary',
              ]"
              clearable
              item-text="label"
              item-value="id"
            />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 2"
          ref="edit_input_secondary_driver_id"
          title="Secondary Driver"
          info_text="Secondary driver for pursuing iniaitive"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          :input_view="2"
          @edit:update="updateEdit('secondary_driver_id')"
          @edit:setup="setupEdit('secondary_driver_id')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <enum-icon :value="value.secondary_driver" style="max-width: 180px" />
          </template>

          <template #input:writer>
            <v-autocomplete
              v-model="edit_value.secondary_driver_id"
              v-bind="$bind.generic"
              :items="secondary_drivers"
              :rules="[(v) => v == null || v != value.primary_driver_id || 'Cannot select the same driver as primary']"
              clearable
              item-text="label"
              item-value="id"
            />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 2"
          ref="edit_input_tonnes"
          title="Tonnes"
          info_text="Total tonnes expected to be added due to initiative"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          :required="false"
          @edit:update="updateEdit('tonnes')"
          @edit:setup="setupEdit('tonnes')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <div class="reader_text">{{ $format.commarize(value.tonnes) ?? 'No Value' }}</div>
          </template>

          <template #input:writer>
            <e-comma-input
              v-model="edit_value.tonnes"
              v-bind="$bind.generic"
              :rules="[]"
              clearable
              hide-details="auto"
            />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 1"
          ref="edit_input_workorder"
          title="Work Order"
          info_text="Work orders from input notification numbers"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          @edit:update="updateEdit('workorder')"
          @edit:setup="setupEdit('workorder')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <todo-box tooltip="How do we want this?" />
          </template>

          <template #input:writer>
            <todo-box tooltip="How do we want this?" />
          </template>
        </editable-input>

        <form-owner
          v-show="input_view === 0"
          :initiative="edit_value"
          :loading="loading"
          :is_new="is_new"
          @edit:update="updateEdit('owner_ou_id')"
        />
      </div>
      <div>
        <editable-input
          v-show="input_view == 0"
          ref="edit_input_triggers"
          title="Trigger"
          info_text="Indicator of why the initiative is being undertaken"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          required
          @edit:update="updateEdit('triggers')"
          @edit:setup="setupEdit('triggers')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <enum-icons :value="value.triggers" />
          </template>

          <template #input:writer>
            <v-autocomplete
              v-model="edit_value.trigger_ids"
              v-bind="$bind.generic"
              :items="triggers"
              :rules="[$form.arr_non_empty(edit_value.trigger_ids)]"
              clearable
              multiple
              item-text="label"
              item-value="id"
            />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 2"
          ref="edit_input_safety"
          title="Safety"
          info_text="Number of safety events due to problem"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          :required="false"
          @edit:update="updateEdit('safety')"
          @edit:setup="setupEdit('safety')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <div class="reader_text">{{ $format.commarize(value.safety) ?? 'No Value' }}</div>
          </template>

          <template #input:writer>
            <e-comma-input
              v-model="edit_value.safety"
              v-bind="$bind.generic"
              :rules="[]"
              clearable
              hide-details="auto"
            />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 2"
          ref="edit_input_availability"
          title="Availability (hrs)"
          info_text="Total availability (in hours) lost that the problem initiative is addressing"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          :required="false"
          @edit:update="updateEdit('availability')"
          @edit:setup="setupEdit('availability')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <div class="reader_text">{{ $format.commarize(value.availability) ?? 'No Value' }}</div>
          </template>

          <template #input:writer>
            <e-comma-input
              v-model="edit_value.availability"
              v-bind="$bind.generic"
              :rules="[]"
              clearable
              hide-details="auto"
            />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 2"
          ref="edit_input_events"
          title="Events"
          info_text="Total number of events that the problem initiative is addressing"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          :required="false"
          @edit:update="updateEdit('events')"
          @edit:setup="setupEdit('events')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <div class="reader_text">{{ $format.commarize(value.events) ?? 'No Value' }}</div>
          </template>

          <template #input:writer>
            <e-comma-input
              v-model="edit_value.events"
              v-bind="$bind.generic"
              :rules="[]"
              clearable
              hide-details="auto"
            />
          </template>
        </editable-input>

        <form-impact
          v-show="input_view === 0"
          :initiative="edit_value"
          :loading="loading"
          :is_new="is_new"
          @edit:update="updateEdit('impact_ou_id')"
        />
      </div>

      <div>
        <editable-input
          v-show="input_view === 2"
          ref="edit_input_cost_benefit_category_id"
          title="Cost Benefit Category"
          info_text="Indicates whether the indicated cost saving is expected to impact CAPEX or OPEX budgets"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          required
          @edit:update="updateEdit('cost_benefit_category_id')"
          @edit:setup="setupEdit('cost_benefit_category_id')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <enum-icon :value="value.cost_benefit_category" style="max-width: 100px" />
          </template>

          <template #input:writer>
            <v-autocomplete
              v-model="edit_value.cost_benefit_category_id"
              v-bind="$bind.generic"
              :items="cost_benefit_categories"
              :rules="[() => $form.required(edit_value.cost_benefit_category_id)]"
              clearable
              item-text="label"
              item-value="id"
            />
          </template>
        </editable-input>

        <editable-input
          v-show="input_view === 2"
          ref="edit_input_benefit_frequency_id"
          title="Benefit Frequency"
          info_text="How often the benefit will be seen"
          class="input"
          :edit_only="is_new"
          :loading="loading"
          required
          @edit:update="updateEdit('benefit_frequency_id')"
          @edit:setup="setupEdit('benefit_frequency_id')"
          @edit:cancel="cancelEdit"
        >
          <template #input:reader>
            <enum-icon :value="value.benefit_frequency" style="max-width: 100px" />
          </template>

          <template #input:writer>
            <v-autocomplete
              v-model="edit_value.benefit_frequency_id"
              v-bind="$bind.generic"
              :items="benefit_frequencies"
              :rules="[() => $form.required(edit_value.benefit_frequency_id)]"
              clearable
              item-text="label"
              item-value="id"
            />
          </template>
        </editable-input>
      </div>
    </div>

    <editable-input
      v-show="input_view == 2"
      ref="edit_input_benefit_estimate_notes"
      title="Estimate Notes"
      info_text="Brief description of how the estimated benefit of the initiative was reached"
      class="input"
      :edit_only="is_new"
      :loading="loading"
      required
      @edit:update="updateEdit('benefit_estimate_notes')"
      @edit:setup="setupEdit('benefit_estimate_notes')"
      @edit:cancel="cancelEdit"
    >
      <template #input:reader>
        <div class="reader_text">{{ value.benefit_estimate_notes }}</div>
      </template>

      <template #input:writer>
        <v-textarea
          v-model="edit_value.benefit_estimate_notes"
          v-bind="$bind.generic"
          :rules="[$form.required(edit_value.benefit_estimate_notes)]"
          no-resize
          rows="4"
        />
      </template>
    </editable-input>
  </v-form>
</template>

<script>
import { mapGetters } from 'vuex'
import { useApiRouter } from '~/client'

import EditableInput from '@/components/test/EditableInput.vue'
import TodoBox from '@/components/utils/TodoBox.vue'
import EnumIcons from '@/components/utils/EnumIcons.vue'
import EnumIcon from '@/components/enco/EnumIcon.vue'

import FormImpact from '@/components/form/FormImpact.vue'
import FormOwner from '@/components/form/FormOwner.vue'

const { InitiativeRouter } = useApiRouter()

export default {
  components: {
    EditableInput,
    TodoBox,
    EnumIcons,
    EnumIcon,
    FormImpact,
    FormOwner,
  },
  props: {
    value: { type: Object },
    edit_value: { type: Object },
    is_new: { type: Boolean, default: false },
    input_view: { type: Number, default: 0 },
    loading: { type: Boolean, default: false },
  },
  computed: {
    ...mapGetters({
      triggers: 'enums/getTriggers',
      primary_drivers: 'enums/getPrimaryDrivers',
      secondary_drivers: 'enums/getSecondaryDrivers',
      cost_benefit_categories: 'enums/getCostBenefitCategories',
      benefit_frequencies: 'enums/getBenefitFrequencies',
    }),
  },
  methods: {
    // ----------------------------------
    // EDIT
    // ----------------------------------
    setupEdit(key) {
      this.edit_value[key] = this.value[key]
      this.$emit('edit:single')
    },
    updateEdit(key) {
      if (this.$refs.form.validate()) {
        this.value[key] = this.edit_value[key]

        InitiativeRouter.updateInitiative(this.edit_value).then((res) => {
          // update initiative
          this.formatDates(res)

          // update this.value but at same memory location to avoid mutating prop
          Object.assign(this.value, res)

          // reset edit value
          Object.assign(this.edit_value, this.value)

          // emit
          this.$emit('edit:update')

          // close edit mode
          const ref_key = `edit_input_${key}`
          this.$refs[ref_key].cancel()

          // push notification
          this.$snackbar.add('Initiative Edited Successfully')
        })
      }
    },
    cancelEdit() {
      this.$emit('edit:cancel')
    },
    // ----------------------------------
    // HELPERS
    // ----------------------------------
    formatDates(initiative) {
      const date_fields = ['date_opened', 'target_completion_date']
      date_fields.forEach((field) => {
        if (initiative[field]) initiative[field] = this.$format.initDate(initiative[field])
      })
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
