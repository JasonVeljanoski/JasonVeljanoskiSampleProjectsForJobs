<template>
  <v-expansion-panels v-model="panel">
    <!-- INVESTIGATIONS PANEL -->
    <v-expansion-panel v-model="panel" expand>
      <v-expansion-panel-header>
        Open Investigations ({{ num_of_investigations }})
      </v-expansion-panel-header>
      <v-expansion-panel-content v-if="num_of_investigations == 0">
        You have no unprocessed investigations
      </v-expansion-panel-content>
      <v-expansion-panel-content v-else class="panel">
        <investigation-table :items="ordered_investigations" />
      </v-expansion-panel-content>
    </v-expansion-panel>

    <!-- ACTIONS PANEL -->
    <v-expansion-panel v-model="panel">
      <v-expansion-panel-header>
        Open Actions ({{ num_of_actions }})
      </v-expansion-panel-header>
      <v-expansion-panel-content v-if="num_of_actions == 0">
        You have no unprocessed actions
      </v-expansion-panel-content>
      <template v-else>
        <v-expansion-panel-content class="panel">
          <action-table :items="ordered_actions" />
        </v-expansion-panel-content>
      </template>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script>
import { mapGetters } from "vuex";
import InvestigationTable from "@/components/Alerts/InvestigationTable";
import ActionTable from "@/components/Alerts/ActionTable";

export default {
  components: {
    InvestigationTable,
    ActionTable,
  },
  head() {
    return {
      title: "Alerts",
    };
  },
  data() {
    return {
      panel: 0,
      isLoading: false,
    };
  },
  computed: {
    ...mapGetters({
      investigations: "socket/investigations",
      actions: "socket/actions",
    }),
    num_of_actions() {
      return this.actions.length;
    },
    num_of_investigations() {
      return this.investigations.length;
    },
    ordered_investigations() {
      return [...this.investigations].sort(
        (a, b) => new Date(b.updated) - new Date(a.updated)
      );
    },
    ordered_actions() {
      const actions = this.actions.map((a) => {
        return { ...a };
      });

      actions.sort((a, b) => new Date(b.updated) - new Date(a.updated));

      return actions;
    },
  },
};
</script>

<style lang="scss" scoped>
// .panel {
//   max-height: 500px;
//   background-color: red;
// }
</style>
