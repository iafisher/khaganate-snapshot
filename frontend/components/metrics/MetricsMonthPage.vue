<template>
  <loading-box class="page-wider" :url="apiUrl" @data-loaded="metrics = $event">
    <h1 class="text-center">
      Metrics for
      <template v-if="month">
        {{ monthName }}
        {{ year }}
      </template>
      <template v-else>
        {{ year }}
      </template>
    </h1>

    <month-nav
      :year="year"
      :month="month"
      :earliest="earliest"
      url="metrics-month"
    />

    <div v-for="group in groups" :key="group.name" class="mb-3">
      <h2>{{ group.name }}</h2>
      <div class="group-metrics">
        <div
          v-for="metric in group.metrics"
          :key="metric.name"
          :class="['statbox', 'text-center', getClass(metric)]"
        >
          <p class="statbox-title">
            <router-link
              :to="{ name: 'metrics', params: { metricName: metric.name } }"
            >
              {{ metric.displayTitle }}
            </router-link>
          </p>
          <p class="statbox-main">
            {{ formatMetricValue(metric.type, metric.value) }}
          </p>
        </div>
      </div>
    </div>
  </loading-box>
</template>

<script>
import * as lodash from "lodash";
import { DateTime } from "luxon";

import { formatMetricValue, getMonthName } from "common.js";

export default {
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
  },

  data() {
    return {
      earliest: DateTime.fromObject({ year: 2022, month: 2 }),
      metrics: [],
    };
  },

  computed: {
    apiUrl() {
      return `/api/metrics/list/${this.year}/${this.month}`;
    },

    groups() {
      const groupsMap = new Map();
      const ungroupedMetrics = [];
      for (const metric of this.metrics) {
        if (metric.group === null) {
          ungroupedMetrics.push(metric);
          continue;
        }

        const groupName = metric.group;
        let groupObject;
        if (!groupsMap.has(groupName)) {
          groupObject = { name: groupName, metrics: [] };
          groupsMap.set(groupName, groupObject);
        } else {
          groupObject = groupsMap.get(groupName);
        }

        groupObject.metrics.push(metric);
      }

      const groups = lodash.orderBy(Array.from(groupsMap.values()), ["name"]);
      groups.push({ name: "Other", metrics: ungroupedMetrics });
      return groups;
    },

    monthName() {
      return getMonthName(this.month);
    },

    rows() {
      let index = 0;
      const rows = [];
      while (index < this.metrics.length) {
        rows.push(this.metrics.slice(index, index + 4));
        index += 4;
      }
      return rows;
    },
  },

  methods: {
    formatMetricValue,

    getClass(metric) {
      if (metric.value === null) {
        return "neutral";
      }

      if (
        metric.goodThreshold &&
        ((metric.higherIsBetter && metric.value >= metric.goodThreshold) ||
          (!metric.higherIsBetter && metric.value <= metric.goodThreshold))
      ) {
        return "good";
      }

      if (
        metric.badThreshold &&
        ((metric.higherIsBetter && metric.value <= metric.badThreshold) ||
          (!metric.higherIsBetter && metric.value >= metric.badThreshold))
      ) {
        return "bad";
      }

      return "neutral";
    },
  },
};
</script>

<style scoped>
.group-metrics {
  display: flex;
  flex-flow: row wrap;
  gap: 10px;
}

.statbox {
  height: 150px;
  width: 225px;
  position: relative;
  border-radius: 5px;
}

.statbox-title {
  position: absolute;
  top: 0;
  margin-top: 5px;
  width: 100%;
}

.statbox-main {
  font-size: 24px;
  position: absolute;
  top: 55px;
  margin-top: 0;
  width: 100%;
}

.statbox-mean {
  font-size: 12px;
  position: absolute;
  bottom: 0;
  margin-bottom: 5px;
  width: 100%;
}

a {
  color: initial;
  text-decoration: underline;
}

.good {
  background-color: #c8e6c9;
  border: 1px solid darkgreen;
}

.neutral {
  background-color: whitesmoke;
  border: 1px solid #ccc;
}

.bad {
  background-color: rgba(217, 48, 37, 0.5);
  border: 1px solid darkred;
}
</style>
