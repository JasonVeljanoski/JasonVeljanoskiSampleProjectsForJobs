<template>
  <e-dialog v-if="action" :dialog="dialog">
    <template #card:header>
      <div class="d-flex align-center">
        <div class="system_image mr-4">
          <v-img :src="source_image_path" :width="source_image_width" contain />
        </div>

        {{ card_title }}
      </div>
    </template>

    <template #card:body>
      <v-form ref="form" class="root-action d-flex justify-center">
        <div class="form-box">
          <span class="d-flex">
            <h4>Action Title</h4>
            <small v-if="isAceAction()" class="ml-2">{{ is_ace_text }}</small>
            <small v-if="!$action_utils.editable_action_fields[action.type].title" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <v-textarea
            v-model="action.title"
            v-bind="$bind.freetext"
            :disabled="!$action_utils.editable_action_fields[action.type].title"
            :rules="formRules('title')"
            rows="3"
          />
          <span class="d-flex">
            <h4>Action Description</h4>
            <small v-if="isAceAction()" class="ml-2"> {{ is_ace_text }} </small>
            <small v-if="!$action_utils.editable_action_fields[action.type].description" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <v-textarea
            v-model="action.description"
            v-bind="$bind.freetext"
            :disabled="!$action_utils.editable_action_fields[action.type].description"
            :rules="formRules('description')"
            rows="5"
          />
          <span class="d-flex">
            <h4>Assigned To</h4>
            <small v-if="isAceAction()" class="ml-2"> {{ is_ace_text }} </small>
            <small v-if="!$action_utils.editable_action_fields[action.type].owner_id" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <user-autocomplete
            v-model="action.owner_id"
            v-bind="$bind.select"
            :disabled="!$action_utils.editable_action_fields[action.type].owner_id"
            :items="users"
            clearable
            :rules="formRules('owner_id')"
            @change="autoFillSupervisor"
          />
          <span v-if="action.dep_extra_owner_id">
            Extra DEP Owner: {{ $utils.getUserName(action.dep_extra_owner_id) }}
          </span>
          <span class="d-flex">
            <h4>Status</h4>
            <small v-if="isAceAction()" class="ml-2"> {{ is_ace_text }} </small>
            <small v-if="!$action_utils.editable_action_fields[action.type].status" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <v-autocomplete
            v-model="action.status"
            v-bind="$bind.select"
            :items="$enums.converter($enums.status)"
            :disabled="!$action_utils.editable_action_fields[action.type].status"
            :rules="formRules('status')"
          />
          <span class="d-flex">
            <h4>Priority</h4>
            <small v-if="isAceAction()" class="ml-2"> {{ is_ace_text }} </small>
            <small v-if="!$action_utils.editable_action_fields[action.type].priority" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <v-autocomplete
            v-model="action.priority"
            v-bind="$bind.select"
            :items="$enums.converter($enums.priority)"
            :disabled="!$action_utils.editable_action_fields[action.type].priority"
            :rules="formRules('priority')"
          />
          <span class="d-flex">
            <h4>Completed</h4>
            <small v-if="!$action_utils.editable_action_fields[action.type].completed" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <v-slider
            v-model="action.completed"
            :label="`${String(action.completed)}%`"
            :color="completed_color"
            step="10"
            ticks
            inverse-label
            :disabled="!$action_utils.editable_action_fields[action.type].completed"
          />
        </div>
        <div class="form-box">
          <span class="d-flex">
            <h4>Supervisor</h4>
            <small v-if="isAceAction()" class="ml-2"> {{ is_ace_text }} </small>
            <small v-if="!$action_utils.editable_action_fields[action.type].supervisor_id" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <user-autocomplete
            v-model="action.supervisor_id"
            v-bind="$bind.select"
            :disabled="!$action_utils.editable_action_fields[action.type].supervisor_id"
            :items="users"
            :rules="formRules('supervisor_id')"
            clearable
          />
          <span class="d-flex">
            <h4>Action Members(s)</h4>
            <small v-if="!$action_utils.editable_action_fields[action.type].member_ids" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <user-autocomplete
            v-model="action.member_ids"
            v-bind="$bind.select"
            :disabled="!$action_utils.editable_action_fields[action.type].member_ids"
            :items="users"
            clearable
            multiple
          />
          <span class="d-flex">
            <h4>Functional location</h4>
            <small v-if="!$action_utils.editable_action_fields[action.type].functional_location" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <functional-location-autocomplete
            v-model="action.functional_location"
            :placeholder="action.functional_location"
            v-bind="$bind.select"
            :items="functional_locs_permutations"
            :disabled="!$action_utils.editable_action_fields[action.type].functional_location"
          />
          <span class="d-flex">
            <h4>Work Center</h4>
            <small v-if="!$action_utils.editable_action_fields[action.type].work_center" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <v-autocomplete
            v-model="action.work_center"
            v-bind="$bind.select"
            :items="work_centers"
            item-text="description"
            item-value="workcenter"
            :disabled="!$action_utils.editable_action_fields[action.type].work_center"
          />
          <span class="d-flex">
            <h4>Source System Link</h4>
            <small v-if="!$action_utils.editable_action_fields[action.type].link" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <v-text-field
            v-model="action.link"
            v-bind="$bind.freetext"
            :disabled="!$action_utils.editable_action_fields[action.type].link"
            rows="1"
          >
            <template #prepend-inner>
              <copy-icon-btn small tooltip_text="Copy Source" @click="copyUrl(action.link)" />
            </template>
          </v-text-field>

          <span class="d-flex">
            <h4>Action Start Date</h4>
            <small v-if="isAceAction()" class="ml-2"> {{ is_ace_text }} </small>
            <small v-if="!$action_utils.editable_action_fields[action.type].start_date" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <e-date-field
            v-model="action.start_date"
            v-bind="$bind.select"
            :clearable="false"
            :time="false"
            :disabled="!$action_utils.editable_action_fields[action.type].start_date"
            :hide-calendar="!$action_utils.editable_action_fields[action.type].start_date"
            :rules="formRules('start_date')"
          />
          <span class="d-flex">
            <h4>Action Due Date</h4>
            <small v-if="isAceAction()" class="ml-2"> {{ is_ace_text }} </small>
            <small v-if="!$action_utils.editable_action_fields[action.type].date_due" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <e-date-field
            v-model="action.date_due"
            v-bind="$bind.select"
            :time="false"
            :clearable="false"
            :disabled="!$action_utils.editable_action_fields[action.type].date_due"
            :hide-calendar="!$action_utils.editable_action_fields[action.type].date_due"
            :quick_select="$action_utils.editable_action_fields[action.type].date_due"
            :rules="formRules('date_due')"
          />
          <span class="d-flex">
            <h4>Action Date Closed</h4>
            <small v-if="!$action_utils.editable_action_fields[action.type].date_closed" class="ml-2">
              ({{ fromSourceText(action) }})
            </small>
          </span>
          <e-date-field
            v-model="action.date_closed"
            v-bind="$bind.select"
            :time="false"
            :clearable="false"
            :hide-calendar="!$action_utils.editable_action_fields[action.type].date_closed"
            :disabled="!$action_utils.editable_action_fields[action.type].date_closed"
          />
        </div>
      </v-form>

      <v-divider />

      <group-action-table
        :action="action"
        :workgroups="action.workgroups"
        class="ma-2"
        @trigger_reload="$emit('trigger_reload')"
      >
        <template #card:header>
          <save-btn
            v-if="!action.id"
            tooltip="You must create the action before assigning it to a group"
            @click="createAction"
          >
            <v-icon left>mdi-content-save</v-icon>
            Create Action
          </save-btn>
        </template>
      </group-action-table>

      <attachment-table
        :attachment_metadata="action.general_attachments"
        class="ma-2"
        @new_attachment="handleNewAttachment"
      />

      <comment-table
        v-if="action.id"
        :comment_metadata="action.comments"
        class="ma-2"
        @create_comment="handleNewComment"
      />
    </template>

    <template #card:footer>
      <cancel-btn @click="cancel()" />
      <v-spacer />
      <save-btn
        v-if="action.type == 'ACE'"
        outlined
        tooltip="Assignee and Members will receive an email"
        @click="submit(true)"
      >
        <v-icon left>mdi-content-save-move</v-icon>
        Save & Email
      </save-btn>
      <save-btn @click="submit()" />
    </template>
  </e-dialog>
</template>

<script>
import { mapGetters } from 'vuex'
import AttachmentTable from '@/components/Attachment/AttachmentTable.vue'
import CommentTable from '@/components/Comment/CommentTable.vue'
import GroupActionTable from '~/components/Action/GroupActionTable.vue'
import CopyIconBtn from '@/components/Icon/CopyIconBtn.vue'

export default {
  components: {
    AttachmentTable,
    CommentTable,
    GroupActionTable,
    CopyIconBtn,
  },
  data() {
    return {
      dialog: false,
      action: null,
      attachments: [],
    }
  },
  computed: {
    ...mapGetters({
      users: 'user/getUsers',
      functional_locs_permutations: 'lists/getFunctionalLocsPermutations',
      work_centers: 'lists/getWorkcenters',
    }),
    card_title() {
      if (this.action) return this.action.id ? 'Edit Action' : 'Create Action'
      return ''
    },
    completed_color() {
      if (this.action.completed < 25) return 'error'
      if (this.action.completed < 75) return 'warning'
      return 'success'
    },
    is_ace_text() {
      return this.isAceAction() ? '(required)' : ''
    },
    source_image_path() {
      if (!this.action) return

      const source = this.action.type
      return this.$enums.source_logos[source].path
    },
    source_image_width() {
      if (!this.action) return

      const source = this.action.type
      return this.$enums.source_logos[source].width
    },
  },
  methods: {
    // ------------------------------
    // DIALOG HANDLERS
    // ------------------------------
    open(action) {
      action = JSON.parse(JSON.stringify(action))

      if (!action) {
        this.resetAction()
        this.attachments = []

        // new actions have this user by default as an owner
        this.action.owner_id = this.$auth.user.id
        this.autoFillSupervisor()

        // default open action
        this.action.status = 2
      } else {
        this.action = action
        this.attachments = []
        this.formatActionDates()
      }

      this.$nextTick(() => {
        this.$refs.form.resetValidation()
      })

      this.fullscreen = false
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
    // --------------------
    // ACTION HELPERS
    // --------------------
    createAction() {
      if (!this.$refs.form.validate()) return

      this.$axios
        .$post('/action', this.action)
        .then((res) => {
          // update action with fields that are not in the form
          // format date like values
          res.date_due = this.$format.initDate(res.date_due)
          res.start_date = this.$format.initDate(res.start_date)
          res.date_closed = this.$format.initDate(res.date_closed)
          res.created = this.$format.initDate(res.created)
          res.updated = this.$format.initDate(res.updated)

          this.action = res

          // update action
          this.$emit('trigger_reload')

          // ----------
          this.$snackbar.add(`Action Created Successfully`)
        })
        .catch((err) => console.error(err))
    },
    submit(email = false) {
      if (this.action.date_closed == null && this.action.status == 4) {
        this.$snackbar.add('You must populate the Date Closed field for Closed actions', 'warning')
      } else if (this.$refs.form.validate()) {
        if (email) {
          if (!confirm('Are you sure you want to also send emails?')) return
        }

        this.formatActionDates()

        const result = {
          action: this.action,
          attachments: this.attachments,
          to_email: email,
        }
        this.resolve(result)
        this.dialog = false
      }
    },
    autoFillSupervisor() {
      // only auto-fill supervisors for new actions
      if (this.action.owner_id) {
        const owner = this.users.find((u) => u.id == this.action.owner_id)
        if (!owner?.supervisor_id) return
        this.action.supervisor_id = owner.supervisor_id
      }
    },
    // ------------------------------
    // DATA SETTERS
    // ------------------------------
    formatActionDates() {
      this.action.created = this.$format.initDate(this.action.created)
      this.action.updated = this.$format.initDate(this.action.updated)
      this.action.start_date = this.$format.initDate(this.action.start_date)
      this.action.date_due = this.$format.initDate(this.action.date_due)
      this.action.date_closed = this.$format.initDate(this.action.date_closed)
    },
    resetAction() {
      this.action = {
        id: null,
        created: null,
        updated: null,
        type: 'ACE',
        title: null,
        description: null,
        member_ids: [],
        owner_id: null,
        supervisor_id: null,
        status: null,
        priority: null,
        completed: 0,
        link: null,
        functional_location: null,
        work_center: null,
        start_date: null,
        date_due: null,
        date_closed: null,
        general_attachments: [],
      }
    },
    // --------------------
    // FORM RULES
    // --------------------
    isAceAction() {
      return this.action.type == 'ACE'
    },
    formRules(key) {
      // no rules for non ACE actions
      if (!this.isAceAction()) return []

      const rules = []
      rules.push(() => {
        return this.$form.required(this.action[key])
      })

      return rules
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

      this.action.general_attachments.push(meta_obj)
    },
    // --------------------
    // COMMENT
    // --------------------
    handleNewComment(comment) {
      if (!this.action.id) return

      this.$axios
        .$post('/action/comment', null, {
          params: {
            action_id: this.action.id,
            comment,
          },
        })
        .then((res) => {
          if (res) {
            this.action.comments.push(res)
            this.$snackbar.add('A new comment was created')
          }
        })
        .catch((err) => console.error(err))
    },
    // ------------------------------
    // VALIDATION
    // ------------------------------
    fromSourceText(action) {
      const type = action.type.replaceAll('_', ' ')
      return `from ${type}`
    },
    // --------------------
    // OTHER
    // --------------------
    toggleFullscreen() {
      this.fullscreen = !this.fullscreen
    },
    copyUrl(source) {
      navigator.clipboard.writeText(source)
    },
  },
}
</script>

<style lang="scss" scoped>
.form-box {
  max-width: 600px;
  width: 100%;
}

.root-action {
  display: grid;
  gap: 0 16px;
  grid-template-columns: repeat(2, 1fr);
}

.system_image {
  background-color: white;
  padding: 5px;
  border-radius: 5px;
}
</style>
