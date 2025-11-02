<template>
  <v-card outlined elevation="0">
    <v-card-title class="att-title">
      Comments
      <v-spacer />
      <v-btn v-bind="$bind.btn" :disabled="disabled" class="mx-3" @click="comment_dialog = true">
        <v-icon left>mdi-plus</v-icon>
        <span>Comment</span>
      </v-btn>
    </v-card-title>

    <v-divider />

    <v-card-text v-if="comment_metadata.length == 0" class="my-2"> No comments. </v-card-text>

    <e-data-table
      v-else
      :headers="headers"
      :loading="loading"
      :items="comment_metadata"
      fixed-header
      :options="{
        itemsPerPage: 4,
        sortBy: ['created'],
        sortDesc: [true],
      }"
      :footer-props="{
        'items-per-page-options': [],
      }"
    >
    </e-data-table>

    <!-- COMMENT DIALOG -->
    <v-dialog v-model="comment_dialog" width="1200" persistent>
      <v-card>
        <v-card-text>
          <h4>Comments</h4>
          <v-textarea
            v-model="tmp_comment"
            v-bind="$bind.select"
            hide-details="auto"
            rows="14"
            counter="2000"
            dense
            required
          />
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-btn v-bind="$bind.btn" outlined color="warning" class="pr-3" @click="comment_dialog = false">
            <v-icon left>mdi-close</v-icon>
            cancel
          </v-btn>
          <v-spacer />
          <v-btn
            v-bind="$bind.btn"
            :disabled="tmp_comment && (tmp_comment.length > 2000 || tmp_comment.length == 0)"
            class="pr-4"
            @click="addComment"
          >
            <v-icon left>mdi-plus</v-icon>
            add
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
export default {
  props: {
    comment_metadata: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  data() {
    return {
      comment_dialog: false,
      tmp_comment: null,
      files: [],
      headers: [
        { text: "Comment", value: "comment" },
        {
          text: "Created By",
          value: "user_id",
          formatter: (x) => this.$utils.getUserName(x),
        },
        {
          text: "Created Date",
          value: "created",
          formatter: (x) => this.$format.date(x),
        },
      ],
    };
  },
  methods: {
    addComment() {
      this.$emit("addComment", this.tmp_comment);
      this.comment_dialog = false;
      this.tmp_comment = null;
    },
  },
};
</script>

<style lang="scss" scoped>
.attachments {
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  gap: 1em;
  overflow-y: auto;
}

.att-title {
  font-size: 16px;
}
</style>
