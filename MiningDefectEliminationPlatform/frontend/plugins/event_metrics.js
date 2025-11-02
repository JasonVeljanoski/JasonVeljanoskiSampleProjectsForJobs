export default ({ app }, inject) => {
  inject("event_metrics", {
    totalAplusLostTonnes(event_details, format = false) {
      if (event_details == null) {
        if (format) return 0.0 + " tonnes";
        return null;
      }

      const selected_event_ids = event_details.map((x) => x.id);

      let agg_lost_tons = 0;
      for (const item of event_details) {
        if (selected_event_ids.includes(item.id)) {
          if (item.tonnes_lost) agg_lost_tons += item.tonnes_lost;
        }
      }
      if (format) return agg_lost_tons.toFixed(2) + " tonnes";
      else return agg_lost_tons;
    },
    totalAplusEffectiveDuration(event_details, format = false) {
      if (event_details == null) {
        if (format) return 0.0 + " hrs";
        return null;
      }

      const selected_event_ids = event_details.map((x) => x.id);

      let agg_effective_duration = 0;
      for (const item of event_details) {
        if (selected_event_ids.includes(item.id)) {
          if (item.effective_duration)
            agg_effective_duration += item.effective_duration;
        }
      }
      if (format) return agg_effective_duration.toFixed(2) + " hrs";
      else return agg_effective_duration;
    },
    totalAplusEventDuration(event_details, format = false, autoItem = null) {
      if (event_details == null) {
        if (format) return 0.0 + " hrs";
        return null;
      }

      const selected_event_ids = event_details.map((x) => x.id);

      let agg_event_duration = 0;
      if (autoItem != null)
        agg_event_duration += parseFloat(autoItem.effective_duration);
      for (const item of event_details) {
        if (selected_event_ids.includes(item.id)) {
          if (item.start_time && item.end_time) {
            var t1 = new Date(item.start_time);
            var t2 = new Date(item.end_time);
            agg_event_duration += Math.abs(t2.getTime() - t1.getTime()) / 36e5;
          }
        }
      }
      if (format) return agg_event_duration.toFixed(2) + " hrs";
      else return agg_event_duration;
    },
    totalRemsEventDuration(event_details, format = false) {
      if (event_details == null) {
        if (format) return 0.0 + " hrs";
        return null;
      }

      const selected_event_ids = event_details.map((x) => x.id);

      let agg_event_duration = 0;
      for (const item of event_details) {
        if (selected_event_ids.includes(item.id)) {
          agg_event_duration += item.event_duration;
        }
      }
      if (format) return agg_event_duration.toFixed(2) + " hrs";
      else return agg_event_duration;
    },
  });
};
