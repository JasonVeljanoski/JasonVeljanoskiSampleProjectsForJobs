<template>
  <v-dialog v-model="dialog" width="600" persistent>
    <v-card
      :class="{ dragover: dragover }"
      @drop.prevent="drop"
      @dragover.prevent="dragover = true"
      @dragenter.prevent="dragover = true"
      @dragleave.prevent="dragover = false"
    >
      <v-card-title>
        Upload Document

        <v-spacer />

        <v-file-input ref="file_input" v-bind="$bind.generic" hide-input style="flex-grow: 0" @change="addFile" />
      </v-card-title>

      <v-divider />

      <!-- FILE UPLOAD -->
      <v-card-text class="pt-4">
        <div class="d-flex justify-center pt-2 mb-2">
          <i>Drag file in to upload</i>
        </div>
        <v-text-field v-if="attachment.file" :value="attachment.file.name" v-bind="$bind.generic" readonly>
          <template #append>
            <e-icon-btn @click="remove">mdi-close</e-icon-btn>
          </template>
        </v-text-field>
      </v-card-text>

      <v-divider />

      <!-- FORM -->
      <v-card-text class="pt-4">
        <v-form ref="attachment_form" class="form">
          <h4>Title</h4>
          <v-textarea
            v-model="attachment.title"
            v-bind="$bind.select"
            :rules="[$form.required(attachment.title), $form.length(attachment.title, 60)]"
            hide-details="auto"
            counter="60"
            rows="2"
            no-resize
          />
          <h4>Description</h4>
          <v-textarea
            v-model="attachment.description"
            v-bind="$bind.freetext"
            :rules="[$form.required(attachment.description), $form.length(attachment.description, 250)]"
            hide-details="auto"
            counter="250"
            rows="7"
            no-resize
          />
        </v-form>
      </v-card-text>

      <v-divider />

      <!-- ACTIONS -->
      <v-card-actions>
        <cancel-btn @click="cancel()" />
        <v-spacer />
        <v-spacer />
        <save-btn @click="save">
          <v-icon left>mdi-plus</v-icon>
          add
        </save-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      dragover: false,
      attachment: {
        title: null,
        description: null,
        file: null,
      },
    }
  },
  methods: {
    open() {
      this.dialog = true

      // reset
      this.attachment.title = null
      this.attachment.description = null
      this.attachment.file = null

      // setup promise structure
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    cancel(status = false) {
      this.resolve(status)
      this.dialog = false
    },
    save() {
      // file input validation
      if (this.attachment.file == null) {
        this.$snackbar.add('You must upload a file', 'warning')
        return
      }
      if (this.$refs.attachment_form.validate()) {
        // resolve promise and close
        this.resolve(this.attachment)
        this.dialog = false
      } else {
        this.$snackbar.add('You did not pass all validation checks', 'warning')
      }
    },
    // ----------------------------------------------------------------
    addFile(files) {
      // if 'drag and drop' more than one file
      if (files.length > 1) {
        this.$snackbar.add('Only one file can be uploaded at a time', 'warning')
      }
      // if 'drag and drop' exactly one file
      else if (files.length == 1) {
        this.attachment.file = files[0]
      }
      // upload by clicking attachment icon
      else {
        this.attachment.file = files
      }
    },
    remove() {
      this.attachment.file = null
    },
    drop(event) {
      this.dragover = false

      const files = event.dataTransfer.files
      this.addFile(files)
    },
  },
}
</script>

<style lang="scss" scoped>
.dragover::after {
  content: '';
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  position: absolute;
  pointer-events: none;

  background: rgba(grey, 0.3);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
