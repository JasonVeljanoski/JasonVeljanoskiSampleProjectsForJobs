<template>
  <v-badge
    color="primary"
    overlap
    offset-x="20"
    offset-y="22"
    :value="no_of_alerts"
    :content="no_of_alerts"
  >
    <v-menu open-on-hover offset-y>
      <template v-slot:activator="{ on, attrs }">
        <e-icon-btn v-bind="attrs" v-on="on" @click="alerts_page">
          mdi-bell
        </e-icon-btn>
      </template>
      <v-card class="item-card">
        <v-list style="width: 400px">
          <template v-if="any_alerts">
            <v-list-item
              v-for="(alert, index) in top_five_alerts"
              :key="index"
              @click="navigate(alert.id, alert.type)"
            >
              <v-list-item-content>
                <v-list-item-title class="d-flex">
                  <v-icon v-if="alert.type == 'ACTION'" left>
                    mdi-clock-fast
                  </v-icon>
                  <v-icon v-if="alert.type == 'INVESTIGATION'" left>
                    mdi-application-edit-outline
                  </v-icon>
                  <div class="action-title">{{ alert.title }}</div>
                  <div class="ml-auto">
                    {{ $format.timeSince(alert.updated) }} ago
                  </div>
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <v-list-item @click="alerts_page">See More</v-list-item>
          </template>
          <template v-else>
            <v-list-item> No investigations or actions. </v-list-item>
          </template>
        </v-list>
      </v-card>
    </v-menu>
  </v-badge>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  computed: {
    ...mapGetters({
      investigations: "socket/investigations",
      actions: "socket/actions",
    }),
    any_alerts() {
      return (
        (this.actions !== null && this.actions.length > 0) ||
        (this.investigations !== null && this.investigations.length > 0)
      );
    },
    no_of_alerts() {
      if (this.actions) return this.actions.length + this.investigations.length;
    },
    top_five_alerts() {
      const ACTION = "ACTION";
      const INVESTIGATION = "INVESTIGATION";

      let actions = [];
      let investigations = [];

      if (this.actions && this.investigations) {
        actions = this.actions.map((a) => {
          return {
            id: a.id,
            title: a.title,
            updated: a.updated,
            message: a.message,
            type: ACTION,
          };
        });

        investigations = this.investigations.map((a) => {
          if (a)
            return {
              id: a.id,
              title: a.title,
              updated: a.updated,
              message: a.description,
              type: INVESTIGATION,
            };
        });

        const alerts = actions.concat(investigations);
        alerts.sort((a, b) => new Date(b.updated) - new Date(a.updated));

        if (alerts.length <= 5) return alerts;
        return alerts.slice(0, 5);
      }
    },
  },
  methods: {
    navigate(alert_id, alert_type) {
      const ACTION = "ACTION";
      const INVESTIGATION = "INVESTIGATION";

      if (alert_type == ACTION)
        window.open(
          `${window.location.origin}/actions?action_id=${alert_id}`,
          "_blank"
        );
      else if (alert_type == INVESTIGATION)
        window.open(
          `${window.location.origin}/investigations?id=${alert_id}`,
          "_blank"
        );
    },
    alerts_page() {
      window.open(`${window.location.origin}/alerts`, "_blank");
    },
  },
};
</script>

<style lang="scss" scoped>
.action-title {
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 200px;
}
</style>
