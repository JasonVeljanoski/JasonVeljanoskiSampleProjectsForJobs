<template>
  <v-dialog v-model="dialog" width="1200" persistent>
    <v-card v-bind="$bind.card" width="1200" class="ml-auto mr-auto">
      <v-card-title>
        Distribute Report
        <v-spacer />
        <hidden-text-field placeholder="Enter Email" @submit="addEmail($event)">
          <template #activator="{ on }">
            <e-icon-btn tooltip="Add Extra Email" v-on="on">mdi-plus</e-icon-btn>
          </template>
        </hidden-text-field>
      </v-card-title>
      <v-divider />
      <span class="body-wrapper">
        <v-card-text>
          <v-form ref="form">
            <h4>EMAIL GROUP:</h4>
            <div class="d-flex justify-space-between" style="gap: 16px">
              <div>
                <h4>Site</h4>
                <v-text-field
                  :placeholder="site"
                  :items="sites"
                  multiple
                  clearable
                  v-bind="$bind.select"
                  disabled
                  style="width: 300px"
                />

                <h4>Department</h4>
                <v-text-field
                  :placeholder="department"
                  :items="departments"
                  multiple
                  clearable
                  v-bind="$bind.select"
                  disabled
                  style="width: 300px"
                />

                <h4>Object Type</h4>
                <v-text-field
                  :placeholder="object_type"
                  :items="object_types"
                  multiple
                  clearable
                  v-bind="$bind.select"
                  disabled
                  style="width: 300px"
                />
              </div>
              <div style="width: 100%">
                <span class="d-flex">
                  <h4>Email Group Users:</h4>
                  <small class="ml-2">({{ site }}, {{ department }}, {{ object_type }})</small>
                </span>
                <v-autocomplete
                  v-model="watched_groups"
                  v-bind="$bind.select"
                  :items="watched_groups"
                  multiple
                  readonly
                  append-icon=""
                >
                  <template #selection="data">
                    <v-chip v-bind="data.attrs" :input-value="data.selected">
                      {{ data.item }}
                    </v-chip>
                  </template>
                </v-autocomplete>
              </div>
            </div>

            <h4>DISTRIBUTION EMAIL LIST:</h4>
            <v-combobox v-model="email.dist_emails" v-bind="$bind.select" :items="dist_emails" clearable multiple>
              <template #selection="data">
                <v-chip
                  v-bind="data.attrs"
                  :input-value="data.selected"
                  close
                  @click="data.select"
                  @click:close="remove(data.item)"
                >
                  {{ data.item }}
                </v-chip>
              </template>
            </v-combobox>

            <span class="d-flex">
              <h4>EXTRA USERS:</h4>
              <small class="ml-2"> (Optional) </small>
            </span>

            <user-list-autocomplete
              v-model="email.users"
              v-bind="$bind.select"
              :items="users"
              item-text="filter_name"
              item-value="email"
              clearable
              multiple
            />
          </v-form>
        </v-card-text>
      </span>
      <v-divider />
      <v-card-actions>
        <cancel-btn @click="cancel" />
        <v-spacer />
        <v-btn :disabled="false" color="primary" @click="submit">
          <v-icon left>mdi-send</v-icon>
          Send
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: {
    site: {
      type: String,
      required: true,
    },
    department: {
      type: String,
      required: true,
    },
    object_type: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      dialog: false,
      email: {
        message: null,
        users: [],
        site: this.site,
        department: this.department,
        object_type: this.object_type,
        dist_emails: [],
      },
      watched_groups: [],
      dist_emails: [],
      resolve: null,
      reject: null,
    };
  },
  computed: {
    ...mapGetters({
      users: "user/getUsers",
      departments: "lists/getDepartments",
      sites: "lists/getSites",
      object_types: "lists/getObjectTypes",
      email_lists: "lists/getEmailLists",
    }),
  },
  methods: {
    // ------------------------------------
    // DIALOG
    // ------------------------------------
    open() {
      this.dialog = true;

      this.email.message = null;
      this.email.users = [];
      this.dist_emails = [];
      this.watched_groups = [];
      this.$refs.form?.reset();

      this.getWatchedGroups();
      this.initDistributionEmails();

      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },
    cancel() {
      this.dialog = false;

      // ------

      this.$refs.form.reset();
      this.email.message = null;
      this.email.users = [];

      // ------

      this.resolve(false);
    },
    submit() {
      if (this.$refs.form.validate()) {
        this.resolve(this.email);
        this.dialog = false;
      }
    },
    // ------------------------------------
    // EMAIL DISTRIBUTION
    // ------------------------------------
    initDistributionEmails() {
      const site = this.site.toLowerCase();
      const department = this.department.toLowerCase();
      const object_type = this.object_type.toLowerCase();

      for (const [k1, v1] of Object.entries(this.email_lists)) {
        if (k1 == site || k1 == "*") {
          for (const [k2, v2] of Object.entries(v1)) {
            if (k2 == department || k2 == "*") {
              for (const [k3, v3] of Object.entries(v2)) {
                if (k3 == object_type || k3 == "*") {
                  this.dist_emails = [...this.dist_emails, ...v3];
                }
              }
            }
          }
        }
      }

      // select all by default
      this.email.dist_emails = [...this.dist_emails];
    },
    getWatchedGroups() {
      this.$axios
        .$get("/email/get_watched_groups", {
          params: {
            site: this.site,
            department: this.department,
            object_type: this.object_type,
          },
        })
        .then((res) => {
          this.watched_groups = res;
        });
    },
    remove(item) {
      const index = this.email.dist_emails.indexOf(item);
      if (index >= 0) this.email.dist_emails.splice(index, 1);
    },
    addEmail(email) {
      this.email.dist_emails.push(email);
    },
  },
};
</script>

<style lang="scss" scoped></style>
