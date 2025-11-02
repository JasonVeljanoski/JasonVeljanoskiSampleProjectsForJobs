<template>
  <base-dialog width="700" :card-props="{ height: 710 }">
    <v-card-title>
      Select User

      <v-spacer />

      <v-text-field
        v-model="search"
        v-bind="$bind.generic"
        hide-details
        placeholder="Search"
        clearable
        append-icon="mdi-magnify"
        style="width: 200px"
      />
    </v-card-title>
    <v-divider />
    <e-data-table
      :headers="headers"
      :items="users"
      :search="search"
      fixed-header
      :footer-props="{
        'items-per-page-options': [10],
      }"
    >
      <template #footer.prepend> <v-spacer style="height: 58px" /> </template>

      <template #item.actions="{ item }">
        <e-icon-btn tooltip="Select User" @click="selectUser(item)">mdi-account-arrow-right-outline</e-icon-btn>
      </template>
    </e-data-table>
    <v-divider />
    <v-card-actions>
      <cancel-btn @click="cancel" />
    </v-card-actions>
  </base-dialog>
</template>

<script>
import mixin from './Mixin.js'

export default {
  mixins: [mixin],
  props: {},
  data() {
    return {
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Email', value: 'email' },
        { text: '', value: 'actions', sortable: false },
      ],
      users: [],
      search: null,
    }
  },

  created() {
    this.$axios.$get('/user/all').then((res) => {
      this.users = res
    })
  },
  methods: {
    selectUser(user) {
      this._close(user)
    },
  },
}
</script>

<style lang="scss" scoped></style>
