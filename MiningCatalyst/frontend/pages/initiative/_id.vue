<template>
  <initiative-card ref="initiative_card" :title="card_title">
    <template #card:body>
      <!-- INITIATIVE TYPE -->
      <template v-if="is_new">
        <form-input-title
          title="Initiative Type"
          :loading="loading"
          :edit_mode="is_edit"
          info_text="Specifies the type of initiative"
          required
        />

        <v-skeleton-loader v-if="loading" type="heading" class="mb-6" />
        <v-radio-group v-else v-model="edit_value.type" row mandatory>
          <v-radio
            v-for="(item, ii) in $enums.converter($enums.initiative_types)"
            :key="ii"
            :label="item.text"
            :value="item.value"
            :rules="[$form.required(edit_value.type)]"
          />
        </v-radio-group>
      </template>

      <v-card outlined>
        <!-- GROUP TABS -->
        <v-tabs v-model="group_tab">
          <v-tab v-for="(item, ii) in groups" :key="ii" :disabled="loading">
            <v-icon left>{{ item.icon }}</v-icon>
            {{ item.name }}
          </v-tab>
        </v-tabs>

        <v-card-text>
          <!-- DETAILS GROUP -->
          <!-- TITLE -->
          <editable-input
            v-show="group_tab == 0"
            ref="edit_input_title"
            title="Title"
            info_text="Brief description of initiative"
            class="input"
            :edit_only="is_new"
            :loading="loading"
            required
            @edit:update="updateEdit('title')"
            @edit:setup="setupEdit('title')"
            @edit:cancel="cancelEdit"
          >
            <template #input:reader>
              <div class="reader_text">{{ initiative.title }}</div>
            </template>

            <template #input:writer>
              <v-textarea
                v-model="edit_value.title"
                v-bind="$bind.generic"
                :rules="[$form.required(edit_value.title)]"
                no-resize
                rows="2"
              />
            </template>
          </editable-input>

          <!-- DESCRIPTION -->
          <editable-input
            v-show="group_tab == 0"
            ref="edit_input_description"
            title="Description"
            info_text="Please provide a clear problem statement or oppurtunity with a proposed solution (if known)"
            skeleton_loader_type="paragraph@2"
            class="input"
            :edit_only="is_new"
            :loading="loading"
            required
            @edit:update="updateEdit('description')"
            @edit:setup="setupEdit('description')"
            @edit:cancel="cancelEdit"
          >
            <template #input:reader>
              <div
                :class="{ markdown_light: !$vuetify.theme.dark, markdown_dark: $vuetify.theme.dark }"
                class="mb-4 mt-2 markdown"
                v-html="initiative.description"
              />
            </template>

            <template #input:writer>
              <wysiwyg-textarea
                v-model="edit_value.description"
                v-bind="$bind.generic"
                :rules="[$form.required(edit_value.description)]"
                no-resize
                rows="5"
              />
            </template>
          </editable-input>

          <!-- COLUMN FILEDS -->
          <div class="grid">
            <div>
              <editable-input
                v-show="group_tab == 0"
                ref="edit_input_date_opened"
                title="Date Opened"
                info_text="Date initiaitve started/opened"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                required
                @edit:update="updateEdit('date_opened')"
                @edit:setup="setupEdit('date_opened')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <div class="reader_text">{{ $format.date(initiative.date_opened) }}</div>
                </template>

                <template #input:writer>
                  <date-field
                    v-model="edit_value.date_opened"
                    v-bind="$bind.generic"
                    :rules="[(v) => $form.required(v), (v) => $form.date_cannot_be_in_future(v)]"
                  />
                </template>
              </editable-input>
              <editable-input
                v-show="group_tab == 0"
                ref="edit_input_target_completion_date"
                title="Target Completion Date"
                info_text="Date initiative is expected to be completed"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                required
                @edit:update="updateEdit('target_completion_date')"
                @edit:setup="setupEdit('target_completion_date')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <div class="reader_text">{{ $format.date(initiative.target_completion_date) }}</div>
                </template>

                <template #input:writer>
                  <date-field
                    v-model="edit_value.target_completion_date"
                    v-bind="$bind.generic"
                    :rules="[(v) => $form.required(v), () => noPastDateTimeRule(edit_value.target_completion_date)]"
                  />
                </template>
              </editable-input>

              <editable-input
                v-show="group_tab == 1"
                ref="edit_input_change_request"
                title="Change Request"
                info_text="Change request number"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                @edit:update="updateEdit('change_request')"
                @edit:setup="setupEdit('change_request')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <todo-box tooltip="How do we want this?" />
                </template>

                <template #input:writer>
                  <todo-box tooltip="How do we want this?" />
                </template>
              </editable-input>
            </div>
            <div>
              <editable-input
                v-show="group_tab == 0"
                ref="edit_input_project_owner_id"
                title="Project Owner"
                info_text="Person leading/responsible for initiaitve completion"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                required
                @edit:update="updateEdit('project_owner_id')"
                @edit:setup="setupEdit('project_owner_id')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <div class="reader_text">{{ $utils.getUserName(initiative.project_owner_id) }}</div>
                </template>

                <template #input:writer>
                  <server-side-user-autocomplete
                    v-model="edit_value.project_owner_id"
                    :rules="[$form.required(edit_value.project_owner_id)]"
                    v-bind="$bind.generic"
                    clearable
                    @change="autoPopulateSupervisor(edit_value.project_owner_id)"
                  />
                </template>
              </editable-input>
              <editable-input
                v-show="group_tab == 0"
                ref="edit_input_supervisor_id"
                title="Supervisor"
                info_text="Supervisor of project owner"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                required
                @edit:update="updateEdit('supervisor_id')"
                @edit:setup="setupEdit('supervisor_id')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <div class="reader_text">{{ $utils.getUserName(initiative.supervisor_id) }}</div>
                </template>

                <template #input:writer>
                  <server-side-user-autocomplete
                    v-model="edit_value.supervisor_id"
                    :rules="[$form.required(edit_value.supervisor_id)]"
                    v-bind="$bind.generic"
                    clearable
                  />
                </template>
              </editable-input>

              <editable-input
                v-show="group_tab === 1"
                ref="edit_input_notification"
                title="Notification"
                info_text="Notifications related to execution of this project"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                :required="false"
                @edit:update="updateEdit('notification')"
                @edit:setup="setupEdit('notification')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <todo-box tooltip="How do we want this?" />
                </template>

                <template #input:writer>
                  <todo-box tooltip="How do we want this?" />
                </template>
              </editable-input>
            </div>
            <div>
              <editable-input
                v-show="group_tab == 0"
                ref="edit_input_priority_id"
                title="Priority"
                info_text="Indicator of importance of this initiative"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                required
                @edit:update="updateEdit('priority_id')"
                @edit:setup="setupEdit('priority_id')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <enum-icon :value="initiative.priority" style="max-width: 150px" />
                </template>

                <template #input:writer>
                  <v-autocomplete
                    v-model="edit_value.priority_id"
                    v-bind="$bind.generic"
                    :items="priorties"
                    :rules="[$form.required(edit_value.priority_id)]"
                    clearable
                    item-text="label"
                    item-value="id"
                  />
                </template>
              </editable-input>

              <editable-input
                v-show="group_tab == 0"
                ref="edit_input_status_id"
                title="Status"
                info_text="Current stage/status in the initiative lifecycle"
                class="input"
                :edit_only="is_new"
                :loading="loading"
                required
                @edit:update="updateEdit('status_id')"
                @edit:setup="setupEdit('status_id')"
                @edit:cancel="cancelEdit"
              >
                <template #input:reader>
                  <enum-icon :value="initiative.status" enum="initiative_status" style="max-width: 150px" />
                </template>

                <template #input:writer>
                  <v-autocomplete
                    v-model="edit_value.status_id"
                    v-bind="$bind.generic"
                    :items="statuses"
                    :rules="[$form.required(edit_value.status_id)]"
                    clearable
                    item-text="label"
                    item-value="id"
                  />
                </template>
              </editable-input>
            </div>
          </div>

          <!-- ------------------------------------------- --->

          <!-- CUSTOM FILEDS SPECIFIC TO INITIATIVE TYPE SELECTED -->
          <component
            :is="initiative_component"
            :value="initiative"
            :edit_value="edit_value"
            :is_new="is_new"
            :input_view="group_tab"
            :loading="loading"
            v-bind="{ ...initiative_component_props }"
            @edit:single="updateEditSingle(true)"
            @edit:update="updateEditSingle(false)"
            @edit:cancel="updateEditSingle(false)"
          />
        </v-card-text>
      </v-card>
    </template>

    <template #card:footer>
      <ul v-if="is_edit || is_edit_single">
        <li v-for="item in legend" :key="item.text"><span class="mr-1">*</span><span v-html="item.text" /></li>
      </ul>
      <v-spacer />
      <v-btn v-if="is_edit" :disabled="loading" v-bind="$bind.btn" @click="submit">
        <v-icon left>mdi-content-save</v-icon>
        {{ save_button_text }}
      </v-btn>
    </template>
  </initiative-card>
</template>

<script>
// vue imports
import { mapGetters } from 'vuex'
import { defineComponent } from 'vue'
import { useApiRouter } from '~/client'

// initiative types imports
import GeneralImprovmentForm from '@/components/test/GeneralImprovementForm.vue'
import MaintenanceImprovementForm from '@/components/initiative/form/types/MaintenanceImprovementForm.vue'
import MaintenanceProjectForm from '@/components/initiative/form/types/MaintenanceProjectForm.vue'
import NonFlocSpecificForm from '@/components/initiative/form/types/NonFlocSpecificForm.vue'
import CostReductionForm from '@/components/initiative/form/types/CostReductionForm.vue'
import SafetyForm from '@/components/initiative/form/types/SafetyForm.vue'
import CapitalForm from '@/components/initiative/form/types/CapitalForm.vue'

// helper imports
import InitiativeCard from '@/components/initiative/form/InitiativeCard.vue'
import EditableInput from '@/components/test/EditableInput.vue'
import WysiwygTextarea from '@/components/utils/WysiwygTextarea.vue'
import DateField from '@/components/enco/DateField.vue'
import EnumIcon from '@/components/enco/EnumIcon.vue'
import TodoBox from '@/components/utils/TodoBox.vue'

const { InitiativeRouter } = useApiRouter()

export default defineComponent({
  components: {
    // initiative types imports
    GeneralImprovmentForm,
    MaintenanceImprovementForm,
    MaintenanceProjectForm,
    NonFlocSpecificForm,
    CostReductionForm,
    SafetyForm,
    CapitalForm,

    // helper imports
    InitiativeCard,
    EditableInput,
    WysiwygTextarea,
    DateField,
    EnumIcon,
    TodoBox,
  },
  data() {
    return {
      // states
      is_new: false,
      is_edit: false,
      is_edit_single: false,

      // initiative
      initiative: null, // used as master for editing
      edit_value: null, // used for edit version or create initiative

      // form group
      group_tab: 0,
      groups: [
        { name: 'details', icon: 'mdi-information-outline' },
        { name: 'references', icon: 'mdi-text-box-search-outline' },
        { name: 'benefit', icon: 'mdi-currency-usd' },
      ],

      // constants
      initiative_component_props: {},
      legend: [
        { text: '<span>Required fields are marked with a <span style="color: red;">RED</span> asterisk ( * )</span>' },
        // { text: 'Fields with a blue background are editable', color: 'blue' },
      ],
    }
  },
  computed: {
    ...mapGetters({
      users: 'lists/getUsers',
      priorties: 'enums/getPriorities',
      statuses: 'enums/getStatuses',
    }),
    initiative_id() {
      const id = this.$route.params.id
      if (id === 'new') return -1
      return parseInt(id)
    },
    // ----------------------------------
    // FORM HELPERS
    // ----------------------------------
    initiative_component() {
      switch (this.edit_value?.type) {
        case 'general_improvement':
          return GeneralImprovmentForm
        case 'non_floc_specific':
          return NonFlocSpecificForm
        case 'maintenance_improvement':
          return MaintenanceImprovementForm
        case 'maintenance_project':
          return MaintenanceProjectForm
        case 'cost_reduction':
          return CostReductionForm
        case 'safety':
          return SafetyForm
        case 'capital':
          return CapitalForm
      }
      return null
    },
    loading() {
      return !this.initiative
    },
    card_title() {
      if (this.is_new) return 'New Initiative'
      else if (this.is_edit) return 'Edit Initiative'

      return `${this.$enums.initiative_types[this.initiative?.type]} Initiative`
    },
    save_button_text() {
      return this.is_new ? 'Create' : 'Save'
    },
  },
  created() {
    if (this.initiative_id === -1) this.is_new = true
    if (this.is_new) this.is_edit = true

    // ----------------------------------

    this.initInitiative()
  },
  methods: {
    // ----------------------------------
    // INIT
    // ----------------------------------
    initEditValue() {
      // todo: could make this better...
      // setup edit value with empty initiative
      this.$axios.$get('/initiative', { params: { id: this.initiative_id } }).then((res) => {
        this.edit_value = res
      })
    },
    initInitiative() {
      const id = this.initiative_id == 'new' ? -1 : this.initiative_id

      // todo: could make this better...
      // setup edit value with empty initiative
      // this.initEditValue()

      // setup initiative with data
      this.$axios.$get('/initiative', { params: { id } }).then((res) => {
        this.formatDates(res)
        this.initiative = res
        this.edit_value = JSON.parse(JSON.stringify(res))

        // setup new initiative auto-fields
        if (this.is_new) {
          this.autoFillNewInitiative()
        }
      })
    },
    // ----------------------------------
    // EDIT
    // ----------------------------------
    setupEdit(key) {
      this.edit_value[key] = this.initiative[key]
      this.is_edit_single = true
    },
    updateEdit(key) {
      if (this.$refs.initiative_card.$refs.form.validate()) {
        this.initiative[key] = this.edit_value[key]

        InitiativeRouter.updateInitiative(this.initiative).then((res) => {
          // update initiative
          this.formatDates(res)
          this.initiative = res
          this.is_edit = false
          this.is_edit_single = false

          // reset edit value
          this.initEditValue()

          // close edit mode
          const ref_key = `edit_input_${key}`
          this.$refs[ref_key].cancel()

          // push notification
          this.$snackbar.add('Initiative Edited Successfully')
        })
      }
    },
    cancelEdit() {
      this.initEditValue()
      this.is_edit_single = false
    },
    updateEditSingle(flag) {
      this.is_edit_single = flag
    },
    // ----------------------------------
    // SAVE
    // ----------------------------------
    submit() {
      if (this.$refs.initiative_card.$refs.form.validate()) {
        InitiativeRouter.updateInitiative(this.edit_value).then((res) => {
          // update initiative
          this.formatDates(res)
          this.initiative = res
          this.is_new = false

          // push notification
          this.$snackbar.add('Initiative Created Successfully')

          // re-route
          this.$router.push(`/initiative/${res.id}`)
        })
      }
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
    autoFillNewInitiative() {
      // dates
      this.initiative.date_opened = this.$format.initDate(new Date())

      // owner & supervisor
      this.initiative.project_owner_id = this.$auth.user.id
      this.initiative.supervisor_id = this.$auth.user.supervisor_id

      // status
      this.initiative.status_id = this.statuses.find((x) => x.label === 'Definition').id
    },
    autoPopulateSupervisor(uid) {
      // todo: fix this
      console.log('todo: autoPopulateSupervisor', uid)
      // if (!uid) return

      // this.$axios.$get('/user/supervisor', { params: { user_id: uid } }).then((res) => {
      //   this.initiative.supervisor_id = res.id
      // })
    },
    // ----------------------------------
    // RULE HELPERS
    // ----------------------------------
    noPastDateTimeRule(datetime) {
      // this method is required when editing an initiative in the future
      // i.e. the future will become the past; so must remove the rule

      if (this.initiative?.id) return

      // only if new initiative
      return this.$form.date_cannot_be_in_past(datetime)
    },
  },
})
</script>

<style lang="scss" scoped>
.reader_text {
  display: flex;
  align-items: center;

  font-size: 12pt;
  height: 40px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-gap: 1rem;
}

ul {
  list-style-type: none;
  padding-left: 10px !important;
  font-size: 10pt;
}

.input {
  margin-bottom: 20px;
}
</style>
