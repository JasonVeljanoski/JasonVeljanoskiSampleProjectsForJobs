<template>
  <v-badge
    color="primary"
    overlap
    offset-x="20"
    offset-y="22"
    :value="noOfNotifications"
    :content="noOfNotifications"
  >
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <e-icon-btn tooltip="Notifications" v-bind="attrs" v-on="on">
          mdi-email
        </e-icon-btn>
      </template>

      <v-card class="item-card">
        <v-list style="width: 400px">
          <template v-if="anyNotifications">
            <v-list-item
              v-for="(notification, index) in topFiveNotifications"
              :key="index"
            >
              <v-list-item-content>
                <v-list-item-title class="d-flex align-center">
                  <v-icon
                    v-if="
                      $enums.notification_types[notification.type] == 'success'
                    "
                    :color="$enums.notification_types[notification.type]"
                    left
                  >
                    mdi-check-circle
                  </v-icon>
                  <v-icon
                    v-if="
                      $enums.notification_types[notification.type] == 'info'
                    "
                    :color="$enums.notification_types[notification.type]"
                    left
                  >
                    mdi-information
                  </v-icon>
                  <v-icon
                    v-if="
                      $enums.notification_types[notification.type] == 'warning'
                    "
                    :color="$enums.notification_types[notification.type]"
                    left
                  >
                    mdi-alert
                  </v-icon>

                  <div class="action-title">{{ notification.title }}</div>
                  <div class="ml-auto">
                    {{ $format.timeSince(notification.created) }} ago
                  </div>
                </v-list-item-title>

                <v-list-item-subtitle
                  class="action-title"
                  style="white-space: normal"
                >
                  {{ notification.message }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-divider />
            <v-list-item to="/notifications">See More</v-list-item>
          </template>
          <template v-else>
            <v-list-item> No notifications. </v-list-item>
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
      notifications: "socket/notifications",
    }),
    anyNotifications() {
      return this.notifications !== null && this.notifications.length > 0;
    },
    noOfNotifications() {
      if (this.notifications) return this.notifications.length;
    },
    topFiveNotifications() {
      if (this.notifications) {
        const notifications = [...this.notifications];
        notifications.sort((a, b) => new Date(b.created) - new Date(a.created));

        if (notifications.length <= 5) return notifications;
        return notifications.slice(0, 5);
      }
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
