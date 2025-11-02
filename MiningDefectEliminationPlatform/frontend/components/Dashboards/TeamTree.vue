<template>
  <div class="tree-root">
    <svg
      id="Layer_1"
      data-name="Layer 1"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1839 879"
    >
      <!-- CONNECTORS -->
      <g v-for="(con, ii) in connectors" :key="'conn_' + ii">
        <line
          :x1="con.x1"
          :y1="con.y1"
          :x2="con.x2"
          :y2="con.y2"
          class="connector"
        />
      </g>

      <!-- NODES -->
      <g
        v-for="(node, ii) in nodes"
        :key="'node_' + ii"
        :class="{ selectable: node.selectable }"
        class="node"
        @click="node.selectable ? clickItem(node) : null"
      >
        <rect
          :x="node.x"
          :y="node.y + 12"
          :fill="
            node.selectable
              ? 'var(--v-warning-darken1)'
              : 'var(--v-primary-base)'
          "
          width="218"
          height="50"
        />
        <text
          text-anchor="middle"
          :x="node.x + 218 / 2"
          :y="node.y + 75 / 2 + 7"
        >
          {{ node.text }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script>
export default {
  props: {
    update_db: { type: Boolean, required: false, default: false },
  },
  data() {
    return {
      connectors: [
        { x1: 109.5, y1: 37.5, x2: 109.5, y2: 800.5 },
        { x1: 109.5, y1: 161.5, x2: 384.5, y2: 161.5 },
        { x1: 109.5, y1: 290.5, x2: 240, y2: 290.5 },
        { x1: 239.5, y1: 246.5, x2: 239.5, y2: 331.5 },
        { x1: 384.5, y1: 246.5, x2: 239, y2: 246.5 },
        { x1: 384.5, y1: 331.5, x2: 239, y2: 331.5 },
        { x1: 109.5, y1: 545.5, x2: 384.5, y2: 545.5 },
        { x1: 109.5, y1: 800.5, x2: 242, y2: 800.5 },
        { x1: 241.5, y1: 756.5, x2: 241.5, y2: 841.5 },
        { x1: 386.5, y1: 756.5, x2: 241, y2: 756.5 },
        { x1: 386.5, y1: 841.5, x2: 241, y2: 841.5 },
        { x1: 109.5, y1: 416.5, x2: 384.5, y2: 416.5 },
        { x1: 109.5, y1: 671.5, x2: 384.5, y2: 671.5 },
        { x1: 605.5, y1: 229.5, x2: 756, y2: 229.5 },
        { x1: 755.5, y1: 145.5, x2: 755.5, y2: 315.5 },
        { x1: 915.5, y1: 145.5, x2: 755, y2: 145.5 },
        { x1: 919.5, y1: 315.5, x2: 755, y2: 315.5 },
        { x1: 755.5, y1: 229.5, x2: 915.5, y2: 229.5 },
        { x1: 605.5, y1: 485.5, x2: 756, y2: 485.5 },
        { x1: 755.5, y1: 401.5, x2: 755.5, y2: 571.5 },
        { x1: 915.5, y1: 401.5, x2: 755, y2: 401.5 },
        { x1: 915.5, y1: 571.5, x2: 755, y2: 571.5 },
        { x1: 755.5, y1: 485.5, x2: 915.5, y2: 485.5 },
        { x1: 605.5, y1: 740.5, x2: 757, y2: 740.5 },
        { x1: 756.5, y1: 656.5, x2: 756.5, y2: 826.5 },
        { x1: 919.5, y1: 656.5, x2: 756, y2: 656.5 },
        { x1: 919.5, y1: 826.5, x2: 756, y2: 826.5 },
        { x1: 756.5, y1: 740.5, x2: 919.5, y2: 740.5 },
        { x1: 1155.5, y1: 55, x2: 1155.5, y2: 574.5 },
        { x1: 1430.5, y1: 55, x2: 1430.5, y2: 489.5 },
        { x1: 1705.5, y1: 55, x2: 1705.5, y2: 486.5 },
        { x1: 1705.5, y1: 37.5, x2: 109, y2: 37.5 },
        { x1: 900, y1: 37.5, x2: 900, y2: 0 },
        { x1: 606, y1: 750, x2: 606, y2: 37.5 },
      ],
      nodes: [
        { x: 496.5, y: 0.5, text: "HME", selectable: false },
        { x: 1046.5, y: 0.5, text: "Energy Operations", selectable: false },
        { x: 1321.5, y: 0.5, text: "Dewatering", selectable: false },
        { x: 1596.5, y: 0.5, text: "Rail", selectable: false },
        { x: 130.5, y: 0.5, text: "Fixed Plant", selectable: false },
        { x: 0.5, y: 123.5, text: "Iron Bridge", selectable: false },
        { x: 0.5, y: 253.5, text: "Solomon", selectable: false },
        { x: 0.5, y: 378.5, text: "Cloudbreak", selectable: false },
        { x: 275.5, y: 123.5, text: "IB OPF", id: 31, selectable: true },
        { x: 275.5, y: 208.5, text: "FT OPF", id: 32, selectable: true },
        { x: 275.5, y: 293.5, text: "KV OPF", id: 33, selectable: true },
        { x: 275.5, y: 378.5, text: "CB OPF", id: 34, selectable: true },
        { x: 0.5, y: 508.5, text: "Christmas Creek", selectable: false },
        { x: 275.5, y: 508.5, text: "CC OPF", id: 35, selectable: true },
        { x: 0.5, y: 633.5, text: "Eliwana", selectable: false },
        { x: 275.5, y: 633.5, text: "EW OPF1", id: 37, selectable: true },
        { x: 2.5, y: 763.5, text: "Anderson Point", selectable: false },
        { x: 277.5, y: 718.5, text: "AP Inloading", id: 38, selectable: true },
        { x: 277.5, y: 803.5, text: "AP Outloading", id: 39, selectable: true },
        { x: 806.5, y: 107.5, text: "Haul Truck", id: 40, selectable: true },
        {
          x: 806.5,
          y: 192.5,
          text: "Diggers & Drills",
          id: 41,
          selectable: true,
        },
        { x: 806.5, y: 277.5, text: "Ancillary", id: 42, selectable: true },
        { x: 516.5, y: 192.5, text: "Christmas Creek", selectable: false },
        { x: 806.5, y: 362.5, text: "Haul Truck", id: 43, selectable: true },
        {
          x: 806.5,
          y: 447.5,
          text: "Diggers & Drills",
          id: 44,
          selectable: true,
        },
        { x: 806.5, y: 532.5, text: "Ancillary", id: 45, selectable: true },
        { x: 516.5, y: 447.5, text: "Solomon", selectable: false },
        { x: 807.5, y: 617.5, text: "Haul Truck", id: 46, selectable: true },
        {
          x: 807.5,
          y: 702.5,
          text: "Diggers & Drills",
          id: 47,
          selectable: true,
        },
        { x: 807.5, y: 787.5, text: "Ancillary", id: 48, selectable: true },
        { x: 517.5, y: 702.5, text: "Cloudbreak", selectable: false },
        { x: 1096.5, y: 111.5, text: "Iron Bridge", id: 15, selectable: true },
        { x: 1096.5, y: 196.5, text: "Solomon", id: 16, selectable: true },
        { x: 1096.5, y: 281.5, text: "Cloudbreak", id: 17, selectable: true },
        {
          x: 1096.5,
          y: 366.5,
          text: "Christmas Creek",
          id: 18,
          selectable: true,
        },
        { x: 1096.5, y: 451.5, text: "Eliwana", id: 19, selectable: true },
        {
          x: 1096.5,
          y: 536.5,
          text: "Anderson Point",
          id: 20,
          selectable: true,
        },
        { x: 1353.5, y: 111.5, text: "Iron Bridge", id: 21, selectable: true },
        { x: 1353.5, y: 196.5, text: "Solomon", id: 22, selectable: true },
        { x: 1353.5, y: 281.5, text: "Chichester", id: 23, selectable: true },
        { x: 1353.5, y: 366.5, text: "Eliwana", id: 24, selectable: true },
        {
          x: 1353.5,
          y: 451.5,
          text: "Anderson Point",
          id: 25,
          selectable: true,
        },
        { x: 1620.5, y: 107.5, text: "Ore Car", id: 26, selectable: true },
        { x: 1620.5, y: 192.5, text: "Signalling", id: 27, selectable: true },
        { x: 1620.5, y: 277.5, text: "Locomotives", id: 28, selectable: true },
        { x: 1620.5, y: 362.5, text: "Track", id: 29, selectable: true },
        {
          x: 1620.5,
          y: 447.5,
          text: "Track Machine",
          id: 30,
          selectable: true,
        },
      ],
    };
  },
  methods: {
    clickItem(node) {
      this.$nuxt.$emit("change_team", node, this.update_db);

      if (this.update_db) {
        this.$axios
          .$patch("/user/change_team", null, {
            params: { team_id: node.id, team_name: node.text },
          })
          .then(() => {})
          .catch((err) => console.error(err));
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.tree-root {
  margin: auto;

  .theme--light & {
    --line-color: var(--v-accent-base);
  }
  .theme--dark & {
    --line-color: white;
  }
}

.node {
  rect {
    stroke-width: 3;
    rx: 5px;
  }

  text {
    font-size: 18px;
    font-weight: bold;
    text-transform: uppercase;
    fill: white;
  }
  &.selectable {
    cursor: pointer;
    rect {
    }

    &:hover rect {
      filter: brightness(105%);
    }
  }
}

.connector {
  fill: none;
  stroke: var(--line-color);
  stroke-miterlimit: 10;
  stroke-width: 4px;
}
</style>
