<template>
  <div>
    <!-- users can see privacy status -->
    <privacy-enum-icon :value="value" />
  </div>
</template>

<script>
import PrivacyEnumIcon from '@/components/Icon/PrivacyEnumIcon.vue'

export default {
  components: {
    PrivacyEnumIcon,
  },
  props: {
    value: { type: Number, default: false },
  },
  data() {
    return {
      menu: false,
      items: [
        { enum: 1, icon: 'mdi-lock-open-variant-outline', colour: '', text: this.$enums.privacy[1] },
        { enum: 3, icon: 'mdi-lock-outline', colour: '', text: this.$enums.privacy[3] },
      ],
    }
  },
  methods: {},
}
</script>

<style></style>
