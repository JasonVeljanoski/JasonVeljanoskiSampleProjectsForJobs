<template>
  <v-dialog v-model="dialog" width="1600">
    <v-card>
      <v-card-title>Change Team</v-card-title>

      <v-card-text>
        <TeamTree :update_db="update_db" />
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-btn v-bind="$bind.btn" outlined color="warning" @click="cancel">
          Close
        </v-btn>
        <v-spacer />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import TeamTree from "@/components/Dashboards/TeamTree";

export default {
  name: "team-tree",
  components: {
    TeamTree,
  },
  props: {
    update_db: { type: Boolean, required: false, default: false },
  },
  data() {
    return {
      dialog: false,
    };
  },
  created() {
    this.$nuxt.$on("change_team", (node, update_db) => {
      this.cancel(node);
    });
  },
  methods: {
    open() {
      this.dialog = true;

      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },
    cancel(node) {
      this.$emit("change_team", node);
      this.dialog = false;
      // this.resolve(false);
    },
  },
};
</script>

<style lang="scss" scoped></style>
