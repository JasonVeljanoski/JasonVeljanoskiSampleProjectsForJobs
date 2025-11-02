<template>
  <e-dialog v-if="workgroup" :dialog="dialog" :title="card_title" persistent scrollable width="1200">
    <template #card:body>
      <v-form ref="form" class="d-flex justify-center">
        <v-expansion-panels v-model="panel" accordion flat>
          <v-expansion-panel>
            <v-expansion-panel-header style="font-size: 12pt; font-weight: 500; margin: 0px; padding: 0px">
              Group Details
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <div class="description">
                <h4>Title</h4>
                <v-textarea
                  v-model="workgroup.title"
                  v-bind="$bind.select"
                  :rules="[$form.required(workgroup.title), $form.length(workgroup.title, 150)]"
                  hide-details="auto"
                  rows="2"
                  counter="150"
                  no-resize
                />
                <h4>Description</h4>
                <v-textarea
                  v-model="workgroup.description"
                  v-bind="$bind.select"
                  :rules="[$form.required(workgroup.description), $form.length(workgroup.description, 500)]"
                  hide-details="auto"
                  counter="500"
                  rows="4"
                  no-resize
                  dense
                  required
                />
              </div>
              <div class="assign">
                <span class="d-flex">
                  <h4>Assigned To</h4>
                  <small class="ml-2"> (can edit the group) </small>
                </span>
                <user-autocomplete
                  v-model="workgroup.owner_id"
                  v-bind="$bind.select"
                  :rules="[$form.required(workgroup.owner_id)]"
                  :items="users"
                />
                <h4>Group Members(s)</h4>
                <user-autocomplete
                  v-model="workgroup.member_ids"
                  v-bind="$bind.select"
                  :rules="[$form.arr_non_empty(workgroup.member_ids)]"
                  :items="users"
                  multiple
                />
                <span class="d-flex">
                  <h4>Group Admin(s)</h4>
                  <small class="ml-2"> (can edit the group) </small>
                </span>
                <user-autocomplete
                  v-model="workgroup.admin_ids"
                  v-bind="$bind.select"
                  :rules="[$form.arr_non_empty(workgroup.admin_ids)]"
                  :items="users"
                  multiple
                />
              </div>
              <div>
                <span class="d-flex">
                  <h4>Functional Location</h4>
                  <small class="ml-2"> (optional) </small>
                </span>
                <functional-location-autocomplete
                  v-model="workgroup.functional_location"
                  v-bind="$bind.select"
                  :items="functional_locs"
                />
                <div class="d-flex align-center">
                  <h4>Set group to confidential</h4>
                  <v-checkbox
                    :value="is_confidential"
                    class="ml-2 my-4"
                    hide-details
                    style="margin: 0; padding: 0"
                    @change="changeConfidential"
                  />
                </div>
                <div class="d-flex align-center">
                  <h4>Do you want to set the group as inactive?</h4>
                  <v-checkbox v-model="is_closed" hide-details class="ml-2" style="margin: 0; padding: 0" />
                </div>
              </div>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-form>

      <v-divider />

      <action-table :actions="workgroup.actions" class="ma-2" @edit="handleCreateAction($event)">
        <template #card:header>
          <div class="d-flex" style="gap: 8px">
            <save-btn
              v-if="!workgroup.id"
              tooltip="You must create the group before assigning actions"
              @click="createGroup"
            >
              <v-icon left>mdi-content-save</v-icon>
              Create Group
            </save-btn>
            <v-btn v-if="!add_mode" v-bind="$bind.btn" :disabled="!workgroup.id" @click="toggleAddMode">
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
            <v-btn v-bind="$bind.btn" :disabled="!workgroup.id" @click="handleCreateAction()">
              <v-icon left>mdi-pencil</v-icon>
              new ace action
            </v-btn>
          </div>
        </template>
      </action-table>

      <attachment-table
        :attachment_metadata="workgroup.general_attachments"
        class="ma-2"
        @new_attachment="handleNewAttachment"
      />

      <comment-table
        v-if="workgroup.id"
        :comment_metadata="workgroup.comments"
        class="ma-2"
        @create_comment="handleNewComment"
      />
    </template>

    <!-- ACTIONS -->
    <template #card:footer>
      <cancel-btn @click="cancel()" />
      <v-spacer />
      <save-btn outlined tooltip="Assignee, Members and Admins will receive an email" @click="submit(true)">
        <v-icon left>mdi-content-save-move</v-icon>
        Save & Email
      </save-btn>
      <save-btn @click="submit()" />

      <!-- DIALOGS -->
      <create-update-action-form ref="action_form" />
    </template>
  </e-dialog>
</template>

<script>
import { mapGetters } from 'vuex'

import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'
import ActionTable from '@/components/Action/ActionTable.vue'
import AttachmentTable from '@/components/Attachment/AttachmentTable.vue'
import CommentTable from '@/components/Comment/CommentTable.vue'
import CreateUpdateActionForm from '@/components/Action/CreateUpdateActionForm.vue'

export default {
  components: {
    PrivacyEnumIcon,
    ActionTable,
    AttachmentTable,
    CommentTable,
    CreateUpdateActionForm,
  },
  data() {
    return {
      // panel
      panel: null,

      // actions
      add_mode: false,
      selected_action: null,
      action_titles: [],

      // ---------

      // workgroup
      dialog: false,
      workgroup: null,
      attachments: [],
      is_confidential: false,
      is_closed: false,
    }
  },
  computed: {
    ...mapGetters({
      users: 'user/getUsers',
      functional_locs: 'lists/getFunctionalLocsPermutations',
    }),
    card_title() {
      if (this.workgroup) return this.workgroup.id ? 'Edit Group' : 'Create Group'
      return ''
    },
  },
  watch: {
    is_closed() {
      this.workgroup.is_active = !this.is_closed
    },
  },
  mounted() {
    this.getWorkgroupTitles()
    this.getActionTitles()
  },
  methods: {
    open(workgroup = null) {
      // if new workgroup
      this.workgroup = JSON.parse(JSON.stringify(workgroup))
      this.attachments = []

      if (!workgroup) {
        this.resetData()
        this.is_confidential = false
        this.panel = 0
      } else {
        this.is_confidential = workgroup.privacy == 3
        this.panel = null
      }

      this.dialog = true

      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    cancel(status = false) {
      this.resolve(status)
      this.dialog = false
    },
    submit(email = false) {
      if (this.$refs.form.validate()) {
        if (email) {
          if (!confirm('Are you sure you want to also send emails?')) return
        }

        this.resolve({
          workgroup: this.workgroup,
          attachments: this.attachments,
          to_email: email,
        })
        this.dialog = false
      } else {
        this.panel = 0
      }
    },
    createGroup() {
      if (!this.$refs.form.validate()) return

      this.$axios
        .$post('/workgroup', this.workgroup)
        .then((res) => {
          this.workgroup = res

          // update group
          this.$emit('trigger_reload')
        })
        .catch((err) => console.error(err))
    },
    resetData() {
      this.workgroup = {
        title: null,
        description: null,
        owner_id: this.$auth.user.id,
        member_ids: [],
        admin_ids: [],
        functional_location: null,
        closed: false,
        privacy: 1, // public
        action_ids: [],
        actions: [],
        general_attachments: [],
        comments: [],
      }

      this.attachments = []
    },
    // --------------------------
    // WORKGROUP
    // --------------------------
    getWorkgroupTitles() {
      this.$axios
        .$get('/privacy/action_titles')
        .then((res) => {
          this.action_titles = res
        })
        .catch((err) => console.error(err))
    },
    changeConfidential(flag) {
      if (
        flag &&
        !confirm(
          `Are you sure? Saving the group will remove the public actions from any other group and change these actions to confidential.`,
        )
      ) {
        this.$nextTick(() => {
          this.workgroup.privacy = 1
          this.is_confidential = false
          return
        })
      }
      this.is_confidential = true
      this.workgroup.privacy = 3
    },
    // --------------------
    // ATTACHMENTS
    // --------------------
    handleNewAttachment(attachment) {
      // update attachments array for emit
      this.attachments.push(attachment)

      // update attachment meta data with pending attachments
      const meta_obj = attachment
      meta_obj.filename = attachment.file.name
      meta_obj.size = attachment.file.size
      meta_obj.extension = meta_obj.filename.split('.').pop()
      meta_obj.uploaded_by = this.$auth.user.id
      meta_obj.created = new Date()

      this.workgroup.general_attachments.push(meta_obj)
    },
    // --------------------
    // COMMENT
    // --------------------
    handleNewComment(comment) {
      if (!this.workgroup.id) return

      this.$axios
        .$post('/workgroup/comment', null, {
          params: {
            workgroup_id: this.workgroup.id,
            comment,
          },
        })
        .then((res) => {
          if (res) {
            this.workgroup.comments.push(res)
            this.$snackbar.add('A new comment was created.')
          }
        })
        .catch((err) => console.error(err))
    },
    // --------------------
    // ACTION
    // --------------------
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
          this.getWorkgroupTitles()
          this.$refs.input.activateMenu()
        } else {
          this.selected_action = null
        }
      })
    },
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
            this.workgroup.action_ids.push(res.id)
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

          // update group
          this.$emit('trigger_reload')
        })
        .catch((err) => {
          console.error(err)
        })
    },
  },
}
</script>

<style lang="scss" scoped>
.root-workgroup {
  margin-bottom: 20px;
  display: grid;

  grid-template-areas:
    'description description'
    'assign floc';

  gap: 16px 16px;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
}

.title {
  grid-area: title;
}

.description {
  grid-area: description;
}

.assign {
  grid-area: assign;
}

.floc {
  grid-area: floc;
}
</style>
