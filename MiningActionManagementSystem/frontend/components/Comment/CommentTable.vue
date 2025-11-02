<template>
  <v-card outlined elevation="0">
    <v-card-title class="att-title">
      Comments
      <v-spacer />
      <v-btn v-bind="$bind.btn" :disabled="disabled" class="mx-3" @click="createComment">
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
        sortBy: [],
        sortDesc: [],
      }"
      :footer-props="{
        'items-per-page-options': [],
      }"
    >
    </e-data-table>

    <!-- COMMENT DIALOG -->
    <comment-dialog ref="comment_dialog" />
  </v-card>
</template>

<script>
import CommentDialog from '@/components/Comment/CommentDialog.vue'

export default {
  components: {
    CommentDialog,
  },
  props: {
    comment_metadata: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    disabled: { type: Boolean, default: false },
  },
  data() {
    return {
      files: [],
      headers: [
        { text: 'Comment', value: 'comment', divider: true },
        {
          text: 'Created By',
          value: 'user_id',
          formatter: (x) => this.$utils.getUserName(x),
          divider: true,
          width: '10',
          cellClass: 'nowrap',
        },
        {
          text: 'Created Date',
          value: 'created',
          formatter: (x) => this.$format.date(x),
          width: '10',
        },
      ],
    }
  },
  methods: {
    createComment() {
      this.$refs.comment_dialog.open().then((res) => {
        // promise returns false - on cancel
        if (!res) return

        this.$emit('create_comment', res)
      })
    },
  },
}
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
