<template>
  <div class="d-flex">
    <p class="mb-auto mt-auto mr-3 text-h7">
      {{ team_name }}
    </p>
    <v-menu
      v-if="$auth.user"
      :value="menu"
      offset-y
      :close-on-content-click="false"
    >
      <template v-slot:activator="{ on, attrs }">
        <e-icon-btn
          fab
          small
          color="primary"
          v-bind="attrs"
          v-on="on"
          @click="menu = true"
        >
          mdi-account
        </e-icon-btn>
      </template>
      <v-card>
        <v-list>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title class="text-h6">
                {{ $auth.user.name }}
              </v-list-item-title>
              <v-list-item-subtitle>
                {{ $auth.user.email }}
              </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-divider />
          <v-list-item link @click="$refs.teams_hierarchy.open()">
            <v-icon left>mdi-routes</v-icon>
            <v-list-item-title>Update Team</v-list-item-title>
          </v-list-item>
          <v-divider />
        </v-list>

        <v-card-text>
          <h3>Groups of Interest</h3>
          <i>You will receive emails based on these preferences.</i>
          <h4>Sites</h4>
          <v-autocomplete
            v-model="watched_groups.sites"
            :items="sites"
            multiple
            clearable
            v-bind="$bind.select"
            :disabled="watched_groups.show_all"
            :placeholder="watched_group_placeholders.site"
            @change="updateWatchedGroups('sites')"
          />
          <h4>Departments</h4>
          <v-autocomplete
            v-model="watched_groups.departments"
            :items="departments"
            multiple
            clearable
            v-bind="$bind.select"
            :disabled="watched_groups.show_all"
            :placeholder="watched_group_placeholders.department"
            @change="updateWatchedGroups('departments')"
          />
          <h4>Object Types</h4>
          <v-autocomplete
            v-model="watched_groups.object_types"
            :items="object_types"
            multiple
            clearable
            v-bind="$bind.select"
            :disabled="watched_groups.show_all"
            :placeholder="watched_group_placeholders.object_type"
            @change="updateWatchedGroups('object_types')"
          />
          <v-checkbox
            v-model="watched_groups.show_all"
            label="Select All Groups"
            @change="saveWatchedGroups"
          />
        </v-card-text>
      </v-card>
    </v-menu>
    <teams-hierarchy
      @change_team="refreshTeam($event)"
      ref="teams_hierarchy"
      update_db
    />
  </div>
</template>

<script>
import TeamsHierarchy from "@/components/Dashboards/TeamsHierarchy";

import { mapGetters } from "vuex";

export default {
  components: {
    TeamsHierarchy,
  },
  data() {
    return {
      menu: false,
      team_name: null,
      watched_group_placeholders: {
        site: "No Sites",
        department: "No Departments",
        object_type: "No Object Types",
      },
      watched_groups: {
        sites: null,
        departments: null,
        object_types: null,
        show_all: false,
      },
    };
  },
  computed: {
    ...mapGetters({
      departments: "lists/getDepartments",
      sites: "lists/getSites",
      object_types: "lists/getObjectTypes",
    }),
  },
  watch: {
    watched_groups: {
      handler: function (newVal, oldVal) {
        if (!newVal.sites && !newVal.departments && !newVal.object_types) {
          this.watched_group_placeholders.site = "No Sites";
          this.watched_group_placeholders.department = "No Departments";
          this.watched_group_placeholders.object_type = "No Object Types";
        } else {
          this.watched_group_placeholders.site = "All Sites";
          this.watched_group_placeholders.department = "All Departments";
          this.watched_group_placeholders.object_type = "All Object Types";
        }
      },
      deep: true,
    },
  },
  created() {
    this.team_name = this.$auth.user.team_name;
    this.watched_groups = JSON.parse(
      JSON.stringify(this.$auth.user.watched_groups)
    );
  },
  methods: {
    refreshTeam(node) {
      this.team_name = node.text;
    },
    // ------------------------------
    updateWatchedGroups(key) {
      if (this.watched_groups[key].length == 0) {
        this.watched_groups[key] = null;
      }

      this.saveWatchedGroups();
    },
    saveWatchedGroups() {
      this.$axios.$post("/user/watched_groups", this.watched_groups);
    },
  },
};
</script>

<style lang="scss" scoped>
table {
  border-collapse: separate;
  border-spacing: 1em 0.5em;
}
</style>
