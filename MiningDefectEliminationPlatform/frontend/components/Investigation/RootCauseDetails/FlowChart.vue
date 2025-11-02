<template>
  <div class="chart-root">
    <div class="button">
      <v-btn
        :disabled="(!is_my_investigation || loading) && !$perms.is_admin"
        v-bind="$bind.btn"
        @click="resetState"
      >
        Reset
      </v-btn>
    </div>
    <svg
      ref="flowchart"
      id="flow-chart"
      data-name="Layer 1"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 2202.22 857.74"
    >
      <def>
        <!-- STYLE FOR DOWNLOAD ONLY -->
        <style>
          .chart-root {
            padding: 10px;
          }
          .button {
            position: relative;
            float: right;
            right: 0px;
            top: 50px;
            transition: 0.5s;
            margin-top: -50px;
          }
          .text {
            font-size: 18pt;
            text-align: center;
            cursor: pointer;
          }
          line,
          polygon {
            fill: black !important;
            color: black !important;
          }
          .disable {
            opacity: 0.2;
          }
          .active {
            opacity: 1;
          }
          .active rect {
            stroke: #355bb7 !important;
          }
          .option {
            opacity: 1 !important;
          }
          .option rect {
            stroke: black !important;
          }
          .option line,
          .option polygon,
          .option text {
            opacity: 0.2;
          }
          .option .box-title {
            fill: black;
            opacity: 1;
          }
          .option .yes,
          .option .no {
            opacity: 1;
          }
          .option:hover rect {
            fill: #355bb7 !important;
            opacity: 0.5;
          }
          .selected {
            opacity: 1;
          }
          .selected rect {
            stroke: #355bb7 !important;
          }
          .selected .text {
            color: #355bb7;
          }
          .activeArrow line {
            stroke: #355bb7 !important;
            opacity: 1 !important;
          }
          .activeArrow polygon {
            fill: #355bb7 !important;
            opacity: 1 !important;
          }
          .activeArrow text {
            fill: #355bb7;
            opacity: 1 !important;
          }
          .activeArrow p,
          .activeArrow span {
            color: #355bb7;
          }
          .cls-1 {
            fill: none;
            stroke: black;
            stroke-miterlimit: 10;
            stroke-width: 2px;
            cursor: pointer;
            pointer-events: all;
          }
          .cls-2 {
            fill: #ffc107 !important;
          }
          .cls-2-1 {
            fill: black;
          }
          .cls-3,
          .cls-45 {
            font-size: 24px;
          }
        </style>
      </def>
      <title>flowchart</title>

      <!------------------- STAR TEXTBOX ------------------>
      <!-- DOWN ARROW -->
      <g class="activeArrow">
        <line class="cls-1" x1="147.61" y1="195" x2="147.61" y2="331.36" />
        <polygon
          points="147.61 338.13 153.61 325.36 141.61 325.36 147.61 338.13"
        />
      </g>
      <polygon
        class="cls-2"
        points="116.94 174.61 54.75 203.43 91.18 166.95 11.12 165.39 82.74 125.28 4.53 115.23 79.17 90.83 33.26 65.77 102.3 66.2 90.99 25.31 151.06 48.41 168.95 2.61 196.65 40.15 249.96 2.08 245.32 51.66 317.84 24.22 280.02 76.37 356.22 64.58 300.87 89.72 366.5 112.74 285.01 124.47 337.48 162.47 248.05 149.11 278.5 202.46 213.48 165.31 201.57 225.29 172.97 171.24 120.37 226.47 116.94 174.61"
      />
      <path
        class="cls-2-1"
        d="M242.54,4.43l-4.29,45.8-.3,3.19,3-1.14,67.9-25.69L274.39,74.1,271.58,78l4.74-.73L343,66.94,296.5,88,292,90.1l4.7,1.65,59.42,20.84-75,10.79-4.89.7,4,2.9,47.15,34.15L244,148.68l-4.08-.6,2,3.57L269.6,200,209,165.38,206.55,164l-.54,2.72-11.09,55.86-26.64-50.34L167,169.8l-1.91,2L115,224.38l-3.18-48.12-.19-2.91L109,174.58,53.21,200.42,84,169.58l3.32-3.32-4.69-.1-74-1.44,65.76-36.83,5.28-3-6-.77-70.81-9.1,68.23-22.3,4.4-1.44L71.4,89.1,31,67.05l63.75.39,2.65,0-.71-2.55L86.26,27.21l57.29,22,1.85.71.73-1.85L163,4.92l26,35.29,1.17,1.58,1.6-1.14L242.54,4.43m2.4-4.17L190.65,39,162.46.82,144.27,47.37l-61-23.45L94.76,65.44,23.07,65,70.44,90.86l-76.66,25,79.61,10.23L1.19,166.58l81.4,1.58L43.85,207l66-30.57,3.48,52.67,53.21-55.87,29.27,55.31L208,167.12l67,38.28-31.26-54.74,91.46,13.66-53.8-39,83.09-12L297.33,89.86l59.72-27.12L276,75.28l38.38-52.92L240.24,50.41,244.94.26Z"
        transform="translate(6.22 -0.26)"
      />
      <foreignObject
        class="text"
        transform="translate(80 80)"
        width="220"
        height="200"
      >
        <p>Failure of equipment or process occurs</p>
      </foreignObject>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX ONE ------------------>
      <g
        :class="{
          disable: isDisabled[0],
          active: isActive[0],
          option: isOption[0],
          selected: isSelected[0],
        }"
      >
        <!-- YES-ARROW -->
        <g
          :class="
            isSelected[0] ? 'activeArrow' : isOption[1] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 yes"
            x1="288.22"
            y1="426.74"
            x2="380.22"
            y2="426.74"
          />
          <polygon
            class="yes"
            points="387 426.74 374.22 420.74 374.22 432.74 387 426.74"
          />
          <foreignObject
            class="cls-3 yes"
            transform="translate(311 395)"
            width="50"
            height="50"
          >
            <p>Yes</p>
          </foreignObject>
        </g>

        <!-- NO-ARROW -->
        <g
          :class="
            isSelected[6] ? 'activeArrow' : isOption[6] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 no"
            x1="148.22"
            y1="511.74"
            x2="148.61"
            y2="578.36"
          />
          <polygon
            class="no"
            points="148.61 585.13 154.61 572.36 142.61 572.36 148.61 585.13"
          />
          <foreignObject
            class="cls-3 no"
            transform="translate(158.04 525)"
            width="50"
            height="50"
          >
            <p>No</p>
          </foreignObject>
        </g>
        <rect
          class="cls-1"
          x="6.22"
          y="339.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(25 390)"
          width="250"
          height="200"
        >
          <p>Is this Failure Mode (FM) known?</p>
        </foreignObject>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX TWO ------------------>
      <g
        :class="{
          disable: isDisabled[1],
          active: isActive[1],
          option: isOption[1],
          selected: isSelected[1],
        }"
        @click="clickBoxTwo()"
      >
        <!-- YES-ARROW -->
        <g
          :class="
            isSelected[2] ? 'activeArrow' : isOption[2] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 yes"
            x1="671.22"
            y1="426.74"
            x2="763.22"
            y2="426.74"
          />
          <polygon
            class="yes"
            points="770 426.74 757.22 420.74 757.22 432.74 770 426.74"
          />
          <foreignObject
            class="cls-3 yes"
            transform="translate(695 395)"
            width="50"
            height="50"
          >
            <p>Yes</p>
          </foreignObject>
        </g>

        <!-- NO-ARROW -->
        <g
          :class="
            isSelected[7] ? 'activeArrow' : isOption[7] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 no"
            x1="535.22"
            y1="512.74"
            x2="535.61"
            y2="579.36"
          />
          <polygon
            class="no"
            points="535.61 586.13 541.61 573.36 529.61 573.36 535.61 586.13"
          />
          <foreignObject
            class="cls-3 no"
            transform="translate(545 525)"
            width="50"
            height="50"
          >
            <p>No</p>
          </foreignObject>
        </g>
        <rect
          class="cls-1"
          x="388.22"
          y="340.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(405 375)"
          width="250"
          height="200"
        >
          <p>Is the failure mode identified in the FMEA for the equipment?</p>
        </foreignObject>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX THREE ------------------>
      <g
        :class="{
          disable: isDisabled[2],
          active: isActive[2],
          option: isOption[2],
          selected: isSelected[2],
        }"
        @click="clickBoxThree()"
      >
        <!-- YES-ARROW -->
        <g
          :class="
            isSelected[3] ? 'activeArrow' : isOption[3] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 yes"
            x1="1054.22"
            y1="426.74"
            x2="1146.22"
            y2="426.74"
          />
          <polygon
            class="yes"
            points="1152.99 426.74 1140.22 420.74 1140.22 432.74 1152.99 426.74"
          />
          <foreignObject
            class="cls-3 yes"
            transform="translate(1079 395)"
            width="50"
            height="50"
          >
            <p>Yes</p>
          </foreignObject>
        </g>

        <!-- NO-ARROW -->
        <g
          :class="
            isSelected[8] ? 'activeArrow' : isOption[8] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 no"
            x1="912.22"
            y1="512.74"
            x2="912.61"
            y2="579.36"
          />
          <polygon
            class="no"
            points="912.61 586.13 918.61 573.36 906.61 573.36 912.61 586.13"
          />
          <foreignObject
            class="cls-3 no"
            transform="translate(922 525)"
            width="50"
            height="50"
          >
            <p>No</p>
          </foreignObject>
        </g>
        <rect
          class="cls-1"
          x="771.22"
          y="340.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(790 360)"
          width="250"
          height="200"
        >
          <p>
            Is there a PM task or strategy in place to manage this failure mode?
          </p>
        </foreignObject>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX FOUR ------------------>
      <g
        :class="{
          disable: isDisabled[3],
          active: isActive[3],
          option: isOption[3],
          selected: isSelected[3],
        }"
        @click="clickBoxFour()"
      >
        <!-- YES-ARROW -->
        <g
          :class="
            isSelected[4] ? 'activeArrow' : isOption[4] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 yes"
            x1="1436.22"
            y1="427.74"
            x2="1528.22"
            y2="427.74"
          />
          <polygon
            class="yes"
            points="1534.99 427.74 1522.22 421.74 1522.22 433.74 1534.99 427.74"
          />
          <foreignObject
            class="cls-3 yes"
            transform="translate(1461 395)"
            width="50"
            height="50"
          >
            <p>Yes</p>
          </foreignObject>
        </g>
        <!-- NO-ARROW -->
        <g
          :class="
            isSelected[9] ? 'activeArrow' : isOption[9] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 no"
            x1="1299.22"
            y1="512.74"
            x2="1299.22"
            y2="579.74"
          />
          <polygon
            class="no"
            points="1299.61 586.13 1305.61 573.36 1293.61 573.36 1299.61 586.13"
          />
          <foreignObject
            class="cls-3 no"
            transform="translate(1309 525)"
            width="50"
            height="50"
          >
            <p>No</p>
          </foreignObject>
        </g>
        <rect
          class="cls-1"
          x="1154.22"
          y="340.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(1170 395)"
          width="250"
          height="200"
        >
          <p>Has the PM task been executed adequately?</p>
        </foreignObject>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX FIVE ------------------>
      <g
        :class="{
          disable: isDisabled[4],
          active: isActive[4],
          option: isOption[4],
          selected: isSelected[4],
        }"
        @click="clickBoxFive()"
      >
        <!-- YES-ARROW -->
        <g
          :class="
            isSelected[5] ? 'activeArrow' : isOption[5] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 yes"
            x1="1819.22"
            y1="427.74"
            x2="1911.22"
            y2="427.74"
          />
          <polygon
            class="yes"
            points="1917.99 427.74 1905.22 421.74 1905.22 433.74 1917.99 427.74"
          />
          <foreignObject
            class="cls-3 yes"
            transform="translate(1844 395)"
            width="50"
            height="50"
          >
            <p>Yes</p>
          </foreignObject>
        </g>
        <!-- NO-ARROW -->
        <g
          :class="
            isSelected[10] ? 'activeArrow' : isOption[10] ? 'option' : 'disable'
          "
        >
          <line
            class="cls-1 no"
            x1="1678.61"
            y1="512.74"
            x2="1678.61"
            y2="579.74"
          />
          <polygon
            class="no"
            points="1678.61 570.51 1684.61 557.74 1672.61 557.74 1678.61 570.51"
            transform="translate(0 15)"
          />
          <foreignObject
            class="cls-3 no"
            transform="translate(1686 525)"
            width="50"
            height="50"
          >
            <p>No</p>
          </foreignObject>
        </g>
        <rect
          class="cls-1"
          x="1536.22"
          y="341.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(1550 380)"
          width="260"
          height="200"
        >
          <p>
            Is the failed component being operated within the design limits?
          </p>
        </foreignObject>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX SIX ------------------>
      <g
        :class="{
          disable: isDisabled[5],
          active: isActive[5],
          option: isOption[5],
          selected: isSelected[5],
        }"
        @click="clickBoxSix()"
      >
        <!-- LOOP BACK LINE -->
        <g :class="{ activeArrow: isSelected[5] }">
          <line
            class="cls-1"
            x1="2063.22"
            y1="303.74"
            x2="147.22"
            y2="303.74"
          />
          <line
            class="cls-1"
            x1="2063.22"
            y1="341.74"
            x2="2063.22"
            y2="302.74"
          />
        </g>
        <rect
          class="cls-1"
          x="1919.22"
          y="341.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(1930 355)"
          width="255"
          height="200"
        >
          <span>Failure should not occur if all of these steps are taken.</span>
          <p>(Re-evaluation required)</p>
        </foreignObject>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX SEVEN ------------------>
      <g
        :class="{
          disable: isDisabled[6],
          active: isActive[6],
          option: isOption[6],
          selected: isSelected[6],
        }"
        @click="clickBoxSeven()"
      >
        <rect
          class="cls-1"
          x="7.22"
          y="585.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(20 600)"
          width="255"
          height="200"
        >
          <p>
            Conduct a Forensic Failure Analysis or Formal RCA to identify
            failure mode
          </p>
        </foreignObject>
        <!-- LOOP BACK ARROW -->
        <g :class="{ activeArrow: isSelected[6] }">
          <line class="cls-1" x1="289.22" y1="671.74" x2="334.22" y2="671.74" />
          <line class="cls-1" x1="334.22" y1="672.74" x2="334.22" y2="426.74" />

          <!-- TEXT -->
          <foreignObject
            class="cls-45 box-title"
            transform="translate(126.1 770)"
            width="100"
            height="50"
          >
            <p>RCA</p>
          </foreignObject>
        </g>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX EIGHT ------------------>
      <g
        :class="{
          disable: isDisabled[7],
          active: isActive[7],
          option: isOption[7],
          selected: isSelected[7],
        }"
        @click="clickBoxEight()"
      >
        <rect
          class="cls-1"
          x="378.22"
          y="586.74"
          width="330"
          height="200"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(395 600)"
          width="300"
          height="200"
        >
          <p>
            Update the FMEA for this equipment to include new FM. Ensure tasks
            or strategies are in place to prevent recurrence.
          </p>
        </foreignObject>

        <!-- TEXT -->
        <g
          :class="{
            activeArrow: isSelected[7],
          }"
        >
          <line class="cls-1" x1="529.22" y1="787" x2="529.22" y2="808.74" />
          <line
            class="cls-1"
            x1="529.22"
            y1="807.74"
            x2="1691.22"
            y2="808.75"
          />
          <foreignObject
            class="cls-3 box-title"
            transform="translate(501.42 820)"
            width="100"
            height="50"
          >
            <p>FMEA</p>
          </foreignObject>
        </g>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX NINE ------------------>
      <g
        :class="{
          disable: isDisabled[8],
          active: isActive[8],
          option: isOption[8],
          selected: isSelected[8],
        }"
        @click="clickBoxNine()"
      >
        <rect
          class="cls-1"
          x="772.22"
          y="586.74"
          width="320"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(780 600)"
          width="300"
          height="200"
        >
          <p>
            Develop or update the PM task or strategy to prevent recurrence.
            Update PM in SAP, PRT's, ITP's etc.
          </p>
        </foreignObject>

        <!-- TEXT -->
        <g
          :class="{
            activeArrow: isSelected[8],
          }"
        >
          <line class="cls-1" x1="913.22" y1="759.74" x2="913.22" y2="807.74" />
          <line
            v-if="isSelected[8]"
            class="cls-1"
            x1="912.22"
            y1="807.74"
            x2="1691.22"
            y2="808.75"
          />
          <foreignObject
            class="cls-3 box-title"
            transform="translate(861 820)"
            width="150"
            height="50"
          >
            <p>STRATEGY</p>
          </foreignObject>
        </g>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX TEN ------------------>
      <g
        :class="{
          disable: isDisabled[9],
          active: isActive[9],
          option: isOption[9],
          selected: isSelected[9],
        }"
        @click="clickBoxTen()"
      >
        <rect
          class="cls-1"
          x="1155.22"
          y="586.74"
          width="330"
          height="200"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(1170 600)"
          width="300"
          height="200"
        >
          <p>
            Investigate reasons for poor execution. Improvements may include
            training, tooling, improved work instructions etc.
          </p>
        </foreignObject>

        <!-- TEXT -->
        <g
          :class="{
            activeArrow: isSelected[9],
          }"
        >
          <line class="cls-1" x1="1296.22" y1="787" x2="1296.22" y2="807.74" />
          <line
            v-if="isSelected[9]"
            class="cls-1"
            x1="1295.22"
            y1="807.74"
            x2="1691.22"
            y2="808.75"
          />
          <foreignObject
            class="cls-3 box-title"
            transform="translate(1237 820)"
            width="150"
            height="50"
          >
            <p>EXECUTION</p>
          </foreignObject>
        </g>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX ELEVEN ------------------>
      <g
        :class="{
          disable: isDisabled[10],
          active: isActive[10],
          option: isOption[10],
          selected: isSelected[10],
        }"
        @click="clickBoxEleven()"
      >
        <rect
          class="cls-1"
          x="1537.22"
          y="586.74"
          width="350"
          height="200"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(1550 600)"
          width="320"
          height="200"
        >
          <p>
            Change operational practice or upgrade component to suit operational
            requirements. Ensure change management is completed.
          </p>
        </foreignObject>

        <!-- TEXT -->
        <g
          :class="{
            activeArrow: isSelected[10],
          }"
        >
          <line class="cls-1" x1="1692.22" y1="787" x2="1692.22" y2="807.74" />
          <foreignObject
            class="cls-3 box-title"
            transform="translate(1623 820)"
            width="170"
            height="50"
          >
            <p>ENGINEERING</p>
          </foreignObject>
        </g>
      </g>
      <!------------------- END ------------------>

      <!--------------- TEXTBOX TWELVE ------------------>
      <g
        :class="{
          disable: isDisabled[11],
          active: isActive[11],
          option: isOption[11],
          selected: isSelected[11],
        }"
      >
        <rect
          class="cls-1"
          x="1919.22"
          y="588.74"
          width="282"
          height="172"
          rx="25.61"
        />
        <foreignObject
          class="text"
          transform="translate(1932 610)"
          width="260"
          height="200"
        >
          <p>Extrapolate to common equipment, communicate and share learning</p>
        </foreignObject>

        <!-- TEXT -->
        <g
          :class="{
            activeArrow: isSelected[11],
          }"
        >
          <line
            class="cls-1"
            x1="1691.22"
            y1="808.74"
            x2="2068.22"
            y2="808.74"
          />
          <line class="cls-1" x1="2068" y1="809.74" x2="2068" y2="768.13" />
          <polygon
            points="2067.61 761.74 2061.61 774.51 2073.61 774.51 2067.61 761.74"
          />
          <foreignObject
            class="cls-3 box-title"
            transform="translate(1966 820)"
            width="250"
            height="50"
          >
            <p>SHARED LEARNINGS</p>
          </foreignObject>
        </g>
      </g>
      <!------------------- END ------------------>
    </svg>
  </div>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: {
    investigation: { Object },
    loading: { type: Boolean, default: false },
  },
  data() {
    return {
      hideDownload: true,
      isSelected: new Array(12).fill(false),
      isActive: new Array(12).fill(false).map((_, i) => {
        return i == 0;
      }),
      isDisabled: new Array(12).fill(false).map((_, i) => {
        return i != 0;
      }),
      isOption: new Array(12).fill(false).map((_, i) => {
        return i == 1 || i == 6;
      }),
    };
  },
  computed: {
    ...mapGetters({
      is_my_investigation: "user/getIsMyInvestigation",
    }),
  },
  mounted() {
    // Auto Fill Existing Flow-Chart (If exists)
    switch (this.investigation.root_cause_detail.cause_category) {
      case "FMEA":
        this.autoFMEA();
        break;
      case "STRATEGY":
        this.autoSTRATEGY();
        break;
      case "EXECUTION":
        this.autoEXECUTION();
        break;
      case "ENGINEERING":
        this.autoENGINEERING();
        break;
      default:
        this.resetState();
    }
  },
  methods: {
    resetState() {
      this.isSelected = new Array(12).fill(false).map((_, i) => {
        return i == 0;
      });
      this.isActive = new Array(12).fill(false).map((_, i) => {
        return i == 0;
      });
      this.isDisabled = new Array(12).fill(false).map((_, i) => {
        return i != 0;
      });
      this.isOption = new Array(12).fill(false).map((_, i) => {
        return i == 1 || i == 6;
      });
      this.hideDownload = true;
    },
    clearSelected() {
      this.isSelected = new Array(12).fill(false);
    },
    clearActives() {
      this.isActive = new Array(12).fill(false);
    },
    clearDisabled() {
      this.isDisabled = new Array(12).fill(true);
    },
    clearOptions() {
      this.isOption = new Array(12).fill(false);
    },
    clickBoxTwo() {
      if (this.isOption[1]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[0] = true;
        this.isSelected[1] = true;

        this.isActive[1] = true;

        this.isOption[2] = true;
        // this.isOption[7] = true;

        this.clickBoxThree();
      }
    },
    clickBoxThree() {
      if (this.isOption[2]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[2] = true;

        this.isActive[2] = true;

        this.isOption[3] = true;
        this.isOption[8] = true;
      }
    },
    clickBoxFour() {
      if (this.isOption[3]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[3] = true;

        this.isActive[3] = true;

        this.isOption[4] = true;
        this.isOption[9] = true;
      }
    },
    clickBoxFive() {
      if (this.isOption[4]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[4] = true;

        this.isActive[4] = true;

        this.isOption[5] = true;
        this.isOption[10] = true;
      }
    },
    clickBoxSix() {
      if (this.isOption[5]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[5] = true;

        this.isActive[5] = true;

        this.warningMessage(
          "Failure should not occur if all these steps are taken. Please re-evaluate."
        );
        this.resetState();
      }
    },
    clickBoxSeven() {
      if (this.isOption[6]) {
        // this.clearActives();
        // this.clearDisabled();
        // this.clearOptions();

        this.clickBoxTwo();
        this.clickBoxThree();

        this.isSelected[0] = true;
        this.isSelected[1] = true;
        this.isSelected[6] = true;

        // this.isActive[1] = true;
        // this.isActive[2] = true;

        // this.isOption[2] = true;
        // this.isOption[8] = true;
        // this.isOption[7] = true;
      }
    },
    // FMEA
    clickBoxEight() {
      if (this.isOption[7]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[7] = true;
        this.isSelected[11] = true;

        this.investigation.root_cause_detail.cause_category = "FMEA";
        this.successMessage("Root Cause is FMEA");
      }
    },
    // STRATEGY
    clickBoxNine() {
      if (this.isOption[8]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[8] = true;
        this.isSelected[11] = true;

        this.investigation.root_cause_detail.cause_category = "STRATEGY";
        this.successMessage("Root Cause is STRATEGY");
      }
    },
    // EXECUTION
    clickBoxTen() {
      if (this.isOption[9]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[9] = true;
        this.isSelected[11] = true;

        this.investigation.root_cause_detail.cause_category = "EXECUTION";
        this.successMessage("Root Cause is EXECUTION");
      }
    },
    // ENGINEERING
    clickBoxEleven() {
      if (this.isOption[10]) {
        this.clearActives();
        this.clearDisabled();
        this.clearOptions();

        this.isSelected[10] = true;
        this.isSelected[11] = true;

        this.investigation.root_cause_detail.cause_category = "ENGINEERING";
        this.successMessage("Root Cause is ENGINEERING");
      }
    },
    // ----------------------
    // AUTO COMPLETE
    // ----------------------
    autoFMEA() {
      this.clearActives();
      this.clearDisabled();
      this.clearOptions();

      this.isSelected[0] = true;
      this.isSelected[1] = true;
      this.isSelected[7] = true;
      this.isSelected[11] = true;
    },
    autoSTRATEGY() {
      this.clearActives();
      this.clearDisabled();
      this.clearOptions();

      this.isSelected[0] = true;
      this.isSelected[1] = true;
      this.isSelected[2] = true;
      this.isSelected[8] = true;
      this.isSelected[11] = true;
    },
    autoEXECUTION() {
      this.clearActives();
      this.clearDisabled();
      this.clearOptions();

      this.isSelected[0] = true;
      this.isSelected[1] = true;
      this.isSelected[2] = true;
      this.isSelected[3] = true;
      this.isSelected[9] = true;
      this.isSelected[11] = true;
    },
    autoENGINEERING() {
      this.clearActives();
      this.clearDisabled();
      this.clearOptions();

      this.isSelected[0] = true;
      this.isSelected[1] = true;
      this.isSelected[2] = true;
      this.isSelected[3] = true;
      this.isSelected[4] = true;
      this.isSelected[10] = true;
      this.isSelected[11] = true;
    },
    successMessage(message) {
      this.$snackbar.add(message, "success");
    },
    warningMessage(message) {
      this.$snackbar.add(message, "warning");
    },
  },
};
</script>

<style lang="scss" scoped>
// MY STYLING
.chart-root {
  padding: 10px;
}

.button {
  position: relative;
  float: right;
  right: 0px;
  top: 50px;
  transition: 0.5s;
  margin-top: -50px;
}

.text {
  font-size: 18pt;
  text-align: center;
  cursor: pointer;
}

line,
polygon {
  fill: var(--v-words-base) !important;
  color: var(--v-words-base) !important;
}

.disable {
  opacity: 0.2;
}

.active {
  opacity: 1;
  rect {
    stroke: var(--v-primary-base) !important;
  }
}

.option {
  opacity: 1 !important;
  rect {
    stroke: var(--v-words-base) !important;
  }
  line,
  polygon,
  text {
    opacity: 0.2;
  }
  .box-title {
    fill: var(--v-words-base);
    opacity: 1;
  }

  .yes,
  .no {
    opacity: 1;
  }

  &:hover rect {
    fill: var(--v-primary-base) !important;
    opacity: 0.5;
  }
}

.selected {
  opacity: 1;
  rect {
    stroke: var(--v-primary-base) !important;
  }

  .text {
    color: var(--v-primary-base);
  }
}

.activeArrow {
  line {
    stroke: var(--v-primary-base) !important;
    opacity: 1 !important;
  }

  polygon {
    fill: var(--v-primary-base) !important;
    opacity: 1 !important;
  }

  text {
    fill: var(--v-primary-base);
    opacity: 1 !important;
  }

  p,
  span {
    color: var(--v-primary-base);
  }
}

// GENERATED SVG STYLING
.cls-1 {
  fill: none;
  stroke: var(--v-words-base);
  stroke-miterlimit: 10;
  stroke-width: 2px;

  cursor: pointer;
  pointer-events: all;
}
.cls-2 {
  fill: var(--v-warning-base) !important;
}
.cls-2-1 {
  fill: var(--v-words-base);
}
.cls-3,
.cls-45 {
  font-size: 24px;
}
</style>
