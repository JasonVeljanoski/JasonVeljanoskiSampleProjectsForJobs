<template>
  <div>
    <shared-learnings-form v-if="!preview_mode" :investigation="investigation" @save="onSave" />
    <shared-learnings-prev
      v-else
      :investigation="investigation"
      :download_name="download_name"
      :loading="loading || report_loading"
      @edit="preview_mode = false"
    />
  </div>
</template>

<script>
import SharedLearningsForm from "@/components/Investigation/SharedLearnings/SharedLearningsForm";
import SharedLearningsPrev from "@/components/Investigation/SharedLearnings/SharedLearningsPrev";

export default {
  components: {
    SharedLearningsForm,
    SharedLearningsPrev,
  },
  props: {
    investigation: { Object },
    loading: { type: Boolean, default: false },
  },
  data() {
    return {
      preview_mode: false,
      report_loading: false,
    };
  },
  computed: {
    download_name() {
      return this.$document.download_name(
        this.investigation.function_location,
        "Shared_Learnings",
        this.investigation.id,
        this.investigation.title
      );
    },
  },
  mounted() {
    if (this.investigation.shared_learning.id) this.preview_mode = true;
  },
  methods: {
    exists() {
      const path = this.$enums.document_paths["shared_learnings"];
      const fname = `shared_learnings_${this.investigation_id}.pdf`;
      this.$axios
        .get(`/document/exists/${path}/${fname}`)
        .then((res) => {
          this.preview_mode = res;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    onSave() {
      this.investigation.shared_learning.investigation_id = this.investigation.id;
      this.report_loading = true;
      this.preview_mode = true;

      this.$axios
        .$put("investigation/create_update/shared_learnings", this.investigation.shared_learning)
        .then((res) => {
          this.investigation.shared_learning = res;

          this.$document
            .create_shared_learnings_report(this.investigation.id)
            .then(() => {
              this.report_loading = false;

              // ---------------------------------------------

              const STEPS_COMPLETED = 6;
              this.$axios
                .$patch("/investigation/save_steps", null, {
                  params: {
                    investigation_id: this.investigation.id,
                    steps_completed: STEPS_COMPLETED,
                  },
                })
                .then(() => {
                  if (this.investigation.steps_completed < STEPS_COMPLETED)
                    this.investigation.steps_completed = STEPS_COMPLETED;
                })
                .catch((err) => {
                  console.error(err);
                });

              // ---------------------------------------------
            })
            .catch((err) => console.error(err));
        })
        .catch((err) => console.error(err));
    },
  },
};
</script>
