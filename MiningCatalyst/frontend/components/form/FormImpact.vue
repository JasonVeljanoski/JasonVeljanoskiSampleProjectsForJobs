<template>
  <initiative-lock :locked="false" :loading="loading.area || loading.department">
    <template #inputs>
      <editable-input info_text="Area" title="Impact Area" :edit_only="is_new">
        <template #input:reader>
          {{ selected_areas }}
        </template>

        <template #input:writer>
          <initiative-input
            ref="area"
            v-model="selected_areas"
            :parent_ref="$refs.department"
            class="mb-4"
            item-text="area"
            url="/lists/organisational_units/search/area"
            @get:children="fromAreaSetDepartments"
            @loading:start="$set(loading, 'area', true)"
            @loading:end="$set(loading, 'area', false)"
          >
            <template #chip-text="{ item }">
              {{ item.area }}
            </template>

            <template #item="{ item }">
              <v-list-item-content>
                <v-list-item-title> {{ item.area }} </v-list-item-title>
              </v-list-item-content>
            </template>
          </initiative-input>
        </template>
      </editable-input>

      <editable-input info_text="Department" title="Department" :edit_only="is_new">
        <template #input:reader>
          {{ selected_departments }}
        </template>

        <template #input:writer>
          <initiative-input
            ref="department"
            v-model="selected_departments"
            :parent_ref="$refs.area"
            class="mb-4"
            item-text="department"
            url="/lists/organisational_units/search/department"
            @get:children="fromDepartmentSetAreas"
            @loading:start="$set(loading, 'department', true)"
            @loading:end="$set(loading, 'department', false)"
          >
            <template #chip-text="{ item }">
              {{ item.department }}
            </template>

            <template #item="{ item }">
              <v-list-item-content>
                <v-list-item-title> {{ item.department }} </v-list-item-title>
              </v-list-item-content>
            </template>
          </initiative-input>
        </template>
      </editable-input>
    </template>
  </initiative-lock>
</template>

<script>
import { mapGetters } from 'vuex'

import EditableInput from '@/components/test/EditableInput.vue'

import InitiativeLock from '@/components/initiative/InitiativeLock.vue'
import InitiativeInput from '@/components/initiative/InitiativeInput.vue'

export default {
  components: {
    EditableInput,
    InitiativeLock,
    InitiativeInput,
  },
  props: {
    initiative: { type: Object },
    is_new: Boolean,
  },

  data() {
    return {
      loading: {},

      selected_areas: [],
      selected_departments: [],
    }
  },

  computed: {
    ...mapGetters({
      organisational_units: 'lists/getOrganisationalUnits',
    }),

    selected_areas_str() {
      return this.selected_areas.map((x) => x.area)
    },
    selected_departments_str() {
      return this.selected_departments.map((x) => x.department)
    },
  },

  methods: {
    fromAreaSetDepartments() {
      const setTo = this.selected_areas.reduce((acc, s) => {
        return [...acc, ...this.organisational_units.filter((x) => x.area === s.area)]
      }, [])
      this.$refs.department.setData(setTo)
    },
    fromDepartmentSetAreas() {
      const setTo = this.selected_departments.reduce((acc, s) => {
        return [...acc, ...this.organisational_units.filter((x) => x.department === s.department)]
      }, [])
      this.$refs.area.setData(setTo)
    },

    clearArea() {
      this.selected_department = null
      this.selected_team = null
    },
    clearDepartment() {
      this.selected_team = null
    },

    setOrganisationalUnit() {
      const selected_ids = this.organisational_units
        .filter(
          (unit) =>
            this.selected_areas_str.includes(unit.area) &&
            (!this.selected_departments_str.length || this.selected_departments_str.includes(unit.department)) &&
            unit.team == null,
        )
        .map((unit) => unit.id)

      const results = this.organisational_units.filter((unit) => selected_ids.includes(unit.id))

      if (results.length === 1) {
        this.initiative.impact_ou_id = results[0].id
        this.$emit('edit:update')
      }
    },
  },

  watch: {
    selected_areas() {
      this.setOrganisationalUnit()
    },
    selected_departments() {
      this.setOrganisationalUnit()
    },
  },
}
</script>
