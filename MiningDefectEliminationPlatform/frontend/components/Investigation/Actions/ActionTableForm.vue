<template>
  <v-dialog v-if="action" v-model="dialog" width="1200" persistent>
    <v-card>
      <!-- TITLE -->
      <v-card-title>
        <span v-if="action.id">Edit Action</span>
        <span v-else>Create Action</span>
      </v-card-title>

      <v-divider />

      <!-- BODY -->
      <span class="body-wrapper">
        <v-card-text>
          <v-form ref="form" class="root-action">
            <div class="form-box">
              <h4>Action Title</h4>
              <v-textarea
                v-model="action.title"
                v-bind="$bind.select"
                :rules="[
                  $form.required(action.title),
                  $form.length(action.title, 150),
                ]"
                hide-details="auto"
                rows="3"
                counter="150"
                no-resize
                dense
                required
              />

              <h4>Action Description</h4>
              <v-textarea
                v-model="action.description"
                v-bind="$bind.textarea"
                :rules="[
                  $form.required(action.description),
                  $form.length(action.description, 500),
                ]"
                hide-details="auto"
                counter="500"
                rows="4"
                no-resize
                dense
                required
              />
              <h4>Status</h4>
              <v-autocomplete
                v-model="action.status"
                v-bind="$bind.select"
                :items="$enums.converter($enums.status)"
                :rules="[$form.required(action.status)]"
                hide-details="auto"
                required
                dense
                @change="statusChange()"
              />
            </div>
            <div class="form-box">
              <h4>Priority</h4>
              <v-autocomplete
                v-model="action.priority"
                v-bind="$bind.select"
                :items="['High', 'Medium', 'Low']"
                :rules="[$form.required(action.priority)]"
                required
                dense
                hide-details="auto"
              />
              <h4>Action Owner</h4>
              <user-list-autocomplete
                v-if="action.owner_ids.length > 1"
                v-model="action.owner_ids"
                v-bind="$bind.select"
                :items="users"
                :rules="[
                  $form.arr_len_lim(action.owner_ids, 2),
                  $form.arr_non_empty(action.owner_ids),
                ]"
                item-text="filter_name"
                item-value="id"
                clearable
                multiple
              />
              <user-list-autocomplete
                v-else
                v-model="owner_id"
                v-bind="$bind.select"
                :items="users"
                :rules="[$form.required(owner_id)]"
                item-text="filter_name"
                item-value="id"
                clearable
                @change="autoFillSupervisor"
              />
              <h4>Action Members</h4>
              <user-list-autocomplete
                v-model="action.member_ids"
                v-bind="$bind.select"
                :items="users"
                :rules="[]"
                item-text="filter_name"
                item-value="id"
                clearable
                multiple
              />
              <h4>Action Owner(s) Supervisor</h4>
              <user-list-autocomplete
                v-model="action.supervisor_id"
                v-bind="$bind.select"
                :items="users"
                :rules="[$form.required(action.supervisor_id)]"
                item-text="filter_name"
                item-value="id"
                clearable
              />
              <h4>Action Due Date</h4>
              <e-date-time
                v-model="action.date_due"
                v-bind="$bind.textfield"
                :time="false"
                quick_select
                required
                dense
                style="width: 350px"
                hide-details="auto"
              />
              <span class="d-flex">
                <h4>Date Closed</h4>
                <small class="ml-2">(only required for closed actions)</small>
              </span>
              <e-date-time
                v-model="action.date_closed"
                v-bind="$bind.textfield"
                :apply_default_rules="false"
                :time="false"
                :rules="noFutureDateTimeRule(action.date_closed)"
                now_select
                required
                dense
                style="width: 350px"
                hide-details="auto"
              />
            </div>
            <div class="form-box">
              <span class="d-flex">
                <h4>Images</h4>
                <small class="ml-2">(optional, max: 1, limit: 50MB)</small>
              </span>
              <image-input
                :images="action.files"
                :img-disabled="action.files.length >= 1"
                :img-rules="[$form.arr_len_lim(action.files, 1)]"
              />
            </div>
          </v-form>
        </v-card-text>

        <v-divider />
        <e-attachment-table
          :attachment_metadata="action.general_attachments"
          class="my-4 mx-2"
          @new_attachment="handleNewAttachment"
        />
        <comment-table
          v-if="action.id"
          :comment_metadata="action.comments"
          :loading="comment_loading"
          :disabled="
            !(is_owner_supervisor_investigation_owner_or_admin || is_member)
          "
          class="my-4 mx-2"
          @addComment="addComment($event)"
        />
      </span>
      <v-divider v-if="action.id" />
      <v-card-actions>
        <v-btn
          v-bind="$bind.btn"
          outlined
          color="warning"
          class="pr-3"
          @click="cancel"
        >
          <v-icon left>mdi-close</v-icon>
          cancel
        </v-btn>
        <v-spacer />
        <e-btn
          :disabled="
            !is_owner_supervisor_investigation_owner_or_admin ||
            exceeded_file_limit
          "
          elevation="0"
          tooltip="Owners and Supervisors will receive an email"
          :outlined="action.id == null ? false : true"
          v-bind="$bind.btn"
          class="pr-4"
          @click="addAction()"
        >
          <v-icon v-if="report_id == null && !action.id" left>mdi-plus </v-icon>
          <v-icon v-else left> mdi-content-save-move</v-icon>
          <span v-if="report_id == null && !action.id">ADD</span>
          <span v-else> Save & Email</span>
        </e-btn>
        <e-btn
          v-if="action.id"
          @click="addAction(true)"
          elevation="0"
          color="primary"
        >
          <v-icon left>mdi-content-save</v-icon>
          Save
        </e-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import ImageInput from "@/components/Utils/ImageInput";
import CommentTable from "@/components/Investigation/Actions/CommentTable";

export default {
  name: "ActionsTableForm",
  components: {
    ImageInput,
    CommentTable,
  },
  props: {
    investigation_id: { type: Number },
    report_id: { type: Number, required: false, default: null },
  },
  data() {
    return {
      investigation_owner_ids: [],
      owner_id: null,
      // ---
      comment_loading: false,
      tmp_comment: null,
      attachments: [],
      exceeded_file_limit: false,
      tmp_img: null,
      dialog: false,
      comment_dialog: false,
      action: null,
    };
  },
  computed: {
    ...mapGetters({
      users: "user/getUsers",
    }),
    current_attachment_bytes() {
      let total = 0;
      for (let meta of this.action.general_attachments) total += meta.size;
      return (total / 1024 ** 2).toFixed(2);
    },
    is_member() {
      const uid = this.$auth.user.id;
      return this.action?.member_ids.includes(uid);
    },
    is_owner_supervisor_investigation_owner_or_admin() {
      // admins can edit anything
      if (this.$perms.is_admin) return true;

      // owners and supervisor logic
      const uid = this.$auth.user.id;

      // investigation owners
      let investigation_owner_ids = this.action.investigation_owner_ids;
      if (investigation_owner_ids.length == 0)
        investigation_owner_ids = this.investigation_owner_ids;

      // return
      // action owners or supervisor or investigation owners
      const res =
        this.action?.owner_ids.includes(uid) ||
        uid === this.action?.supervisor_id ||
        this.action?.owner_id === uid ||
        investigation_owner_ids.includes(uid);

      return res;
    },
  },
  watch: {
    "action.owner_ids"(newVal) {
      // (max len 3). Overwrite old if overflow.
      if (newVal.length == 3) {
        this.action.owner_ids.shift();
      }
    },
    owner_id(newVal) {
      if (newVal) {
        this.action.owner_ids = [newVal];
      }
    },
  },
  mounted() {
    if (!this.investigation_id) return;

    this.$axios
      .$get("/investigation/owner_ids", {
        params: { id: this.investigation_id },
      })
      .then((res) => {
        this.investigation_owner_ids = res;
      })
      .catch((err) => console.error(err));
  },
  methods: {
    open(action) {
      if (!action) {
        this.action = {
          id: null,
          created: null,
          updated: null,
          investigation_id: null,
          five_why_id: null,
          root_cause_detail_id: null,
          title: null,
          description: null,
          status: 1,
          priority: null,
          date_due: null,
          date_closed: null,
          supervisor_id: null,
          investigation_owner_ids: [],
          owner_ids: [],
          member_ids: [],
          files: [],
          filenames: [],
          owners: [],
          general_attachments: [],
        };
      } else {
        this.action = JSON.parse(JSON.stringify(action));
        this.initDates();
      }

      // NEW actions have this user by default as a member
      if (this.action.owner_ids.length == 0) {
        this.action.owner_ids.push(this.$auth.user.id);
        this.autoFillSupervisor(this.$auth.user.id);
      }

      // Frontend hacks to handle old actions haveing 2 owners and future actions having one owner
      if (this.action.owner_ids.length <= 1) {
        this.owner_id = this.action?.owner_ids[0];
      }

      this.dialog = true;

      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },
    cancel() {
      this.resetData();
      this.$refs.form.reset();
      this.resolve(false);
    },
    resetData() {
      this.attachments = [];
      // this.action.general_attachments = [];
      this.action.files = [];
      this.tmp_img = false;
      this.dialog = false;
    },
    updateFileLimStatus(payload) {
      this.exceeded_file_limit = payload;
    },
    statusChange() {
      if (this.action.status == 1) this.action.date_closed = null;
    },
    addAction(noEmail) {
      if (this.action.date_closed == null && this.action.status == 3) {
        this.$snackbar.add(
          "You must populate the Date Closed field for Closed actions",
          "warning"
        );
      } else if (
        this.action.status == 4 &&
        this.$format.initDate(this.action.date_due) >= new Date()
      ) {
        this.$snackbar.add(
          "Overdue actions must have a due date in the past",
          "warning"
        );
      } else if (this.$refs.form.validate()) {
        // TODO move to backend
        let owners = [];
        let id = this.action.id;
        for (let ii of this.action.owner_ids) {
          owners.push({ id: null, action_id: id, user_id: ii });
        }
        this.action.owners = owners;

        // ---

        let members = [];
        for (let ii of this.action.member_ids) {
          members.push({ id: null, action_id: id, user_id: ii });
        }
        this.action.members = members;
        this.action.noEmail = noEmail;

        // ---

        this.action.investigation_id = this.investigation_id;

        // push action to parent to update db
        // add action in parent layer as it may belong to
        // an investigation or five_why or rca...
        this.$emit("add_action", {
          action: { ...this.action },
          attachments: this.attachments,
        });

        // clear
        this.cancel();
      }
    },
    autoFillSupervisor(user_id) {
      // only for new actions
      if (this.action.id) return;

      // only auto-fill supervisors for new actions
      if (this.action.owner_ids.length == 1) {
        const owner = this.users.find((u) => u.id == user_id);
        if (!owner?.supervisor_id) return;
        this.action.supervisor_id = owner.supervisor_id;
      }
    },
    initDates() {
      this.action.created = this.$format.initDate(this.action.created);
      this.action.updated = this.$format.initDate(this.action.updated);
      this.action.date_due = this.$format.initDate(this.action.date_due);
      this.action.date_closed = this.$format.initDate(this.action.date_closed);
    },
    noFutureDateTimeRule(datetime) {
      if (this.action.id) return [];

      // only if new investigation
      return [this.$form.date_cannot_be_in_future(datetime)];
    },
    // --------------------
    // COMMENTS
    // --------------------
    addComment(comment) {
      this.comment_loading = true;

      this.$axios
        .$patch("/action/add_comment", null, {
          params: { action_id: this.action.id, comment: comment },
        })
        .then((res) => {
          this.action.comments.push(res);
          this.comment_loading = false;
        })
        .catch((err) => console.error(err));
    },
    // --------------------
    // ATTACHMENTS
    // --------------------
    handleNewAttachment(attachment) {
      // update attachments array for emit
      const file_clone = {
        title: JSON.parse(JSON.stringify(attachment.title)),
        description: JSON.parse(JSON.stringify(attachment.description)),
        network_drive_link: JSON.parse(
          JSON.stringify(attachment.network_drive_link)
        ),
        file: new File([attachment.file], attachment.file.name, {
          type: attachment.file.type,
        }),
      };

      this.attachments.push(file_clone);

      // update attachment meta data with pending attachments
      let meta_obj = {};
      meta_obj.filename = JSON.parse(JSON.stringify(attachment.file.name));
      meta_obj.size = JSON.parse(JSON.stringify(attachment.file.size));
      // meta_obj.extension = JSON.parse(JSON.stringify(attachment.file.filename.split(".").pop()));
      meta_obj.uploaded_by = this.$auth.user.id;
      meta_obj.created = new Date();
      meta_obj.network_drive_link = attachment.network_drive_link;
      meta_obj.title = attachment.title;
      meta_obj.description = attachment.description;

      this.action.general_attachments.push(meta_obj);
    },
  },
};
</script>

<style lang="scss" scoped>
.form-box {
  max-width: 400px;
  width: 100%;
  padding: 10px;
}

.root-action {
  display: grid;
  gap: 0 16px;
  grid-template-columns: repeat(3, 1fr);
}

.add-img {
  cursor: pointer;
  text-align: right;

  &:hover {
    text-decoration: underline;
    color: var(--v-primary-base);
  }
}

.dialog-container {
  background-color: var(--v-background-base);
  overflow: hidden;
  padding: 10px;
}

.img-wrapper {
  display: flex;
  justify-content: space-evenly;
}

.img-item {
  display: flex;
  border-radius: 10px;
  overflow: hidden;
  max-width: 300px;
}

.remove-img {
  position: relative;
  margin-left: -27px;
  margin-top: 7px;
  background-color: var(--v-accent-base);

  &:hover {
    opacity: 0.4;
  }
}
</style>
