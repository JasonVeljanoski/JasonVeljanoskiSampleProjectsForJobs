<template>
  <v-card outlined>
    <v-subheader class="d-flex justify-space-between">
      ACTIONS
      <div class="d-flex" style="gap: 8px">
        <v-btn
          v-if="!add_mode"
          v-bind="$bind.btn"
          :disabled="!$workgroup_perms.canEdit(workgroup.owner_id, workgroup.admin_ids)"
          @click="toggleAddMode"
        >
          <v-icon left>mdi-import</v-icon>
          Import Action
        </v-btn>
        <v-autocomplete
          v-else
          ref="input"
          v-model="selected_action"
          :items="action_titles"
          v-bind="$bind.select"
          return-object
          autofocus
          dense
          :append-icon="selected_action ? 'mdi-content-save' : 'mdi-menu-down'"
          item-text="title"
          placeholder="Start typing the action title..."
          @click:append="handleAddAction"
          @click:clear="toggleAddMode"
          @blur="toggleAddMode"
          @keypress.enter="handleAddAction"
        >
          <template #item="{ item }">
            <privacy-enum-icon :value="item.privacy" />
            <span class="ml-2">{{ item.title }}</span>
          </template>
        </v-autocomplete>
        <v-btn
          v-bind="$bind.btn"
          :disabled="!$workgroup_perms.canEdit(workgroup.owner_id, workgroup.admin_ids)"
          @click="handleCreateAction()"
        >
          <v-icon left>mdi-pencil</v-icon>
          new ace action
        </v-btn>
        <slot name="card:header" />
      </div>
    </v-subheader>

    <v-divider />

    <v-card-text v-if="!is_loading && workgroup.actions?.length == 0" class="my-2"> No actions. </v-card-text>

    <e-data-table
      v-else
      :loading="is_loading"
      :headers="headers"
      :items="sorted_actions"
      fixed-header
      hide-default-footer
      :options="{
        itemsPerPage: 100,
      }"
      dense
      class="action-table"
    >
      <template #item.id="{ item }">
        <e-icon-btn
          tooltip="Edit Action"
          :disabled="!$workgroup_perms.canEdit(workgroup.owner_id, workgroup.admin_ids)"
          @click="handleCreateAction(item)"
        >
          mdi-pencil
        </e-icon-btn>
      </template>
      <template #item.title="{ item }">
        <v-tooltip bottom max-width="300">
          <template #activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">{{ item.title }}</span>
          </template>
          <span>{{ item.description }}</span>
        </v-tooltip>
      </template>

      <template #item.link="{ item }">
        <e-icon-btn :href="item.link" target="_blank">mdi-link-variant</e-icon-btn>
      </template>
    </e-data-table>

    <!-- DIALOGS -->
    <create-update-action-form ref="action_form" />
  </v-card>
</template>

<script>
import CreateUpdateActionForm from '@/components/Action/CreateUpdateActionForm.vue'
import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'

export default {
  components: {
    CreateUpdateActionForm,
    PrivacyEnumIcon,
  },
  props: {
    workgroup: { type: Object },
    loading: { type: Boolean, default: false },
  },
  data() {
    return {
      local_loading: false,
      add_mode: false,
      selected_action: null,
      action_titles: [],
      headers: this.$table_headers.action_simple,
    }
  },
  computed: {
    sorted_actions() {
      const actions = [...this.workgroup.actions]
      // sort by priority, status then date_due
      return actions.sort((a, b) => {
        if (a.priority != b.priority) {
          return a.priority - b.priority
        } else if (a.status != b.status) {
          return a.status - b.status
        } else {
          return a.date_due - b.date_due
        }
      })
    },
    is_loading() {
      return this.local_loading || this.loading
    },
  },
  mounted() {
    this.getActionTitles()
  },
  methods: {
    getActionTitles() {
      this.$axios
        .$get('/privacy/action_titles')
        .then((res) => {
          this.action_titles = res
        })
        .catch((err) => console.error(err))
    },
    toggleAddMode() {
      this.add_mode = !this.add_mode

      this.$nextTick(() => {
        if (this.add_mode) {
          this.getActionTitles()
          this.$refs.input.activateMenu()
        } else {
          this.selected_action = null
        }
      })
    },
    // -----------------------------
    // APPEND ACTION HANDLERS
    // -----------------------------
    appendActionToWorkgroup() {
      this.$axios
        .$patch('/action/append_action_to_workgroup', null, {
          params: {
            action_id: this.selected_action.id,
            workgroup_id: this.workgroup.id,
            workgroup_privacy: this.workgroup.privacy,
            action_privacy: this.selected_action.privacy,
            return_action_response: true,
          },
        })
        .then((res) => {
          if (res) {
            this.workgroup.actions.push(res)

            // must trigger data reload due to permission changes affecting what actions are available to each group
            this.$emit('trigger_reload')
            this.$snackbar.add(`Action was successfully added to the group`)
          }
          // reset
          this.selected_action = null
          this.add_mode = false
        })
        .catch((err) => console.error(err))
    },
    handleAddAction() {
      let message = 'Are you sure you want to append this action to the group? '
      if (this.workgroup.privacy == 1 && this.selected_action.privacy == 1) {
        message += 'Any public action can be appended to any public group.'
      } else {
        message += `Confirming will remove this action from all other groups as well as changing the privacy accordingly if needed.`
      }

      if (this.selected_action && confirm(message)) {
        // you cannot add the same action twice to a single workgroup
        const res = this.workgroup.actions.filter((x) => x.id == this.selected_action.id)
        if (res.length > 0) {
          this.$snackbar.add(`Action already exists in Group`, 'warning')
          return
        }

        // add action to workgroup
        this.appendActionToWorkgroup()
      } else {
        // reset
        this.selected_action = null
        this.add_mode = false
      }
    },
    // -----------------------------
    // CREATE NEW ACTION
    // -----------------------------
    handleCreateAction(item = null) {
      this.$refs.action_form
        .open(item)
        .then((res) => {
          // dialog cancelled
          if (res == false) return

          // handle res from submit
          this.createUpdateAction(res)
        })
        .catch((err) => console.error(err))
    },
    createUpdateAction(payload) {
      this.local_loading = true

      const form_data = new FormData()
      const action = payload.action

      // SET PRIVACY OF ACTION DEPENDING ON WORKGROUP PRIVACY
      if (this.workgroup.privacy == 1) action.privacy = 1
      else if (this.workgroup.privacy == 3) action.privacy = 3

      // ---------

      const attachments = payload.attachments

      for (const x of attachments) form_data.append('attachments', x.file)
      form_data.append('action', JSON.stringify(action))

      this.$axios
        .$put('/action', form_data, {
          params: {
            workgroup_id: this.workgroup.id,
          },
        })
        .then((res) => {
          const indx = this.workgroup.actions.findIndex((x) => x.id == res.id)

          if (indx > -1) {
            this.workgroup.actions.splice(indx, 1, res)
            this.$snackbar.add(`Action updated successfully`)
          } else {
            this.workgroup.actions.push(res)
            this.$snackbar.add(`Action created successfully and appended to Group`)
          }
          this.local_loading = false
        })
        .catch((err) => {
          console.error(err)
        })
    },
  },
}
</script>

<style lang="scss" scoped>
::v-deep {
  .action-table > * > table > * > tr > * {
    &:nth-child(-n + 1) {
      position: sticky;
      z-index: 2;
      background: var(--default-background);
    }

    &:nth-child(1) {
      left: 0;
    }
  }
  .action-table > * > table > * > tr > th {
    &:nth-child(-n + 1) {
      z-index: 5;
    }
  }
}
</style>
