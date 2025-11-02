<template>
  <div class="analysis-root">
    <base-section title="Event Description">
      <v-form ref="event-desc-form">
        <v-textarea
          v-model="investigation.five_why.event_description"
          v-bind="$bind.textarea"
          :rules="[
            $form.required(investigation.five_why.event_description),
            $form.length(investigation.five_why.event_description, 850),
          ]"
          hide-details="auto"
          counter="850"
        />
      </v-form>
    </base-section>

    <scroll-btn ref="why-scroll-btn" :unfoil="unfoil" @click="validateEventDesc()"> Why? </scroll-btn>

    <cause-card
      ref="cause-card"
      v-show="show_cause_card"
      :response="investigation.five_why.root_response"
      :been_split="split_reason"
      @scroll_down="show_solution = true"
      @cause_change="
        hideActions();
        hideSolution();
      "
    />

    <scroll-btn
      v-show="show_cause_card"
      ref="cause-scroll-btn"
      :class="{ split: split_reason }"
      :unfoil="unfoil"
      class="actions-btn"
      @click="validateCauseCard($refs['cause-card'])"
    >
      Go To Actions
    </scroll-btn>

    <actions-table
      v-if="show_action"
      :investigation_id="investigation.id"
      :actions="investigation.five_why.actions"
      hide_button
      type="five_why"
      class="mt-n4"
      @loading="updateActionsTableLoader($event)"
    />

    <flash-report-actions
      v-if="show_action"
      :investigation_id="investigation.id"
      :five_why="investigation.five_why"
      :actions="investigation.flash_report.actions"
      hide_button
      @loading="updateActionsTableLoader($event)"
    />

    <div v-if="show_action" class="ml-auto mr-auto mt-2" style="width: 1200px">
      <v-btn
        :disabled="!is_my_investigation && !$perms.is_admin && !is_new_five_why"
        color="success"
        @click="showSolution()"
      >
        <v-icon left>mdi-arrow-down-left-bold</v-icon>
        Accountability
      </v-btn>
    </div>

    <div ref="solution-scroll" />
    <base-section v-if="show_solution" title="Accountability" class="mt-4">
      <solution ref="solution" :investigation="investigation" />
    </base-section>

    <v-btn
      v-if="sumitable"
      :disabled="(!is_my_investigation && !$perms.is_admin && !is_new_five_why) || actions_table_loader"
      class="mt-1"
      color="success"
      @click="submit()"
    >
      <v-icon left>mdi-content-save</v-icon>
      Submit 5-Why
    </v-btn>
    <v-btn
      v-else
      :disabled="!is_my_investigation && !$perms.is_admin"
      class="mt-1"
      color="success"
      @click="$emit('save')"
    >
      <v-icon left>mdi-content-save</v-icon>
      Save Progress
    </v-btn>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import EventDesc from "@/components/FiveWhy/EventDesc";
import CauseCard from "@/components/FiveWhy/CauseCard";
import Solution from "@/components/FiveWhy/Solution";
import ScrollBtn from "@/components/FiveWhy/ScrollBtn";
import ActionsTable from "@/components/Investigation/Actions/ActionsTable";
import FlashReportActions from "@/components/FiveWhy/FlashReportActions.vue";

export default {
  name: "FiveWhyAnalysis",
  components: {
    EventDesc,
    CauseCard,
    Solution,
    ScrollBtn,
    ActionsTable,
    FlashReportActions,
  },
  props: {
    investigation: { type: Object },
    unfoil: { type: Boolean, default: false },
  },
  data() {
    return {
      actions_table_loader: false,
      show_cause_card: false,
      show_action: false,
      show_solution: false,
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
    split_reason() {
      // Inner Function to handle recursive tree traversal
      let checkForSplit = (node) => {
        // Base Case - Check if current node has >1 children
        if (node.children_responses.length > 1) {
          return true;
        }
        // Recurse to all children
        for (let child of node.children_responses) {
          if (checkForSplit(child)) {
            return true;
          }
        }
      };
      // Call recursive function and return result
      return checkForSplit(this.investigation.five_why.root_response);
    },
    // feature: anyone can make a five why if it is being created for the first time
    //          users can create five whys on behalf of someone else
    is_new_five_why() {
      return this.investigation.five_why.id == null;
    },
    sumitable() {
      return (
        this.show_solution &&
        this.investigation.five_why.owner_ids.length > 0 &&
        this.investigation.five_why.supervisor_id
      );
    },
  },
  watch: {
    "investigation.five_why.actions": function (val) {
      if (val.length === 0) {
        this.show_solution = false;
      }
    },
    unfoil: function (newVal, oldVal) {
      if (newVal) {
        this.show_cause_card = true;
        this.show_action = true;
        this.show_solution = true;
      }
    },
  },
  mounted() {
    this.investigation.five_why.event_datetime = this.investigation.event_datetime;

    // --------------

    // link 5-why to investigation
    const query = this.$route.query;
    if (query) {
      this.investigation.five_why.investigation_id = query.id;
    }

    // --------------

    // populate `event description` with default information to get the ball rolling
    let total_effective_duration = this.investigation.total_effective_duration;
    if (total_effective_duration) total_effective_duration = total_effective_duration.toFixed(2);
    else total_effective_duration = 0.0;
    let total_tonnes_lost = this.investigation.total_tonnes_lost || 0.0;
    if (total_tonnes_lost) total_tonnes_lost = total_tonnes_lost.toFixed(1);
    else total_tonnes_lost = 0.0;

    if (!this.investigation.five_why.event_description) {
      const description = `At ${this.$format.time(this.investigation.event_datetime)} on ${this.$format.date(
        this.investigation.event_datetime
      )}, ${
        this.investigation.description
      }. Event had an Effective Duration of ${total_effective_duration} hours and ${total_tonnes_lost} tonnes. `;
      this.investigation.five_why.event_description = description;
    }

    // --------------

    // init unfoil process
    if (this.unfoil) {
      this.show_cause_card = true;
      this.show_action = true;
      this.show_solution = true;
    }
  },
  methods: {
    // -----------------------------
    // ACTIONS
    // -----------------------------
    updateActionsTableLoader(flag) {
      this.actions_table_loader = flag;
    },
    addAction(action) {
      this.investigation.five_why.actions.push(action);
      this.$utils.scrollToElement("solution-scroll", this);
    },
    showActions() {
      this.show_action = true;
      this.$refs["cause-scroll-btn"].disable = true;
    },
    hideActions() {
      this.show_action = false;
      this.$refs["cause-scroll-btn"].disable = false;
    },
    // -----------------------------
    // SOLUTION
    // -----------------------------
    showSolution() {
      this.show_solution = true;
      this.$utils.scrollToElement("solution-scroll", this);
      // if (this.investigation.five_why.actions.length != 0) {
      //   this.show_solution = true;
      //   this.$utils.scrollToElement("solution-scroll", this);
      // } else {
      //   let title = `<h4>Five Why</h4>`;
      //   let message = "You must create at least one action to continue!";
      //   const body = title + message;
      //   this.$snackbar.add(body, "error", 5);
      // }
    },
    hideSolution() {
      this.show_solution = false;
    },
    // -----------------------------
    // VALIDATION
    // -----------------------------
    validateEventDesc() {
      if (this.$refs["event-desc-form"].validate()) {
        this.show_cause_card = true;
        this.$refs["why-scroll-btn"].disable = true;
      }
    },
    validateCauseCard(root_cause_card) {
      let flags = [];
      let q = new this.$adt.Queue();

      q.enqueue(root_cause_card);

      while (!q.isEmpty) {
        let v = q.dequeue();

        const form = v.$refs["cause-form"];
        const children = v.$refs["children"];

        // save validation status
        flags.push(form.validate());

        if (children) for (const child of children) q.enqueue(child);
      }

      // validated ONLY if all flags are true
      if (!flags.includes(false)) {
        this.showActions();
      } else {
        this.hideActions();
      }
    },
    // -----------------------------
    // SUBMIT
    // -----------------------------
    submit() {
      if (this.$refs["solution"].$refs["solution-form"].validate()) {
        this.$emit("submit");
        // if (this.investigation.five_why.actions.length == 0) {
        //   const message = "You must create at least one action!";
        //   this.$snackbar.add(message, "warning");
        // } else {
        //   this.$emit("submit");
        // }
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.analysis-root {
  margin: 0 auto;
  min-height: 800px;

  width: 1200px;

  ::v-deep .v-card {
    width: 100%;
  }
}

.actions-btn {
  margin-top: -25px;
  margin-left: 1px;

  position: relative;

  &.split::before {
    content: "";
    position: absolute;
    left: calc(25% - 8px);
    right: calc(25% - 9px);
    top: 0px;
    border-top: solid thin var(--v-accent-base);
  }
}
</style>
