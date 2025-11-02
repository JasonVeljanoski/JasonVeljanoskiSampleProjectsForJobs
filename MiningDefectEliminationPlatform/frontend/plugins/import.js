export default ({ app }, inject) => {
  inject("import", {
    // check the below if called more than once otherwise remove from here
    filterEquipmentByFunctionLocation(function_location) {
      return app.$axios
        .$get("/incident/filter_equipment_by_function_locations", {
          params: {
            function_location: function_location,
          },
        })
        .then((res) => {
          return res;
        })
        .catch((err) => {
          console.error(err);
        });
    },
    filterFunctionLocationByEquipment(equipment) {
      return app.$axios
        .$get("/incident/filter_function_locations_by_equipment", {
          params: {
            equipment: equipment,
          },
        })
        .then((res) => {
          return res;
        })
        .catch((err) => {
          console.error(err);
        });
    },
  });
};
