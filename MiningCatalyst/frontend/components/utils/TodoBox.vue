<template>
  <div class="todo_box">
    <i>Todo.</i>

    <v-tooltip v-if="tooltip" bottom>
      <template #activator="{ on }">
        <v-icon right v-on="on">mdi-information-box-outline</v-icon>
      </template>
      <span>{{ tooltip }}</span>
    </v-tooltip>
  </div>
</template>

<script>
export default {
  name: 'TodoBox',
  props: {
    tooltip: {
      type: String,
    },
  },
}
</script>

<style lang="scss" scoped>
.todo_box {
  display: flex;
  background-color: var(--v-accent-base);
  border: 1px var(--v-accent-base);
  border-radius: 5px;
  padding: 7px;
  // margin: 5px;
  // max-width: 200px;
}
</style>
