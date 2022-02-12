<template>
  <loading-box
    class="page-very-wide"
    :url="apiUrl"
    :refresh="refresh"
    @data-loaded="counties = $event"
  >
    <p class="main-point">
      <template v-if="year">
        <span class="faded">I visited</span>
        {{ counties.length }} count{{ counties.length === 1 ? "y" : "ies" }}
        <span class="faded">in {{ year }}</span>
      </template>
      <template v-else>
        <span class="faded">I have visited</span>
        {{ counties.length }} count{{ counties.length === 1 ? "y" : "ies" }}
        <span class="faded">in my life</span>
      </template>
    </p>

    <!-- eslint-disable-next-line vue/require-v-for-key -->
    <p v-for="(yearGroup, index) in years" class="text-center">
      <span v-for="xYear in yearGroup" :key="xYear" class="spaced-inline">
        <strong v-if="xYear === year">{{ xYear }}</strong>
        <router-link
          v-else
          :to="{ name: 'travel-year', params: { year: xYear } }"
          >{{ xYear }}</router-link
        >
      </span>

      <template v-if="index === years.length - 1">
        <!-- eslint-disable vue/multiline-html-element-content-newline -->
        <router-link v-if="year" class="spaced-inline" :to="{ name: 'travel' }"
          >lifetime</router-link
        >
        <!-- eslint-enable vue/multiline-html-element-content-newline -->
        <strong v-else class="spaced-inline">lifetime</strong>
      </template>
    </p>

    <div class="align-center main-column">
      <object
        class="block mb-3"
        data="/static/blank-us-counties.svg"
        height="600px"
        type="image/svg+xml"
        @load="initializeMap"
      ></object>

      <div v-if="focusedCountyId" class="text-center">
        <h2>{{ formatCountyName(focusedCountyId) }}</h2>

        <div v-if="isEditable">
          <input v-model="form.date" type="date" />
          <select v-model="form.type">
            <option value="traveled through">traveled through</option>
            <option value="visited">visited</option>
            <option value="spent the night">spent the night</option>
          </select>
          <input
            type="submit"
            class="btn btn-primary"
            value="Create visit"
            @click="onSubmit"
          />
        </div>

        <div class="visits-container">
          <!-- eslint-disable-next-line vue/require-v-for-key -->
          <p v-for="visit in getVisits(focusedCountyId)">
            <template v-if="visit.yearOnly">
              {{ visit.date ? visit.date.slice(0, 4) : "unknown" }}
            </template>
            <template v-else>
              <template v-if="visit.date === visit.dateEnd">
                <date-link :date="visit.date" />
              </template>
              <template v-else>
                <date-link :date="visit.date" /> to
                <template v-if="visit.dateEnd">
                  <date-link :date="visit.dateEnd" />
                </template>
                <template v-else>present</template>
              </template>
            </template>

            <span class="visit-type">
              ({{ visit.type
              }}{{ visit.isIntermittent ? " - intermittent" : "" }})
            </span>
          </p>
        </div>
      </div>
    </div>
  </loading-box>
</template>

<script>
import * as lodash from "lodash";
import svgPanZoom from "svg-pan-zoom";

const TRAVELED_THROUGH = "traveled through";
const VISITED = "visited";
const SPENT_THE_NIGHT = "spent the night";
const RESIDED = "resided";
const SORTED_VISIT_TYPES = [
  TRAVELED_THROUGH,
  VISITED,
  SPENT_THE_NIGHT,
  RESIDED,
];

const FILL_TRAVELED_THROUGH = "#ff6600"; // orange
const FILL_VISITED = "#ffcc00"; // dark yellow
const FILL_SPENT_THE_NIGHT = "#00cc00"; // light green
const FILL_NONE = "#d0d0d0";

export default {
  props: {
    year: { type: Number, required: false, default: null },
  },

  data() {
    return {
      counties: [],
      focusedCountyId: null,
      form: {
        date: this.today().toISODate(),
        type: VISITED,
      },
      refresh: 0,
    };
  },

  computed: {
    apiUrl() {
      return this.year ? `/api/travel/list/${this.year}` : "/api/travel/list";
    },

    countiesMap() {
      const countiesMap = new Map();
      for (const county of this.counties) {
        countiesMap.set(getCountySvgName(county), county);
      }
      return countiesMap;
    },

    currentYear() {
      return this.today().year;
    },

    isEditable() {
      return !this.year || this.year === this.currentYear;
    },

    years() {
      const years = [[]];
      const baseYear = 2022;
      let index = 0;
      while (index + baseYear <= this.currentYear) {
        years[years.length - 1].push(index + baseYear);
        index++;
        if (index % 15 === 0) {
          years.push([]);
        }
      }
      return years;
    },
  },

  watch: {
    counties: function (newCounties, oldCounties) {
      this.redrawMap(oldCounties, newCounties);
    },
  },

  methods: {
    formatCountyName,

    getVisits(id) {
      const county = this.countiesMap.get(id);
      const visits = county ? county.visits : [];
      return lodash.orderBy(visits, [(visit) => visit.date || ""], ["desc"]);
    },

    initializeMap() {
      svgPanZoom("object", {
        controlIconsEnabled: true,
        zoomScaleSensitivity: 0.5,
        maxZoom: 100,
      });
      this.redrawMap([], this.counties);
    },

    redrawMap(oldCounties, newCounties) {
      const svgDom = document.querySelector("object");
      if (!svgDom) {
        return;
      }

      const svg = svgDom.getSVGDocument();
      if (!svg) {
        return;
      }

      // Clear all currently filled-in counties.
      for (const county of oldCounties) {
        const name = getCountySvgName(county);
        svg.getElementById(name).style.fill = FILL_NONE;
      }

      // Fill in the new counties.
      for (const county of newCounties) {
        let maxVisit = null;
        let maxVisitValue = -1;
        for (const visit of county.visits) {
          const value = SORTED_VISIT_TYPES.indexOf(visit.type);
          if (value > maxVisitValue) {
            maxVisit = visit.type;
            maxVisitValue = value;
          }
        }

        const name = getCountySvgName(county);
        if (maxVisit === TRAVELED_THROUGH) {
          svg.getElementById(name).style.fill = FILL_TRAVELED_THROUGH;
        } else if (maxVisit === VISITED) {
          svg.getElementById(name).style.fill = FILL_VISITED;
        } else if (maxVisit === SPENT_THE_NIGHT || maxVisit === RESIDED) {
          svg.getElementById(name).style.fill = FILL_SPENT_THE_NIGHT;
        }
      }

      svg.addEventListener("click", (event) => {
        if (this.focusedCountyId) {
          svg.getElementById(this.focusedCountyId).style.strokeWidth = "";
        }

        let controls = svg.getElementById("svg-pan-zoom-controls");
        if (controls.contains(event.target)) {
          return;
        }

        if (
          !event.target.id ||
          event.target.id === "_State_borders" ||
          event.target.id === "_separator"
        ) {
          // If the click is not on a county (and not on zoom controls), hide
          //the caption.
          this.focusedCountyId = null;
          return;
        }

        event.target.style.strokeWidth = "1";
        event.target.classList.add("focus");
        // If the click is on a county, display its information.
        this.focusedCountyId = event.target.id;
      });
    },

    onSubmit() {
      const date = this.form.date;
      const type = this.form.type;
      const payload = { county: this.focusedCountyId, date, type };
      this.$apiPost("/api/travel/create", payload).then(() => {
        this.refresh++;
      });
    },
  },
};

function getCountySvgName(county) {
  return county.county + "__" + county.state;
}

const SPECIAL = {
  // Census areas of Alaska
  Aleutians_West__AK: "Aleutians West Census Area",
  Bethel__AK: "Bethel Census Area",
  Dillingham__AK: "Dillingham Census Area",
  Hoonah_Angoon__AK: "Hoonah-Angoon Census Area",
  Kusilvak__AK: "Kusilvak Census Area",
  Nome__AK: "Nome Census Area",
  Prince_of_Wales_Hyder__AK: "Prince of Wales-Hyder Census Area",
  Southeast_Fairbanks__AK: "Southeast Fairbanks Census Area",
  "Valdez-Cordova__AK": "Valdez-Cordova Census Area",
  "Yukon-Koyukuk__AK": "Yukon-Koyukuk Census Area",
  // Consolidated city-counties and independent cities outside Virginia
  Anchorage__AK: "City of Anchorage",
  Baltimore_City__MD: "City of Baltimore",
  Carson_City__NV: "Carson City",
  San_Francisco__CA: "City and County of San Francisco",
  "St._Louis__MO": "City of St. Louis",
  Washington__DC: "Washington",
};
const VIRGINIA_CITIES = [
  "Alexandria",
  "Bristol",
  "Buena Vista",
  "Charlottesville",
  "Chesapeake",
  "Colonial Heights",
  "Covington",
  "Danville",
  "Emporia",
  "Fairfax",
  "Falls Church",
  "Franklin",
  "Fredericksburg",
  "Galax",
  "Hampton",
  "Harrisonburg",
  "Hopewell",
  "Lexington",
  "Lynchburg",
  "Manassas",
  "Manassas Park",
  "Martinsville",
  "Newport News",
  "Norfolk",
  "Norton",
  "Petersburg",
  "Poquoson",
  "Portsmouth",
  "Radford",
  "Richmond",
  "Roanoke",
  "Salem",
  "Staunton",
  "Suffolk",
  "Virginia Beach",
  "Waynesboro",
  "Williamsburg",
  "Winchester",
];
function formatCountyName(id) {
  let split = id.split("__");
  let name = split[0].replace(/_/g, " ");
  let state = split[1];
  if (SPECIAL[id]) {
    return SPECIAL[id] + ", " + state;
  } else if (state === "LA") {
    return name + " Parish, LA";
  } else if (state === "AK") {
    return name + " Borough, AK";
  } else if (state === "VA" && VIRGINIA_CITIES.includes(name)) {
    return name + ", VA";
  } else {
    if (name.endsWith("Co.")) {
      name = name.slice(0, name.length - 4);
    }
    return name + " County, " + state;
  }
}
</script>

<style scoped>
.faded {
  opacity: 50%;
}

.main-column {
  max-width: 1000px;
}

.visit-type {
  font-size: 0.8rem;
}

.visits-container {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  height: 200px;
  align-content: center;
  column-gap: 30px;
}

.visits-container p {
  text-align: left;
}
</style>
