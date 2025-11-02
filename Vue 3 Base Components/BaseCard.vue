<template>
  <div class="base-card" data-testid="base-card">
    <!--#region Header -->
    <div>
      <slot name="header">
        <span class="base-card--header" data-testid="base-card-header">{{
          title
        }}</span>
      </slot>
    </div>
    <!--#endregion    -->

    <!--#region Body -->
    <div class="base-card--body" data-testid="base-card-body">
      <slot />
    </div>
    <!--#endregion    -->

    <!--#region Footer -->
    <div
      v-if="$slots.footer"
      class="base-card--footer"
      data-testid="base-card-footer"
    >
      <slot name="footer" />
    </div>
    <!--#endregion    -->
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '',
  },
})
</script>

<style lang="scss" scoped>
.base-card {
  display: flex;
  flex-direction: column;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border-radius: 12px;
  padding: 24px;

  &--header {
    font-family: Rubik;
    font-size: 16px;
    font-weight: 400;
  }

  &--body {
    flex: 1;
    overflow-y: auto;
    max-height: 100%;
  }

  &--footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>
