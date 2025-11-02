<template>
  <v-tooltip bottom max-width="300">
    <template #activator="{ on, attrs }">
      <span v-bind="attrs" v-on="on">
        {{
          item.members
            .map((a) => $utils.getUserName(a.user_id))
            .sort()
            .join(", ")
        }}
      </span>
    </template>
    <ul v-for="member in item.members" :key="member.user_id" style="list-style-type: none; padding: 0">
      <li>{{ $utils.getUserName(member.user_id) }}</li>
    </ul>
  </v-tooltip>
</template>

<script>
export default {
  props: {
    item: {
      type: Object,
      required: true,
    },
  },
};
</script>
