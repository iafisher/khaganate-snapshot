<template>
  <loading-box
    class="page-wide"
    :url="'/api/metrics/get/' + metricName"
    @data-loaded="metric = $event"
  >
    <template v-if="metric !== null">
      <h1>Metric: {{ metric.displayTitle }}</h1>
      <p>
        This metric was first collected in {{ start }} and
        <!-- eslint-disable vue/multiline-html-element-content-newline -->
        <template v-if="end !== null">was deprecated in {{ end }}</template
        ><template v-else>is currently active</template>.
        <!-- eslint-enable vue/multiline-html-element-content-newline -->
      </p>
      <line-chart
        :data="lineChartData"
        :labels="lineChartLabels"
        :type="metric.type"
        :suggested-min="suggestedMin"
        :suggested-max="suggestedMax"
        :width="800"
      />
      <p class="font-sm mt-3">
        <router-link :to="{ name: 'metrics-redirect' }">
          return to metrics
        </router-link>
      </p>
    </template>
    <p v-else class="text-center">Sorry, that metric was not found.</p>
  </loading-box>
</template>

<script>
import { DateTime } from "luxon";

import LineChart from "components/LineChart.js";

import { convertTimeStringToMinutes } from "common.js";

export default {
  components: {
    LineChart,
  },
  props: {
    metricName: { type: String, required: true },
  },

  data() {
    return {
      metric: null,
    };
  },

  computed: {
    lineChartData() {
      return this.metricValues.map((o) => o.value);
    },

    lineChartLabels() {
      return this.metricValues.map((o) => o.month);
    },

    metricValues() {
      const values = [];
      for (const valuePair of this.metric.values) {
        let value = valuePair[1];

        if (value !== null && this.metric.type === "time") {
          value = convertTimeStringToMinutes(value);
        }

        // Add null values so that any gaps in metric collection are shown.
        // Trailing nulls will be popped off the array in the while loop below.
        if (value !== null || values.length > 0) {
          values.push({ month: valuePair[0], value });
        }
      }

      // Remove null entries from the end of the array.
      while (values.length > 0 && values[values.length - 1].value === null) {
        values.pop();
      }

      return values;
    },

    suggestedMax() {
      if (this.metric.type === "percentage") {
        return 1;
      } else {
        return this.metric.suggestedMax;
      }
    },

    suggestedMin() {
      if (this.metric.type === "percentage") {
        return 0;
      } else {
        return this.metric.suggestedMin;
      }
    },

    start() {
      return DateTime.fromISO(this.metric.start).toFormat("MMMM y");
    },

    end() {
      if (this.metric.end === null) {
        return null;
      }

      return DateTime.fromISO(this.metric.end).toFormat("MMMM y");
    },
  },
};
</script>
