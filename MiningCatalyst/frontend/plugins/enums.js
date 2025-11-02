export default ({ app, store }, inject) => {
  inject('enums', {
    initiative_types: {
      general_improvement: 'General Improvement',
      // non_floc_specific: 'Non-FLOC Specific',
      // maintenance_improvement: 'Maintenance Improvement',
      // maintenance_project: 'Maintenance Project',
      // cost_reduction: 'Cost Reduction',
      // safety: 'Safety',
      // capital: 'Capital',
    },

    // -------------------------------------------

    converter(items) {
      if (Array.isArray(items)) {
        return items
      }

      return Object.entries(items).map(([k, v]) => ({
        value: parseInt(k) || k,
        text: v,
      }))
    },

    async importAllEnums() {
      await Promise.all([
        store.dispatch('enums/fetchPriorities'),
        store.dispatch('enums/fetchStatuses'),
        store.dispatch('enums/fetchTriggers'),
        store.dispatch('enums/fetchPrimaryDrivers'),
        store.dispatch('enums/fetchSecondaryDrivers'),
        store.dispatch('enums/fetchCostBenefitCategories'),
        store.dispatch('enums/fetchBenefitFrequencies'),
      ])
    },
  })
}
