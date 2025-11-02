<template>
  <v-card outlined elevation="0">
    <v-card-title class="att-title">
      Group(s)
      <v-spacer />

      <div class="mr-2">
        <slot name="card:header" />
      </div>

      <workgroup-autocomplete
        :action_id="action.id"
        :action_privacy="action.privacy"
        :existing_workgroups="workgroups"
        @trigger_reload="updateGroups"
      >
        <template #activator="{ on }">
          <v-btn v-bind="$bind.btn" :disabled="!action.id" v-on="on">
            <v-icon left>mdi-plus</v-icon>
            <span>Group</span>
          </v-btn>
        </template>
      </workgroup-autocomplete>
    </v-card-title>

    <v-divider />

    <v-card-text v-if="workgroups.length == 0" class="my-2"> No groups. </v-card-text>

    <e-data-table
      v-else
      :headers="headers"
      :loading="loading"
      :items="workgroups"
      :options="{
        itemsPerPage: 4,
        sortBy: [],
        sortDesc: [],
      }"
      :footer-props="{
        'items-per-page-options': [],
      }"
    >
      <!-- DATA -->
      <template #item.id="{ item }">
        <e-icon-btn tooltip="Go to group" @click="navGroupUrl(item.id)"> mdi-link-variant </e-icon-btn>
      </template>

      <template #item.privacy="{ item }">
        <privacy-enum-icon :value="item.privacy" />
      </template>
    </e-data-table>

    <!-- COMMENT DIALOG -->
    <comment-dialog ref="comment_dialog" />
  </v-card>
</template>

<script>
import WorkgroupAutocomplete from '@/components/Action/WorkgroupAutocomplete.vue'
import CommentDialog from '@/components/Comment/CommentDialog.vue'
import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'
import BooleanIcon from '@/components/Icon/BooleanIcon.vue'

export default {
  components: {
    CommentDialog,
    PrivacyEnumIcon,
    WorkgroupAutocomplete,
  },
  props: {
    action: { type: Object },
    workgroups: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
  },
  data() {
    return {
      files: [],
      headers: [
        {
          text: '#',
          align: 'center',
          value: 'id',
          sortable: false,
          divider: true,
          hide: false,
          width: '10',
        },
        {
          text: 'Privacy',
          value: 'privacy',
          hide: false,
          width: '10',
          divider: true,
          align: 'center',
        },
        {
          text: 'Date Created',
          value: 'created',
          formatter: (x) => this.$format.date(x),
          hide: false,
          width: '10',
          divider: true,
        },
        {
          text: 'Last Updated',
          value: 'updated',
          formatter: (x) => this.$format.date(x),
          hide: false,
          width: '10',
          divider: true,
        },
        {
          text: 'Is Active',
          value: 'is_active',
          hide: false,
          width: '10',
          divider: true,
          align: 'center',
          component: BooleanIcon,
        },
        {
          text: 'Group',
          value: 'title',
          cellClass: 'title-cell',
          hide: false,
          divider: true,
        },
        {
          text: 'Assigned To',
          value: 'owner_id',
          hide: false,
          cellClass: 'nowrap',
          formatter: (x) => this.$utils.getUserName(x),
          width: '10',
        },
        // {
        //   text: 'Members',
        //   value: 'member_ids',
        //   hide: false,
        //   cellClass: 'title-cell',
        //   formatter: (x) =>
        //     x
        //       .map((a) => this.$utils.getUserName(a))
        //       .sort()
        //       .join(', '),
        //   width: '350',
        //   divider: true,
        //   sortable: false,
        // },
        // {
        //   text: 'Admins',
        //   value: 'admin_ids',
        //   hide: false,
        //   cellClass: 'title-cell',
        //   formatter: (x) =>
        //     x
        //       .map((a) => this.$utils.getUserName(a))
        //       .sort()
        //       .join(', '),
        //   width: '350',
        //   divider: true,
        //   sortable: false,
        // },
        // {
        //   text: 'Functional Location',
        //   value: 'functional_location',
        //   hide: false,
        //   cellClass: 'nowrap',
        //   divider: true,
        //   width: '10',
        // },
      ],
    }
  },
  methods: {
    createComment() {
      this.$refs.comment_dialog.open().then((res) => {
        // promise returns false - on cancel
        if (!res) return

        this.$emit('create_comment', res)
      })
    },
    navGroupUrl(id) {
      const text = `${window.location.origin}/groups?id=${id}`
      window.open(text, '_blank')
    },
    updateGroups() {
      // trigger reload on actions table in case 'cancel' button is clicked after changing group
      this.$emit('trigger_reload')

      // --------------------------------------------

      // update privacy of action according to permission system
      // this should match the logic when 'trigger_reload' is called
      if (this.workgroups.length > 0) this.action.privacy = this.workgroups[0].privacy

      // --------------------------------------------

      // update workgroups list according to permission system
      // this should match the logic when 'trigger_reload' is called
      this.$axios.$get('/workgroup/of_action', { params: { action_id: this.action.id } }).then((res) => {
        const res_ids = res.map((a) => a.id)

        // remove any workgroups that are no longer in the list
        let i = 0
        while (i < this.workgroups.length) {
          if (!res_ids.includes(this.workgroups[i].id)) {
            this.workgroups.splice(i, 1)
          } else {
            i++
          }
        }

        // add any new workgroups
        res.forEach((a) => {
          if (!this.workgroups.map((b) => b.id).includes(a.id)) this.workgroups.push(a)
        })
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.attachments {
  display: flex;
  flex-wrap: wrap;
  flex-direction: column;
  gap: 1em;
  overflow-y: auto;
}

.att-title {
  font-size: 16px;
}
</style>
