<template>
  <div class="d-flex justify-center">
    <v-card outlined width="900">
      <v-card-title>
        Notifications ({{ num_of_notifications }})

        <e-icon-btn
          class="ml-auto"
          tooltip="Clear all notifications"
          @click="deleteAllNotifications"
        >
          mdi-close
        </e-icon-btn>
      </v-card-title>
      <v-divider />
      <v-card-text v-if="isLoading" class="d-flex justify-center">
        <v-progress-circular indeterminate color="primary" />
      </v-card-text>

      <v-card-text v-else>
        <div
          class="notification"
          v-for="(notification, index) in orderedNotifications"
          :key="index"
        >
          <div class="d-flex">
            <div>
              <div class="d-flex align-center">
                <v-icon
                  v-if="$enums.notification_types[notification.type] == 'info'"
                  color="info"
                  class="mr-2"
                >
                  mdi-information
                </v-icon>
                <v-icon
                  v-else-if="
                    $enums.notification_types[notification.type] == 'success'
                  "
                  color="success"
                  class="mr-2"
                >
                  mdi-check-circle
                </v-icon>
                <v-icon
                  v-else-if="
                    $enums.notification_types[notification.type] == 'warning'
                  "
                  color="warning"
                  class="mr-2"
                >
                  mdi-alert
                </v-icon>
                <p style="font-weight: 500">
                  {{ notification.title }}
                </p>
              </div>
              <p>{{ notification.message }}</p>
              <p style="font-size: 12px">
                {{ $format.dateTime(notification.created) }}
              </p>
              <small style="font-weight: 500">
                {{ displayTags(notification) }}
              </small>
            </div>
            <div class="ml-auto">
              <e-btn icon @click="deleteNotification(notification)">
                <v-icon>mdi-window-close </v-icon>
              </e-btn>
            </div>
          </div>

          <v-divider class="mt-4" />
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  head() {
    return {
      title: "Notifications",
    };
  },
  data() {
    return {
      isLoading: false,
    };
  },
  computed: {
    ...mapGetters({
      notifications: "socket/notifications",
    }),
    num_of_notifications() {
      if (this.notifications) return this.notifications.length;
    },
    orderedNotifications() {
      const notifications = [...this.notifications];
      notifications.sort((a, b) => new Date(b.created) - new Date(a.created));
      return notifications;
    },
  },
  methods: {
    displayTags(notification) {
      const tags = notification.tags;
      let res = "";
      for (let ii in tags) {
        res += tags[ii];
        if (ii < tags.length - 1) res += " - ";
      }
      return res;
    },
    deleteNotification(notification) {
      const url = `/notification/${notification.id}`;
      this.$axios
        .delete(url)
        .then(() => {
          this.$socket.removeNotification(notification);
        })
        .catch((err) => {
          console.error(err);
        });
    },
    deleteAllNotifications() {
      const confirmed = confirm(
        "Are you sure you want to clear all notifications?"
      );
      if (!confirmed) return;

      const url = "/notification/all";
      this.$axios
        .delete(url)
        .then(() => {
          this.$socket.removeAllNotifications();
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.notification {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;

  p {
    margin-bottom: 0px;
  }
}
</style>
