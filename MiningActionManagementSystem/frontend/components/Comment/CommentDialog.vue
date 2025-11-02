<template>
  <v-dialog v-model="dialog" width="1200" persistent>
    <v-card>
      <v-card-title> Comment </v-card-title>
      <v-card-text>
        <v-textarea
          ref="freetext"
          v-model="tmp_comment"
          v-bind="$bind.freetext"
          rows="14"
          placeholder="Write a comment..."
          dense
          required
          @keydown.@="handleInput"
        />
        <div class="d-flex">
          <v-spacer />
          <mention-helper ref="mention_helper" @mention="handleMention" />
        </div>
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-btn v-bind="$bind.btn" outlined color="warning" class="pr-3" @click="cancel()">
          <v-icon left>mdi-close</v-icon>
          cancel
        </v-btn>
        <v-spacer />
        <v-btn v-bind="$bind.btn" :disabled="tmp_comment && tmp_comment.length == 0" class="pr-4" @click="submit()">
          <v-icon left>mdi-content-save</v-icon>
          save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import MentionHelper from '@/components/Comment/MentionHelper.vue'

export default {
  components: {
    MentionHelper,
  },
  data() {
    return {
      dialog: false,
      tmp_comment: null,
    }
  },
  methods: {
    open() {
      this.dialog = true

      this.resetData()

      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    cancel(status = false) {
      this.resolve(status)
      this.dialog = false
    },
    submit() {
      this.resolve(this.tmp_comment)
      this.dialog = false
    },
    resetData() {
      this.tmp_comment = null
    },
    // ------------------------------
    // MENTION
    // ------------------------------
    handleMention(mention) {
      if (!this.tmp_comment) this.tmp_comment = ''
      // remove @ if it is the last character, edge-case: user types @
      if (this.tmp_comment[this.tmp_comment.length - 1] == '@') {
        this.tmp_comment = this.tmp_comment.slice(0, -1)
      }

      const textfield = this.$refs.freetext.$refs.input

      const cursor = textfield.selectionStart

      const text = this.tmp_comment
      this.tmp_comment = `${text.slice(0, cursor)} ${mention} ${text.slice(cursor)}`

      textfield.focus()
      this.$nextTick(() => {
        textfield.setSelectionRange(cursor + mention.length + 2, cursor + mention.length + 2)
      })
    },
    handleInput() {
      this.$refs.mention_helper.open()
    },
  },
}
</script>
