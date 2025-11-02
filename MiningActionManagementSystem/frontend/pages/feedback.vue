<template>
  <v-card class="feedback-root" outlined>
    <e-data-table
      :loading="loading"
      :headers="headers"
      :items="feedback_items"
      :search="search"
      multi-sort
      fixed-header
      :footer-props="{
        'items-per-page-options': [30, 50, 100],
      }"
      @clear="clearFilters()"
    >
      <template #top>
        <v-card-title class="header">
          Feedback
          <v-spacer />
          <v-text-field
            v-model="search"
            v-bind="$bind.select"
            clearable
            placeholder="Global Text Search"
            prepend-inner-icon="mdi-magnify"
            style="max-width: 350px"
          />
        </v-card-title>
        <v-divider />
      </template>

      <!-- DATA TABLE SLOTS -->
      <template #item.id="{ item }">
        <copy-icon-btn @click="copyFeedbackUrl(item.id)" />
      </template>

      <template #item.edit="{ item }">
        <e-icon-btn tooltip="Edit Feedback" @click="editFeedback(item)"> mdi-pencil </e-icon-btn>
      </template>

      <template #item.summary="{ item }">
        <table-text-tooltip v-if="item.summary" :text="item.summary" />
      </template>
      <template #item.replicate="{ item }">
        <table-text-tooltip v-if="item.replicate" :text="item.replicate" />
      </template>
    </e-data-table>

    <!-- ENTRY FORM -->
    <feedback-form ref="feedback_form" @add_feedback="submitFeedback($event)" />
  </v-card>
</template>

<script>
import { mapGetters } from 'vuex'
import FeedbackForm from '@/components/Feedback/FeedbackForm'
import CopyIconBtn from '@/components/Icon/CopyIconBtn.vue'

export default {
  components: {
    FeedbackForm,
    CopyIconBtn,
  },
  data() {
    return {
      loading: false,
      total_items: 0,
      search: null,
      options: {
        itemsPerPage: 20,
        sortBy: [],
        sortDesc: [],
      },

      // table
      feedback_items: [],
      headers: this.$table_headers.feedback,

      // filters
      global_text: null,
      filters: {
        global_text: null,
        id: null,
        reason: [],
        status: [],
        created_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        owner_id: null,
        page: null,
        replicate: null,
      },
    }
  },
  head() {
    return {
      title: 'Feedback',
    }
  },
  computed: {
    ...mapGetters({
      users: 'user/getUsers',
    }),
  },
  watch: {
    options: {
      handler() {
        this.loadData()
      },
      deep: true,
    },
    filters: {
      handler() {
        this.loadData()
      },
      deep: true,
    },
    '$route.query'() {
      // if /feedback?id=1 then user clicks menu to go to /feedback, must repopulate table
      this.loadData()
    },
  },
  created() {
    this.$nuxt.$on('force_load_data_update', () => {
      this.loadData()
    })
  },
  mounted() {
    this.loadData()
  },
  beforeDestroy() {
    this.$nuxt.$off('open-contact-form')
  },
  methods: {
    // -----------------------------
    // TABLE DATA
    // -----------------------------
    filterFeedbacksByID(id) {
      this.loading = true
      this.$axios
        .$get('/feedback', { params: { id } })
        .then((res) => {
          this.feedback_items = res
          this.total_items = res.length
          this.loading = false
        })
        .catch((err) => console.error(err))
    },
    loadData() {
      const query = this.$route.query
      if (Object.keys(query).includes('id')) {
        this.filterFeedbacksByID(query.id)
        return
      }

      // ------------------------------------------

      this.loading = true
      this.$axios
        .$get('/feedback/all')
        .then((res) => {
          this.feedback_items = res
        })
        .finally(() => (this.loading = false))
    },
    // -----------------------------
    // FILTERS
    // -----------------------------
    clearFilters() {
      this.options = {
        sortBy: [],
        sortDesc: [],
        page: 1,
        itemsPerPage: 20,
      }

      this.global_text = null

      this.filters = {
        id: null,
        reason: [],
        status: [],
        created_date: {
          min_date: null,
          max_date: null,
        },
        updated_date: {
          min_date: null,
          max_date: null,
        },
        owner_id: null,
        page: null,
        replicate: null,
      }
    },
    // -----------------------------
    // FEEDBACK
    // -----------------------------
    editFeedback(feedback) {
      if (feedback) this.$refs.feedback_form.open(feedback)
    },
    submitFeedback(payload) {
      this.loading = true

      // ---------------------------
      // handle attachments + its metadata (sending attachments through pydantic sucks...)

      const form_data = new FormData()

      const attachments = payload.attachments
      const files_metadatas = []
      for (const attachment of attachments) {
        files_metadatas.push({
          title: attachment.title,
          description: attachment.description,
          network_drive_link: attachment.network_drive_link,
        })

        form_data.append('attachments', attachment.file)
      }

      const feedback = payload.feedback
      feedback.general_attachments_metas = files_metadatas
      form_data.append('edits', JSON.stringify(feedback))

      // ----------------------------

      this.$axios
        .$put('feedback', form_data)
        .then((res) => {
          res.created = this.$format.initDate(res.created)
          res.updated = this.$format.initDate(res.updated)

          const idx = this.feedback_items.findIndex((x) => x.id == res.id)

          if (idx != -1) this.feedback_items.splice(idx, 1)

          this.feedback_items.unshift(res)

          // --------------------------------
          const message = feedback.id ? `Feedback Item Updated Successfully` : `Feedback Item Created Successfully`
          this.$snackbar.add(message)
          this.loading = false
          // --------------------------------

          if (payload.to_email) {
            this.$axios
              .$post('/feedback/send_email', null, {
                params: { feedback_id: res.id },
              })
              .catch((err) => console.error(err))
          }
        })
        .catch((err) => console.error(err))
    },
    copyFeedbackUrl(id) {
      const text = `${window.location.origin}/feedback?id=${id}`
      navigator.clipboard.writeText(text)
    },
    // -----------------------------
    // GLOBAL TEXT SEARCH FILTER
    // -----------------------------
    searchGlobalText() {
      this.filters.global_text = this.global_text
    },
    clearGlobalText() {
      this.filters.global_text = null
    },
  },
}
</script>

<style lang="scss" scoped>
.feedback-root {
  height: 100%;

  .header {
    color: var(--v-primary-base);
  }

  ::v-deep {
    .filter-table > * > table > * > tr > * {
      &:nth-child(-n + 2) {
        position: sticky;
        z-index: 2;
        background: var(--default-background);
      }

      &:nth-child(1) {
        left: 0;
      }

      &:nth-child(2) {
        left: 69px;
      }
    }
    .filter-table > * > table > * > tr > th {
      &:nth-child(-n + 2) {
        z-index: 4;
      }
    }
  }
}
</style>
