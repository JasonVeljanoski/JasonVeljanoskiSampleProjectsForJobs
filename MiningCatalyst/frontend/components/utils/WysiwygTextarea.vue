<template>
  <WYSIWYG v-bind="{ ...$attrs, ...$props }" v-on="$listeners" />
</template>

<script>
import WYSIWYG from '@/components/utils/WYSIWYG.vue'
export default {
  components: {
    WYSIWYG,
  },
}
</script>
