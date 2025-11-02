<template>
  <div
    v-if="investigation.steps_completed >= 1"
    :class="{ modal: full_screen_table }"
    class="scroll-area forgiveness"
  >
    <investigation-table :investigation="investigation" />
    <v-btn
      :disabled="
        !is_my_investigation && !$perms.is_admin && !is_new_flash_report
      "
      class="mt-n16"
      color="success"
      @click="$emit('scroll_down')"
    >
      <v-icon left>mdi-arrow-down-left-bold</v-icon>
      Create Flash Report
    </v-btn>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import InvestigationTable from "@/components/Investigation/Investigation/InvestigationTable";

export default {
  name: "LearnFromPastFailures",
  components: {
    InvestigationTable,
  },
  props: {
    investigation: { type: Object },
  },
  data() {
    return {
      full_screen_table: false,
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    // feature: anyone can make a flash report if it is being created for the first time
    //          users can create flash reports on behalf of someone else
    is_new_flash_report() {
      return this.investigation.flash_report.id == null;
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.scroll-area {
  padding-top: calc(#{$stepper-height} + 10px);
  scroll-snap-align: none;
}

.forgiveness {
  padding-bottom: 0px;
}

.title {
  text-align: center;
  width: 100%;
  font-size: 14px !important;
  margin-bottom: -26px;
}

.progress {
  width: 100%;
}

.sticky {
  position: fixed;
  width: 100%;
  top: #{$header-height};
  z-index: 5;
}

.footer {
  margin: 10px;
  position: fixed;
  bottom: 0;
  right: 0;
  background-color: var(--v-primary-base);
}

.stepper {
  cursor: pointer;

  &:hover {
    background-color: rgba(0, 0, 0, 0.03);
  }
}

.modal {
  position: fixed;
  z-index: 10;
  padding-top: 100px;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.25);
  overflow: hidden;
}
</style>
