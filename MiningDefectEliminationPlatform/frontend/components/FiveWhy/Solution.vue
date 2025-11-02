<template>
  <v-form ref="solution-form">
    <h4>Group Participants</h4>
    <user-list-autocomplete
      v-model="investigation.five_why.owner_ids"
      v-bind="$bind.select"
      :items="users"
      :rules="[$form.arr_non_empty(investigation.five_why.owner_ids)]"
      item-text="filter_name"
      item-value="id"
      clearable
      multiple
      @change="updateOwners"
    />

    <h4>Supervisor</h4>
    <user-list-autocomplete
      v-model="investigation.five_why.supervisor_id"
      v-bind="$bind.select"
      :items="users"
      :rules="[$form.required(investigation.five_why.supervisor_id)]"
      item-text="filter_name"
      item-value="id"
      clearable
    />
  </v-form>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: {
    investigation: { Object },
  },
  computed: {
    ...mapGetters({
      users: "user/getUsers",
    }),
  },
  methods: {
    updateOwners() {
      // update owners list for back-end
      this.investigation.five_why.owners = [];
      this.investigation.five_why.owners = this.investigation.five_why.owner_ids.map((x) => ({
        id: null,
        five_why_id: this.investigation.five_why.id,
        user_id: x,
      }));
    },
  },
};
</script>

<style lang="scss" scoped>
.v-text-field {
  max-width: 600px;
}
</style>
