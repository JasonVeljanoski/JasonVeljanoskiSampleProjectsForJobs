<template>
  <v-dialog v-if="feedback" v-model="dialog" width="1200" persistent scrollable>
    <v-card>
      <v-card-title>
        <span v-if="feedback.id">Edit Feedback</span>
        <span v-else>Create Feedback</span>
      </v-card-title>
      <v-divider />
      <span class="body-wrapper">
        <v-card-text>
          <v-form ref="form" class="feedback_root">
            <div>
              <h4>Reason</h4>
              <v-autocomplete
                v-model="feedback.reason"
                v-bind="$bind.select"
                :items="$enums.converter($enums.feedback_types)"
                :rules="[$form.required(feedback.reason)]"
                hide-details="auto"
                required
                dense
                class="mb-4"
                @change="onReasonChange"
              />
              <h4>Title</h4>
              <v-textarea
                v-model="feedback.title"
                v-bind="$bind.select"
                :rules="[
                  $form.required(feedback.title),
                  $form.length(feedback.title, 60),
                ]"
                hide-details="auto"
                rows="3"
                counter="60"
                no-resize
                dense
                required
              />
              <h4>Issue relates to</h4>
              <v-textarea
                v-model="feedback.page"
                v-bind="$bind.select"
                :rules="[
                  $form.required(feedback.page),
                  $form.length(feedback.page, 50),
                ]"
                hide-details="auto"
                rows="1"
                counter="50"
                no-resize
                dense
                required
              />

              <h4>Summary</h4>
              <v-textarea
                v-model="feedback.summary"
                v-bind="$bind.select"
                :rules="[
                  $form.required(feedback.summary),
                  $form.length(feedback.summary, 2000),
                ]"
                hide-details="auto"
                rows="4"
                counter="2000"
                no-resize
                dense
                required
              />

              <template v-if="is_bug">
                <h4>How to replicate</h4>
                <v-textarea
                  v-model="feedback.replicate"
                  v-bind="$bind.select"
                  :rules="[
                    $form.conditional_required(feedback.replicate, is_bug),
                    $form.length(feedback.replicate, 2000),
                  ]"
                  hide-details="auto"
                  rows="6"
                  counter="2000"
                  no-resize
                  dense
                  required
                />
              </template>
            </div>
            <div v-if="$perms.is_admin">
              <span class="d-flex">
                <h4>Status</h4>
                <small class="ml-2"> (Admins only) </small>
              </span>
              <v-autocomplete
                v-model="feedback.status"
                v-bind="$bind.select"
                :items="$enums.converter($enums.feedback_status)"
                :disabled="!$perms.is_admin"
                hide-details="auto"
                required
                dense
              />
              <span class="d-flex">
                <h4>Admin Notes</h4>
                <small class="ml-2">
                  (Admins only, This task can be completed later)
                </small>
              </span>
              <v-textarea
                v-model="feedback.closure_notes"
                v-bind="$bind.select"
                :rules="[$form.length(feedback.closure_notes, 2000)]"
                :disabled="!$perms.is_admin"
                hide-details="auto"
                rows="6"
                counter="2000"
                no-resize
                dense
                required
              />
            </div>
          </v-form>

          <v-divider v-if="feedback.id" />

          <e-attachment-table
            :attachment_metadata="feedback.general_attachments"
            class="my-4 mx-2"
            @new_attachment="handleNewAttachment"
          />

          <comment-table
            v-if="feedback.id"
            :comment_metadata="feedback.comments"
            :loading="comment_loading"
            class="my-4 mx-2"
            @addComment="addComment($event)"
          />
        </v-card-text>
      </span>

      <v-divider />
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
          elevation="0"
          tooltip="Owners and Supervisors will receive an email"
          :outlined="feedback.id == null ? false : true"
          v-bind="$bind.btn"
          class="pr-4"
          @click="addFeedback(true)"
        >
          <v-icon left>mdi-content-save-move</v-icon>
          <span>Save & Email</span>
        </e-btn>
        <e-btn
          v-if="feedback.id"
          v-bind="$bind.btn"
          class="pr-4"
          @click="addFeedback"
        >
          <v-icon left>mdi-content-save</v-icon>
          Save
        </e-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import ImageInput from "@/components/Utils/ImageInput";
import CommentTable from "@/components/Investigation/Actions/CommentTable";

export default {
  name: "FeedbackForm",
  components: {
    ImageInput,
    CommentTable,
  },
  data() {
    return {
      dialog: false,
      feedback: null,

      // comment
      comment_loading: false,

      // attachments
      attachments: [],
      exceeded_file_limit: false,
    };
  },
  computed: {
    current_attachment_bytes() {
      let total = 0;
      for (let meta of this.feedback.general_attachments) total += meta.size;
      return (total / 1024 ** 2).toFixed(2);
    },
    is_bug() {
      return this.feedback.reason == 1;
    },
  },
  methods: {
    //---------------------------
    // OPEN
    //---------------------------
    open(feedback) {
      if (!feedback) {
        this.feedback = {
          id: null,
          title: null,
          reason: null,
          page: `Appears on ${this.$nuxt.$route.path.substring(1)} page.`,
          summary: null,
          replicate: null,
          creator_id: null,
          status: 1,
          closure_notes: null,
          general_attachments: [],
          noEmail: false,
          images: [],
        };
      } else {
        this.feedback = { ...feedback };
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
      this.dialog = false;
    },
    addFeedback(noEmail) {
      if (noEmail) this.feedback.noEmail = noEmail;
      if (this.$refs.form.validate()) {
        this.$emit("add_feedback", {
          feedback: { ...this.feedback },
          noEmail: noEmail,
          attachments: this.attachments,
        });

        // clear
        this.cancel();
      }
    },
    // -----------------------------
    // REASON CHANGE (BUG <--> FEEDBACK)
    // -----------------------------
    onReasonChange() {
      // FEEDBACK reason never need a replicate field
      if (this.feedback.reason == 2) this.feedback.replicate = null;
    },
    // -----------------------------
    // COMMENTS
    // -----------------------------
    addComment(comment) {
      this.comment_loading = true;

      this.$axios
        .$patch("/feedback/add_comment", null, {
          params: { feedback_id: this.feedback.id, comment: comment },
        })
        .then((res) => {
          this.feedback.comments.push(res);
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

      this.feedback.general_attachments.push(meta_obj);
    },
    updateFileLimStatus(payload) {
      this.exceeded_file_limit = payload;
    },
  },
};
</script>

<style lang="scss" scoped>
.feedback_root {
  .admin_wrapper {
    padding: 10px;
    border-radius: 5px;
    border: solid 2px var(--v-primary-base);

    legend {
      font-weight: bold;
      color: var(--v-primary-base);
    }
  }
}

.body-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: scroll;
}
</style>
