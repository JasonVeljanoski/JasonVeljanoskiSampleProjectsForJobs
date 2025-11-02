<template>
  <div v-if="$perms.is_super && enums" class="d-flex" style="gap: 8px">
    <enum-edit-card base_url="/enums/priority" title="Priority" :values="enums.priority" />
    <enum-edit-card base_url="/enums/status" title="Status" :values="enums.status" />
    <enum-edit-card base_url="/enums/trigger" title="Trigger" :values="enums.trigger" />
    <enum-edit-card base_url="/enums/primary_driver" title="Primary Driver" :values="enums.primary_driver" />
    <enum-edit-card base_url="/enums/secondary_driver" title="Secondary Driver" :values="enums.secondary_driver" />
    <enum-edit-card
      base_url="/enums/cost_benefit_category"
      title="Cost Benefit"
      :values="enums.cost_benefit_category"
    />
    <enum-edit-card base_url="/enums/benefit_frequency" title="Benefit Frequency" :values="enums.benefit_frequency" />
  </div>
</template>

<script>
import EnumEditCard from '@/components/admin/EnumEditCard.vue'

export default {
  components: {
    EnumEditCard,
  },
  data() {
    return {
      enums: null,
    }
  },
  mounted() {
    this.$axios.$get('/enums/all').then((res) => {
      this.enums = res
    })
  },
  methods: {},
}
</script>

<style lang="scss" scoped></style>
