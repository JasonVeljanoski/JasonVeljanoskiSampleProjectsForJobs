<template>
  <initiative-lock :locked="true">
    <template #inputs>
      <editable-input
        ref="input"
        title="Owner Area/Department/Team"
        info_text="Area/Department/Team"
        :edit_only="is_new"
        required
        @edit:cancel="setUp()"
        @edit:update="$refs.input.cancel()"
      >
        <template #input:reader>
          <p>{{ selected_area }}</p>
          <p>{{ selected_department }}</p>
          <p>{{ selected_team }}</p>
        </template>

        <template #input:writer>
          <v-autocomplete
            v-model="selected_area"
            :items="areas"
            v-bind="$bind.generic"
            clearable
            hide-details
            class="mb-4"
            @click:clear="clearArea"
            @change="
              selected_department = null
              selected_team = null
            "
          />
          <v-autocomplete
            v-model="selected_department"
            :items="departments"
            v-bind="$bind.generic"
            clearable
            hide-details
            class="mb-4"
            @click:clear="clearDepartment"
            @change="selected_team = null"
          />
          <v-autocomplete
            v-model="selected_team"
            :items="teams"
            v-bind="$bind.generic"
            clearable
            hide-details
            class="mb-4"
            @change="setOrganisationalUnit"
          />
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
      selected_area: null,
      selected_department: null,
      selected_team: null,
    }
  },
  computed: {
    ...mapGetters({
      organisational_units: 'lists/getOrganisationalUnits',
    }),
    areas() {
      return this.organisational_units.map((x) => x.area).sort()
    },
    departments() {
      if (!this.selected_area) return []

      return this.organisational_units
        .filter((x) => x.area === this.selected_area)
        .map((x) => x.department)
        .sort()
    },
    teams() {
      if (!this.selected_department) return []

      return this.organisational_units
        .filter((x) => x.department === this.selected_department && x.area === this.selected_area)
        .map((x) => x.team)
        .sort()
    },
  },

  methods: {
    clearArea() {
      this.selected_department = null
      this.selected_team = null
    },
    clearDepartment() {
      this.selected_team = null
    },

    setOrganisationalUnit() {
      const single_result = this.organisational_units.find(
        (unit) =>
          unit.area === this.selected_area &&
          unit.department === this.selected_department &&
          unit.team === this.selected_team,
      )

      if (single_result) {
        this.initiative.owner_ou_id = single_result.id
        this.$emit('edit:update')
      } else {
        this.selected_area = null
        this.selected_department = null
        this.selected_team = null
      }
    },

    setUp() {
      if (this.initiative && this.initiative.owner_ou_id) {
        const ou = this.organisational_units.find((x) => x.id === this.initiative.owner_ou_id)

        this.selected_area = ou.area
        this.selected_department = ou.department
        this.selected_team = ou.team
      }
    },
  },

  watch: {
    initiative() {
      this.setUp()
    },
  },

  mounted() {
    this.setUp()
  },
}
</script>
