<template>
  <div class="root">
    <!-- FIVE WHY DOCUMENT -->
    <div v-if="investigation.investigation_type_id === getTypeID('FIVEWHY')">
      <!-- CREATE MODE -->
      <div v-if="!preview_mode">
        <h2>Create your 5-Why Document</h2>
        <the-five-why-analysis
          :investigation="investigation"
          @submit="
            preview_mode = true;
            $emit('five_why_submitted');
          "
        />
      </div>

      <!-- PREVIEW MODE -->
      <div class="d-flex justify-center" v-else>
        <v-card class="preview-root" max-width="1200" v-bind="$bind.card">
          <div class="button-wrapper">
            <v-btn @click="preview_mode = false" v-bind="$bind.btn">
              Edit
            </v-btn>
            <v-btn :href="five_why_doc" v-bind="$bind.btn"> Download </v-btn>
          </div>
        </v-card>
      </div>
    </div>

    <!-- RCA DOCUMENT -->
    <div v-else-if="investigation.investigation_type_id === getTypeID('RCA')">
      <h2>RCA ANALYSIS</h2>
      <base-section title="" max-width="1200" class="ml-auto mr-auto mb-2">
        <div style="height: 600px">RCA doc goes here....</div>
      </base-section>
    </div>
  </div>
</template>

<script>
import TheFiveWhyAnalysis from "@/components/FiveWhy/TheFiveWhyAnalysis";

export default {
  props: {
    investigation: { Object },
  },
  components: {
    TheFiveWhyAnalysis,
  },
  data() {
    return {
      types: [],
      preview_mode: false,
      document_path: null,
      document: null,
    };
  },
  computed: {
    five_why_doc() {
      const path = this.$enums.document_paths["five_why"];
      const fname = `five_why_${this.investigation.id}.docx`;
      return this.$document.download(`${path}/${fname}`);
    },
  },
  methods: {
    getTypeID(payload) {
      for (const _type of this.types) {
        if (_type.type.localeCompare(payload)) {
          return _type.id;
        }
      }
    },
  },
  mounted() {
    // ---------------------------------
    // FETCH LIST OF INVESTIGATION TYPES
    // ---------------------------------
    this.$axios
      .$get("/investigation/types")
      .then((res) => {
        // update types with result
        this.types = res;

        // ---------------------------------
        // FETCH EXISTING 5-WHY (IF ANY)
        // requires this.types
        // ---------------------------------
        const query = this.$route.query;
        if (
          Object.keys(query).length !== 0 &&
          this.investigation.investigation_type_id === this.getTypeID("FIVEWHY")
        ) {
          this.$axios
            .$get("/five_why", {
              params: { investigation_id: this.$route.query.id },
            })
            .then((res) => {
              if (res) {
                // populate five-why
                this.investigation.five_why.investigation_id =
                  res.investigation_id;
                this.investigation.five_why.event_description =
                  res.event_description;
                this.investigation.five_why.actions = res.actions;
                this.investigation.five_why.participants = res.participants;
                this.investigation.five_why.root_response = res.root_response;
                this.investigation.five_why.supervisor = res.supervisor;

                // preview mode
                this.preview_mode = true;
              }
            })
            .catch((err) => {
              console.error(err);
            });
        }
      })
      .catch((err) => {
        console.error(err);
      });
  },
};
</script>

<style lang="scss" scoped>
$header-height: 64px;
$stepper-height: 72px;

.root {
  display: flex;
  flex-direction: column;
  gap: 16px;

  height: 100%;

  overflow-y: auto;
}
h2 {
  text-align: center;
  color: var(--v-primary-base);
}

.preview-root {
  width: 100%;
  height: calc(100vh - #{$header-height} - #{$stepper-height} - 40px);
  border-radius: 5px;

  iframe {
    width: 100%;
    height: 100%;
    border: 0px;
  }

  .button-wrapper {
    position: relative;
    float: right;
    right: 20px;
    bottom: 50px;
  }
}
</style>
