<template>
  <v-dialog v-model="dialog" width="unset">
    <v-card v-if="user">
      <v-card-title>Test Dialog</v-card-title>
      <v-card-text>
        <v-text-field v-model="user.name" label="Name" />
        <v-text-field v-model="user.email" label="Email" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="warning" text @click="cancel">Cancel</v-btn>
        <v-btn color="primary" outlined π@click="save">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      user: false,
    }
  },
  methods: {
    open(user) {
      this.user = JSON.parse(JSON.stringify(user))
      this.dialog = true
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    cancel() {
      this.dialog = false
      this.reject()
      // this.resolve(false)
    },
    save() {
      this.dialog = false
      this.resolve(this.user)
      this.user = false
    },
  },
}
</script>
