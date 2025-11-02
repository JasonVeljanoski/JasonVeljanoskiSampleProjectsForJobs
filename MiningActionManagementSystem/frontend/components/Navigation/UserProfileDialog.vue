<template>
  <v-dialog v-model="dialog" persistent width="600">
    <v-card>
      <!-- TITLE -->
      <v-card-title>Edit Profile</v-card-title>

      <v-divider />

      <!-- BODY -->
      <span class="body-wrapper">
        <v-card-text>
          <h4>Functional location</h4>
          <v-autocomplete
            v-model="user.functional_locations"
            v-bind="$bind.select"
            :placeholder="floc_placeholder"
            :items="functional_locs_permutations"
            clearable
            multiple
          />
          <h4>Workcenter</h4>
          <v-autocomplete
            v-model="user.work_centers"
            v-bind="$bind.select"
            :items="workcenters"
            item-value="workcenter"
            item-text="description"
            clearable
            multiple
          />

          <h4>Back to back</h4>
          <user-autocomplete v-model="user.back_to_back_id" v-bind="$bind.select" :items="users" clearable />
          <div class="d-flex align-center">
            <h4>Do you wish to see "TX Oil Sample" work orders?</h4>
            <v-checkbox v-model="user.txoilsample" class="ml-2" />
          </div>
        </v-card-text>
      </span>

      <v-divider />

      <!-- ACTIONS -->
      <v-card-actions>
        <cancel-btn @click="cancel()" />
        <v-spacer />
        <save-btn @click="submit()" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data() {
    return {
      dialog: false,

      user: {
        id: null,
        functional_locs: [],
        work_centers: [],
        back_to_back_id: null,
        txoilsample: null,
      },
    }
  },
  computed: {
    ...mapGetters({
      users: 'user/getUsers',
      workcenters: 'lists/getWorkcenters',
      functional_locs_permutations: 'lists/getFunctionalLocsPermutations',
    }),
    floc_placeholder() {
      if (this.user.functional_locations) return this.user.functional_locations.join(', ')
      return ''
    },
  },
  methods: {
    resetData() {
      this.user.id = this.$auth.user.id
      this.user.functional_locations = this.$auth.user.functional_locations
      this.user.work_centers = this.$auth.user.work_centers
      this.user.back_to_back_id = this.$auth.user.back_to_back_id
      this.user.txoilsample = this.$auth.user.txoilsample
    },
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
      this.resetData()
      this.dialog = false
    },
    submit() {
      this.resolve(this.user)
      this.dialog = false
    },
  },
}
</script>
