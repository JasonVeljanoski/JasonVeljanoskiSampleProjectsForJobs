<template>
  <div>
    <!-- PROGRESS TRACKER -->
    <div class="d-flex justify-center">
      <v-stepper v-model="current_step" v-bind="$bind.stepper" class="my-2 sticky" max-width="1200">
        <v-stepper-header>
          <div v-if="investigation.id" class="title">Investigation #{{ investigation.id }}</div>
          <v-stepper-step
            class="stepper"
            step="1"
            :complete="investigation.steps_completed > 0"
            @click="elementScroll('page1')"
          >
            Create Investigation
          </v-stepper-step>
          <v-divider />
          <v-stepper-step
            class="stepper"
            step="2"
            :complete="investigation.steps_completed > 1"
            @click="elementScroll('page2')"
          >
            Learn From Past Failures
          </v-stepper-step>
          <v-divider />
          <v-stepper-step
            class="stepper"
            step="3"
            :complete="investigation.steps_completed > 2"
            @click="elementScroll('page3')"
          >
            Create Flash Report
          </v-stepper-step>

          <template v-if="!is_flash_report_only">
            <v-divider />
            <v-stepper-step
              class="stepper"
              step="4"
              :complete="investigation.steps_completed > 3"
              @click="elementScroll('page4')"
            >
              Conduct Analysis
            </v-stepper-step>
            <v-divider />
            <v-stepper-step
              class="stepper"
              step="5"
              :complete="investigation.steps_completed > 4"
              @click="elementScroll('page5')"
            >
              Root Cause Details
            </v-stepper-step>
            <v-divider />
            <v-stepper-step
              class="stepper"
              step="6"
              :complete="investigation.steps_completed > 5"
              @click="elementScroll('page6')"
            >
              Shared Learnings
            </v-stepper-step>
          </template>
        </v-stepper-header>
      </v-stepper>
    </div>

    <!-- MAIN CARDS -->
    <div ref="page1" />
    <create-investigation
      :investigation="investigation"
      :items="items"
      @scroll_up="elementScroll('page1')"
      @scroll_down="scrollDownPage(1)"
      @created="updateIsFlashreportOnly()"
      @flash_report_loading="updateFlashReportLoading($event)"
      @shared_learning_loading="updateSharedLearningLoading($event)"
    />

    <div ref="page2">
      <learn-from-past-failures :investigation="investigation" @scroll_down="scrollDownPage(2, false, true)" />
    </div>

    <div ref="page3">
      <create-flash-report
        :investigation="investigation"
        :preview-mode="preview_flashreport"
        :loading="flash_report_loading"
        @scroll_up="elementScroll('page3')"
        @scroll_down="scrollDownPage(3, false, true)"
        @last_page="scrollDownPage(3, true)"
        @shared_learning_loading="updateSharedLearningLoading($event)"
      />
    </div>

    <!-- [4] 5-WHY OR RCA ANALYSIS -->
    <div v-if="investigation.steps_completed >= 3 && !is_flash_report_only" class="scroll-area forgiveness" ref="page4">
      <template v-if="investigation.investigation_type === 1">
        <the-five-why
          :investigation="investigation"
          @next="scrollDownPage(4, false, true)"
          @scroll_up="elementScroll('page4')"
          @preview="elementScroll('page4')"
          @shared_learning_loading="updateSharedLearningLoading($event)"
        />
      </template>
      <template v-else-if="investigation.investigation_type === 2">
        <the-rca :investigation="investigation" @next="scrollDownPage(4)" />
      </template>
    </div>

    <!-- [5] ROOT CAUSE DETAILS -->
    <div v-if="investigation.steps_completed >= 4 && !is_flash_report_only" class="scroll-area" ref="page5">
      <the-root-cause
        :investigation="investigation"
        @scroll_up="elementScroll('page5')"
        @next="scrollDownPage(5)"
        @shared_learning_loading="updateSharedLearningLoading($event)"
      />
    </div>

    <!-- [6] SHARED LEARNINGS -->
    <div v-if="investigation.steps_completed >= 5 && !is_flash_report_only" class="scroll-area" ref="page6">
      <shared-learnings
        :investigation="investigation"
        :loading="shared_learning_loading"
        @scroll_up="elementScroll('page6')"
      />
    </div>
  </div>
</template>

<script>
import CreateInvestigation from "@/components/Investigation/Investigation/Sections/CreateInvestigation";
import LearnFromPastFailures from "@/components/Investigation/Investigation/Sections/LearnFromPastFailures";
import CreateFlashReport from "@/components/Investigation/Investigation/Sections/CreateFlashReport";

import CreateInvestigationForm from "@/components/Investigation/Investigation/CreateInvestigation/CreateInvestigationForm";
import InvestigationTable from "@/components/Investigation/Investigation/InvestigationTable";
import FlashReportForm from "@/components/Investigation/FlashReport/FlashReportForm";
import FlashReportPrev from "@/components/Investigation/FlashReport/FlashReportPrev";
import InvestigationAnalysis from "@/components/Investigation/Investigation/InvestigationAnalysis";
import TheFiveWhy from "@/components/Investigation/Investigation/TheFiveWhy";
import TheRca from "@/components/Investigation/Investigation/TheRCA";
import TheRootCause from "@/components/Investigation/RootCauseDetails/TheRootCause";
import SharedLearnings from "@/components/Investigation/SharedLearnings/SharedLearnings";

export default {
  name: "NewInvestigation",
  components: {
    CreateInvestigation,
    LearnFromPastFailures,
    CreateFlashReport,
    CreateInvestigationForm,
    InvestigationTable,
    FlashReportForm,
    FlashReportPrev,
    InvestigationAnalysis,
    TheFiveWhy,
    TheRca,
    TheRootCause,
    SharedLearnings,
  },
  props: {
    items: {
      type: Array,
      default: null,
    },
  },
  data() {
    return {
      full_screen_table: false,
      preview_flashreport: false,
      is_flash_report_only: false,
      flash_report_loading: false,
      shared_learning_loading: false,

      investigation: {
        status: 1,
        total_tonnes_lost: 0.0,
        total_effective_duration: 0.0,

        id: null,
        created: null,
        updated: null,
        title: null,
        description: null,
        priority: null,
        working_folder_link: null,
        investigation_type: null,
        function_location: null,
        catalog_profile: null,
        catalog_profiles: [],
        object_part_description: null,
        damage_code: null,
        equipment_description: null,
        object_type: null,
        site: null,
        department: null,
        owner_ids: [this.$auth.user.id],
        owners: [],
        supervisor_id: null,
        aplus_delay_event_ids: [],
        rems_delay_event_ids: [],
        event_type: null,
        event_datetime: null,
        date_closed: null,
        completion_due_date: null,
        cause: null,
        cause_code: null,
        relevant_investigation_ids: [],
        steps_completed: null,
        aplus_delay_events: [],
        rems_delay_events: [],
        relevant_investigations: [],
        actions: [],
        general_attachments: [],
        five_why: {
          id: null,
          created: null,
          updated: null,
          investigation_id: null,
          root_response_id: null,
          event_description: null,
          owners: [],
          owner_ids: [],
          flash_report_action_ids: [],
          supervisor_id: null,
          is_complete: false,
          root_response: {
            id: null,
            created: null,
            updated: null,
            cause: null,
            reason: null,
            files: [],
            filenames: [],
            children_responses: [], // next response in the form of another root_response obj.
          },
          actions: [],
        },
        flash_report: {
          id: null,
          created: null,
          updated: null,
          investigation_id: null,
          event_title: null,
          event_description: null,
          business_impact: null,
          immediate_action_taken: null,
          sufficient_inventory_levels: false,
          potential_root_causes: [],
          delay_event_ids: [],
          actions: [],
          files: [],
          filenames: [],
        },
        root_cause_detail: {
          id: null,
          created: null,
          updated: null,
          investigation_id: null,
          cause_code: null,
          description: null,
          additional_contribution_factors: null,
          cause_category: null,
          actions: [],
          files: [],
          filenames: [],
          rca_doc: null,
          rca_filename: null,
        },
        shared_learning: {
          investigation_id: null,
          event_title: null,
          event_description: null,
          reason: null,
          shared_learning: null,
          initiative_images: [],
        },
      },
    };
  },
  computed: {
    current_step() {
      return this.investigation.steps_completed + 1;
    },
  },
  mounted() {
    this.setupInvestigation();
  },
  methods: {
    // -----------------------------
    // UTILITY
    // -----------------------------
    elementScroll(ref_name) {
      this.$utils.scrollToElement(ref_name, this);
    },
    updateInvestigationSteps(page, flashOnly = false) {
      if (flashOnly == true) {
        this.$axios.$patch("/investigation/save_steps", null, {
          params: {
            investigation_id: this.investigation.id,
            steps_completed: page,
          },
        });
        this.$router.push({
          name: "investigations",
        });
      } else {
        if (page > this.investigation.steps_completed) {
          this.investigation.steps_completed = page;
        } else page = -1;

        return this.$axios.$patch("/investigation/save_steps", null, {
          params: {
            investigation_id: this.investigation.id,
            steps_completed: page,
          },
        });
      }
    },
    updateSteps(page) {
      if (page > this.investigation.steps_completed) {
        this.investigation.steps_completed = page;
      } else page = null;

      this.$axios
        .$patch("/investigation/save_steps", null, {
          params: {
            investigation_id: this.investigation.id,
            steps_completed: page,
          },
        })
        .catch((err) => {
          console.error(err);
        });
    },
    updateIsFlashreportOnly() {
      this.is_flash_report_only = this.investigation.investigation_type == 3;
    },
    scrollDownPage(num, flashOnly = false, force_scroll = false) {
      if (flashOnly) this.updateInvestigationSteps(num, flashOnly);
      else {
        this.updateInvestigationSteps(num).then(() => {
          // Hacks on hacks on hacks
          const scroll_when_save_on_last_available_page = this.investigation.steps_completed == num;
          const stop_scrolling_if_save_page1_and_on_step2 = this.investigation.steps_completed - 1 != 0;

          if ((scroll_when_save_on_last_available_page && stop_scrolling_if_save_page1_and_on_step2) || force_scroll) {
            this.elementScroll(`page${num + 1}`);
          }
        });
      }
    },
    // // -----------------------------
    // // PUSH NOTIFICATION
    // // -----------------------------
    // warningMessage(title, message) {
    //   this.$snackbar.add(message, "warning");
    // },
    // -----------------------------
    // FLASH REPORT
    // -----------------------------
    updateFlashReportLoading(flag) {
      this.flash_report_loading = flag;
    },
    updateSharedLearningLoading(flag) {
      this.shared_learning_loading = flag;
    },
    async initFlashReportFormValues() {
      // investigation id should always exist
      // that is to say that you must create an investigation before you get here
      this.investigation.flash_report.investigation_id = this.investigation.id;

      // -----------------------------
      // POPULATE WHAT YOU CAN FROM PREV FORMS
      // only if null (you do NOT want to overwrite existing work!)
      // -----------------------------

      // title
      if (this.investigation.flash_report.event_title == null) {
        this.investigation.flash_report.event_title = this.investigation.title;
      }

      // total event duration
      // this.events = await this.$import.getFilteredAPLUSEventDetails(
      //   this.investigation.aplus_delay_event_ids
      // );
      let total_effective_duration = this.investigation.total_effective_duration;
      if (total_effective_duration) total_effective_duration = total_effective_duration.toFixed(2);
      else total_effective_duration = 0.0;
      let total_tonnes_lost = this.investigation.total_tonnes_lost || 0.0;
      if (total_tonnes_lost) total_tonnes_lost = total_tonnes_lost.toFixed(1);
      else total_tonnes_lost = 0.0;
      let total_event_duration = this.investigation.total_event_duration;
      if (total_event_duration) total_event_duration = total_event_duration.toFixed(2);
      else total_event_duration = 0.0;

      // description
      const flash_rep_description = this.investigation.flash_report.event_description;
      if (!flash_rep_description) {
        const description = `At ${this.$format.time(this.investigation.event_datetime)} on ${this.$format.date(
          this.investigation.event_datetime
        )}, ${
          this.investigation.description
        }. Event resulted in ${total_effective_duration} hours of Effective Downtime.`;
        this.investigation.flash_report.event_description = description;
      }
    },
    // -----------------------------
    // INVESTIGATION
    // -----------------------------
    setupInvestigation() {
      // GET CURRENT INVESTIGATION (IF ANY)
      // otherwise we are creating a new one
      // -----------------

      // get router params if exist
      const query = this.$route.query;

      if (Object.keys(query).includes("id") && query.type !== "REMS") {
        // get the appropriate investigation
        this.$axios
          .$get("/investigation", { params: { id: parseInt(query.id) } })
          .then((res) => {
            // UPDATE INVESTIGATION
            // update investigation object
            // -----------------
            // EVENT DETAILS

            res.event_datetime = this.$format.initDate(res.event_datetime);
            res.completion_due_date = this.$format.initDate(res.completion_due_date);
            res.date_closed = this.$format.initDate(res.date_closed);

            // FLASH REPORT
            if (res.flash_report === null) {
              res.flash_report = {
                id: null,
                created: null,
                updated: null,
                investigation_id: null,
                event_title: null,
                event_description: null,
                business_impact: null,
                immediate_action_taken: null,
                sufficient_inventory_levels: false,
                potential_root_causes: [],
                delay_event_ids: [],
                actions: [],
                files: [],
                filenames: [],
                attachments: [],
                attachment_names: [],
              };
            } else {
              // res.flash_report.event_datetime = this.$format.initDate(
              //   res.flash_report.event_datetime
              // );
              this.preview_flashreport = true;
            }

            // FIVE WHY
            if (res.five_why === null) {
              res.five_why = {
                id: null,
                created: null,
                updated: null,
                investigation_id: null,
                root_response_id: null,
                event_description: null,
                owners: [],
                owner_ids: [],
                flash_report_action_ids: [],
                supervisor_id: null,
                is_complete: false,
                root_response: {
                  id: null,
                  created: null,
                  updated: null,
                  cause: null,
                  reason: null,
                  files: [],
                  filenames: [],
                  children_responses: [], // next response in the form of another root_response obj.
                },
                actions: [],
              };
            } else {
              // res.five_why.event_datetime = this.$format.initDate(
              //   res.five_why.event_datetime
              // );
            }

            // ROOT CAUSE DETAILS
            if (res.root_cause_detail === null) {
              res.root_cause_detail = {
                id: null,
                created: null,
                updated: null,
                investigation_id: null,
                cause_code: null,
                description: null,
                additional_contribution_factors: null,
                cause_category: null,
                actions: [],
                files: [],
                filenames: [],
                rca_doc: null,
                rca_filename: null,
              };
            }

            if (res.shared_learning === null) {
              res.shared_learning = {
                investigation_id: null,
                event_title: null,
                event_description: null,
                reason: null,
                shared_learning: null,
                initiative_images: [],
              };
            }

            this.investigation = res;

            // init is_flash_report_only flag
            this.is_flash_report_only = this.investigation.investigation_type == 3;

            // must be after this.investigation is populated
            this.initFlashReportFormValues();
          })
          .catch((err) => {
            console.error(err);
          })
          .finally(() => {
            // NAVIGATE
            // navigate to correct page (i.e. always scroll to bottom on mounted)
            // unless investigation is complete (then scroll only to top)
            // -----------------
            this.$nextTick(() => {
              const MAX_STEPS = 5;
              if (this.current_step <= MAX_STEPS) {
                this.elementScroll(`page${this.current_step}`, this);
              }
            });
          });
      }
    },
    navigateActions(payload) {
      this.$router.push({
        path: "/actions",
        query: { id: payload.id },
      });
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.scroll-area {
  padding-top: calc(#{$stepper-height} + 10px);
  // height: calc(100vh - #{$header-height} - 24px);

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
