<template>
  <v-menu v-model="menu" offset-y min-width="200" :close-on-content-click="false">
    <template #activator="{ on, attrs }">
      <div v-bind="attrs" class="d-flex" v-on="on">
        <e-icon-btn tooltip="Mention">mdi-at</e-icon-btn>
      </div>
    </template>
    <v-card v-if="menu" dense>
      <user-autocomplete
        ref="user_select"
        v-bind="$bind.select"
        :items="users"
        :clearable="false"
        autofocus
        item-value="email"
        prepend-inner-icon=""
        placeholder="Type a user..."
        @change="mention($event)"
      />
    </v-card>
    <!-- <v-list dense>
      <v-subheader>MENTION</v-subheader>
      <v-divider />
      <v-list-item @click="mention('assignee')">
        <v-list-item-subtitle> Assignee </v-list-item-subtitle>
      </v-list-item>
      <v-list-item @click="mention('members')">
        <v-list-item-subtitle> Members </v-list-item-subtitle>
      </v-list-item>
      <v-list-item @click="mention('supervisor')">
        <v-list-item-subtitle> Supervisor </v-list-item-subtitle>
      </v-list-item>
      <v-list-item @click="mention('all')">
        <v-list-item-subtitle> All </v-list-item-subtitle>
      </v-list-item>
      <v-subheader>OTHER</v-subheader>
      <v-divider />

      <v-list-item>
        <v-list-item-content>
          <user-autocomplete
            ref="user_select"
            v-bind="$bind.select"
            :items="users"
            :clearable="false"
            item-value="email"
            prepend-inner-icon=""
            placeholder="Type a user..."
            @change="mention($event)"
          />
        </v-list-item-content>
      </v-list-item>
    </v-list> -->
  </v-menu>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  data() {
    return {
      menu: false,
    }
  },
  computed: {
    ...mapGetters({
      users: 'user/getUsers',
    }),
  },
  methods: {
    open() {
      this.menu = true
    },
    focus() {
      this.$nextTick(() => {
        this.$refs.user_select.$refs.input.focus()
        this.$refs.user_select.$refs.input.activateMenu()
      })
    },
    mention(text) {
      // user autocomplete gives an email. Only 'mention' the username
      text = text.split('@')[0]

      this.$emit('mention', `@${text}`)
      this.menu = false
    },
  },
}
</script>

<style></style>
