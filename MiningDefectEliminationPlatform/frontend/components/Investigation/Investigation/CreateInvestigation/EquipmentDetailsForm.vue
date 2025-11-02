<template>
  <div class="form-box">
    <h3>Equipment Details</h3>

    <h4>Equipment Functional Location</h4>
    <function-location-autocomplete
      v-model="investigation.function_location"
      :loading="equipmentLoading || floc_loading"
      :items="filtered_function_locations"
      :rules="[$form.required(investigation.function_location)]"
      v-bind="$bind.select"
      clearable
      @change="clearEquipmentSelectors('function_location')"
    />

    <div class="d-flex">
      <h4>Equipment</h4>
      <v-icon class="ml-2" small>mdi-filter-variant</v-icon>
    </div>
    <v-autocomplete
      v-model="investigation.equipment_description"
      v-bind="$bind.select"
      :loading="equipmentLoading || equipmentDesLoading"
      :items="filtered_equipment_descriptions"
      :rules="[$form.required(investigation.equipment_description)]"
      hide-details="auto"
      clearable
      @change="clearEquipmentSelectors('equipment_description')"
    />

    <div class="d-flex">
      <h4>Object Type</h4>
      <v-icon class="ml-2" small>mdi-filter-variant</v-icon>
      <small class="ml-2">(auto)</small>
    </div>
    <v-autocomplete
      v-model="investigation.object_type"
      v-bind="$bind.select"
      :loading="equipmentLoading || equipmentDesLoading"
      :items="object_type_items"
      :rules="[$form.required(investigation.object_type)]"
      hide-details="auto"
      clearable
      @change="clearEquipmentSelectors('object_type')"
    />

    <div class="d-flex justify-between">
      <div class="mr-2">
        <div class="d-flex">
          <h4>Object Part</h4>
          <v-icon class="ml-2" small>mdi-filter-variant</v-icon>
        </div>
        <v-autocomplete
          v-model="investigation.object_part_description"
          v-bind="$bind.select"
          :loading="equipmentLoading || equipmentDesLoading || object_damage_loading"
          :items="object_part_items"
          :rules="[$form.required(investigation.object_part_description)]"
          hide-details="auto"
          clearable
        />
      </div>
      <div class="ml-2">
        <div class="d-flex">
          <h4>Damage Code</h4>
          <v-icon class="ml-2" small>mdi-filter-variant</v-icon>
        </div>
        <v-autocomplete
          v-model="investigation.damage_code"
          v-bind="$bind.select"
          :loading="equipmentLoading || equipmentDesLoading || object_damage_loading"
          :items="damage_code_items"
          :rules="[$form.required(investigation.damage_code)]"
          hide-details="auto"
          clearable
        />
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: {
    investigation: { type: Object },
  },
  data() {
    return {
      // loading
      floc_loading: false,
      equipmentLoading: false,
      object_damage_loading: false,
      equipmentDesLoading: false,
      // items
      filtered_equipment_descriptions: [],
      filtered_function_locations: [],
      // other
      filtered_equipments: [],
      // object_types: [],
      filtered_object_parts: [],
      filtered_damage_codes: [],
    };
  },
  computed: {
    ...mapGetters({
      function_locations: "lists/getFunctionLocations",
      object_types: "lists/getObjectTypes",
      equipments: "lists/getEquipments",
    }),
    // --------------------
    // FLAGS
    // --------------------
    is_loading() {
      return this.equipmentLoading || this.object_damage_loading || this.equipmentDesLoading;
    },
    // --------------------
    // INCIDENT DATA
    // --------------------
    object_type_items() {
      if (this.investigation.function_location != null && this.investigation.equipment_description != null)
        return this.object_types;
      return [];
    },
    object_part_items() {
      if (
        this.investigation.function_location != null &&
        this.investigation.equipment_description != null &&
        this.investigation.object_type != null
      )
        return this.filtered_object_parts;
      return [];
    },
    damage_code_items() {
      if (
        this.investigation.function_location != null &&
        this.investigation.equipment_description != null &&
        this.investigation.object_type != null
      )
        //Temp FIx
        this.filtered_damage_codes.push("Ripped");
      return this.filtered_damage_codes;
    },
  },
  watch: {
    is_loading() {
      this.$emit("loading", this.is_loading);
    },
    "investigation.owner_ids"(newVal) {
      // Select user and back-to-back (max len 2). Overwrite old if overflow.
      if (newVal.length == 3) {
        // update owner_ids for front-end
        this.investigation.owner_ids.shift();
      }
    },
    function_locations() {
      this.filtered_function_locations = this.function_locations;
    },
    equipments() {
      this.filtered_equipments = this.equipments;
    },
    async "investigation.function_location"() {
      if (this.investigation.function_location) {
        this.equipmentDesLoading = true;
        this.filtered_equipments = await this.$import.filterEquipmentByFunctionLocation(
          this.investigation.function_location
        );

        this.filtered_equipment_descriptions = this.$utils.uniqueList(
          this.filtered_equipments,
          "equipment_description"
        );
        this.equipmentDesLoading = false;
      } else {
        this.filtered_equipment_descriptions = this.equipments;
      }
    },
    async "investigation.equipment_description"() {
      if (this.investigation.equipment_description) {
        this.floc_loading = true;
        this.filtered_function_locations = await this.$import.filterFunctionLocationByEquipment(
          this.investigation.equipment_description
        );

        this.filtered_function_locations = this.$utils.uniqueList(
          this.filtered_function_locations,
          "function_location"
        );
        this.floc_loading = false;
      } else {
        this.filtered_function_locations = this.function_locations;
      }
    },
    "investigation.catalog_profile"() {
      if (this.investigation.object_type) this.getObjectAndDamage();
    },
    "investigation.catalog_profiles"() {
      if (this.investigation.object_type) this.getObjectAndDamage();
    },
  },
  mounted() {
    this.filtered_equipment_descriptions = this.equipments;
    this.filtered_function_locations = this.function_locations;
  },
  methods: {
    changeLoading(flag) {
      this.isLoading = flag;
    },
    clearEquipmentSelectors(payload) {
      if (payload === "function_location") {
        // ability to reverse selection: select Equipment first and then select a filtered Function Location; else as normal
        if (this.investigation.function_location != null && this.investigation.equipment_description != null) {
          this.getUniqueObjectType();
        } else {
          this.investigation.equipment_description = null;
          this.investigation.object_type = null;
          this.investigation.catalog_profile = null;
          this.investigation.catalog_profiles = [];
          this.investigation.object_part_description = null;
          this.investigation.damage_code = null;
        }
      } else if (payload === "equipment_description") {
        this.investigation.object_type = null;
        this.investigation.catalog_profile = null;
        this.investigation.catalog_profiles = [];
        this.investigation.object_part_description = null;
        this.investigation.damage_code = null;
        this.getUniqueObjectType();
      } else if (payload === "object_type") {
        this.investigation.object_part_description = null;
        this.investigation.damage_code = null;
        this.getCatalogProfilesByObjectType();
      }
    },
    getUniqueObjectType() {
      const function_location = this.investigation.function_location;
      const equipment_description = this.investigation.equipment_description;
      if (function_location == null || equipment_description == null) return;

      this.equipmentLoading = true;

      this.$axios
        .$get("/incident/default_object_type_and_cat_profile", {
          params: {
            function_location: function_location,
            equipment_description: equipment_description,
          },
        })
        .then((res) => {
          this.investigation.object_type = res.object_type;
          this.investigation.catalog_profile = res.catalog_profile;
          this.investigation.site = res.site;
          this.investigation.department = res.department;

          this.equipmentLoading = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    filterEquipmentByFunctionLocation() {
      const function_location = this.investigation.function_location;
      if (function_location == null) return;
      this.equipmentDesLoading = true;
      this.$axios
        .$get("/incident/filter_equipment_by_function_locations", {
          params: {
            function_location: function_location,
          },
        })
        .then((res) => {
          this.filtered_equipments = res;

          this.equipmentDesLoading = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    getCatalogProfilesByObjectType() {
      const object_type = this.investigation.object_type;
      if (object_type == null) return;

      this.object_damage_loading = true;

      this.$axios
        .$get("/incident/filtered_cat_profiles_by_object_type", {
          params: {
            object_type: object_type,
          },
        })
        .then((res) => {
          this.investigation.catalog_profiles = res;

          this.object_damage_loading = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    getObjectAndDamage() {
      // check if catalog_profiles is populated. i.e. another object type has been selected
      let items = [];
      if (this.investigation.catalog_profiles.length > 0) {
        items = this.investigation.catalog_profiles;
      } else {
        const function_location = this.investigation.catalog_profile;
        const equipment_description = this.investigation.equipment_description;
        if (function_location == null || equipment_description == null) return;
        items = [this.investigation.catalog_profile];
      }

      this.object_damage_loading = true;

      this.$axios
        .$post("/incident/objects_and_damages_by_catalog_profiles", items)
        .then((res) => {
          this.filtered_object_parts = res.object_parts;
          this.filtered_damage_codes = res.damage_codes;

          this.object_damage_loading = false;
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.form-box {
  max-width: 400px;
  width: 100%;
}

h3 {
  color: var(--v-primary-base);
  margin-bottom: 5px;
  font-weight: 400;
}
</style>
