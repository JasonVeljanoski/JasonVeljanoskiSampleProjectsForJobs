<template>
  <div>
    <!-- EDIT AREA -->
    <v-card-title>Edit Area</v-card-title>
    <v-card-text>
      <WYSIWYG ref="wysiwyg" :disabled="!edit_mode">
        <template #card:footer>
          <v-spacer />

          <save-btn v-bind="$bind.btn" :outlined="!edit_mode" @click="handleSave">
            <v-icon left>{{ edit_mode ? 'mdi-content-save' : 'mdi-pencil' }}</v-icon>
            {{ edit_mode ? 'Save' : 'Edit' }}
          </save-btn>
        </template>
      </WYSIWYG>
    </v-card-text>

    <!-- PREVIEW AREA -->
    <v-card-title>Preview Area</v-card-title>

    <v-card-text>
      <i> Here is a preview to see how the changes will appear to users upon activation. </i>
      <div class="d-flex justify-center self-center my-4">
        <v-card max-width="1200" width="100%" outlined>
          <v-card-title>Latest ACE Updates</v-card-title>
          <v-progress-linear v-if="loading" indeterminate />
          <v-divider />
          <v-card-text>
            <div v-if="!loading" class="html_render" v-html="news?.content ? news.content : 'No Content'" />
          </v-card-text>
          <v-divider />
          <v-card-actions>
            <v-spacer />
            <v-checkbox label="Don't show again" hide-details disabled class="mx-4 my-2" />
            <v-btn v-bind="$bind.btn" disabled> OK </v-btn>
          </v-card-actions>
        </v-card>
      </div>
      <v-switch
        :value="news?.active"
        :disabled="!news?.id"
        label="Activate feature for all users"
        @change="changeActiveStatus"
      />
    </v-card-text>

    <!-- HISTORY AREA -->
    <!-- <v-card outlined elevation="0" max-width="1200" class="mx-auto">
      <v-card-title>
        User Update Comms
        <v-spacer />
        <v-btn v-bind="$bind.btn" color="primary">
          <v-icon left>mdi-plus</v-icon>
          Add New
        </v-btn>
      </v-card-title>

      <v-divider />
      <v-card-text v-if="non_deleted_history.length == 0" class="my-2"> No dashboards. </v-card-text>

      <e-data-table
        v-else
        :headers="headers"
        :items="non_deleted_history"
        fixed-header
        :item-class="rowClass"
        :options="{
          itemsPerPage: 10,
          sortBy: ['created'],
          sortDesc: [true],
        }"
        :footer-props="{
          'items-per-page-options': [],
        }"
      >
        <template #item.preview="{ item }">
          <e-icon-btn tooltip="Preview"> mdi-open-in-new </e-icon-btn>
        </template>
        <template #item.remove="{ item }">
          <e-icon-btn color="error" tooltip="Remove" @click="removeHistory(item.id)"> mdi-delete </e-icon-btn>
        </template>
      </e-data-table>
    </v-card> -->
  </div>
</template>

<script>
import WYSIWYG from '~/components/Utils/WYSIWYG.vue'

export default {
  components: {
    WYSIWYG,
  },
  data() {
    return {
      edit_mode: false,
      news: null,
      loading: false,
      history: [],

      headers: [
        {
          text: 'Preview',
          value: 'preview',
          width: '10',
          divider: true,
          sortable: false,
          align: 'center',
        },
        { text: 'Created', value: 'created', divider: true, formatter: (x) => this.$format.dateTime(x) },
        {
          text: 'Created By',
          value: 'user_id',
          divider: true,
          formatter: (x) => this.$utils.getUserName(x),
        },
        {
          text: 'Remove',
          value: 'remove',
          width: '10',
          sortable: false,
          align: 'center',
        },
      ],
    }
  },
  computed: {
    non_deleted_history() {
      return this.history.filter((x) => !x.deleted)
    },
  },
  mounted() {
    this.getLatestUpdateNews()

    this.$axios.$get('/log/history').then((res) => {
      this.history = res
    })
  },
  methods: {
    // ------------------------------------
    // NEWS
    // ------------------------------------
    handleSave() {
      this.edit_mode = !this.edit_mode

      if (!this.edit_mode) {
        this.$axios
          .$post('/log/create_history', null, {
            params: {
              content: this.$refs.wysiwyg.content,
            },
          })
          .then((res) => {
            this.news = res
          })
      }
    },
    getLatestUpdateNews() {
      this.loading = true
      this.$axios.$get('/log/latest_update').then((res) => {
        this.news = res

        this.$refs.wysiwyg.content = this.news.content

        this.loading = false
      })
    },
    changeActiveStatus(e) {
      const flag = e == true
      this.$axios.$put('/log/update_history_activate', null, {
        params: {
          id: this.news.id,
          active: flag,
        },
      })
    },
    // ------------------------------------
    // HISTORY
    // ------------------------------------
    removeHistory(id) {
      if (!confirm('Are you sure you want to remove this?')) {
        return
      }

      console.log('todo')
    },
    rowClass(x) {
      if (x.active) return 'active_row'
    },
  },
}
</script>

<style lang="scss" scoped>
.active_row {
  color: red;
  background-color: green;
}
</style>
