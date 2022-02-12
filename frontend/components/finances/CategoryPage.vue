<template>
  <loading-box class="page-wide" :url="apiUrls" @data-loaded="onDataLoaded">
    <h1 class="text-center">
      <template v-if="subcategoryTitle">
        <router-link :to="{ name: 'finances-category', params: { category } }">
          {{ categoryTitle }}
        </router-link>
        / {{ subcategoryTitle }}
      </template>
      <template v-else-if="categoryTitle">
        {{ categoryTitle }}
      </template>
    </h1>

    <p class="main-point">
      <strong>{{ totalLast12Months | usd }}</strong> spent in
      <strong>
        {{ creditsLast12Months.length | pluralize("transaction") }}
      </strong>
      in the past 12 months
    </p>

    <b-nav v-if="sortedSubcategories" align="center" class="mb-3">
      <b-nav-item
        v-for="otherSubcategory in sortedSubcategories"
        :key="otherSubcategory.slug"
      >
        <router-link
          :to="{
            name: 'finances-subcategory',
            params: { category, subcategory: otherSubcategory.slug },
          }"
        >
          {{ otherSubcategory.name }}
        </router-link>
      </b-nav-item>
    </b-nav>

    <b-row class="mb-3">
      <line-chart
        :data="lineChartData"
        :labels="lineChartLabels"
        type="dollar"
        :suggested-min="0"
        :suggested-max="100"
        :width="800"
        :height="400"
        css-classes="mx-auto"
        :styles="{ width: '800px' }"
      />
    </b-row>

    <template v-if="!subcategory">
      <b-row class="mb-3">
        <category-chart
          :entries="creditsLast12Months"
          :subcategories="true"
          :width="800"
          :height="400"
          css-classes="mx-auto"
          :styles="{ width: '800px' }"
        />
      </b-row>
      <p class="font-sm text-center">
        Pie chart is for last 12 months of expenses only.
      </p>
    </template>

    <credits-table :credits="credits" :links-to-month-pages="true" />
  </loading-box>
</template>

<script>
import * as lodash from "lodash";
import { DateTime } from "luxon";

import CategoryChart from "./CategoryChart.js";
import LineChart from "components/LineChart.js";
import CreditsTable from "./CreditsTable.vue";

export default {
  components: {
    CategoryChart,
    CreditsTable,
    LineChart,
  },
  props: {
    category: { type: String, required: true },
    subcategory: { type: String, required: false, default: "" },
  },

  data() {
    return {
      categoryTitle: "",
      credits: [],
      subcategoryTitle: "",
      subcategories: [],
    };
  },

  computed: {
    apiUrls() {
      const urls = ["/api/db/list/credits"];
      if (this.subcategory) {
        urls.push(
          `/api/finances/credit-categories/get/${this.category}/${this.subcategory}`
        );
      } else {
        urls.push(`/api/finances/credit-categories/get/${this.category}`);
      }
      return urls;
    },

    creditsLast12Months() {
      const start = DateTime.local()
        .startOf("month")
        .minus({ months: 11 })
        .toISODate();
      return this.credits.filter((credit) => credit.dateIncurred >= start);
    },

    totalLast12Months() {
      return lodash.sum(
        this.creditsLast12Months.map((credit) => credit.amount)
      );
    },

    months() {
      const months = [];
      let month = DateTime.local(2019, 7);
      while (month < this.todayAdjusted()) {
        months.push(month);
        month = month.plus({ months: 1 });
      }
      return months;
    },
    lineChartData() {
      const groups = lodash.groupBy(this.credits, (credit) => {
        return DateTime.fromISO(credit.dateIncurred)
          .startOf("month")
          .toISODate();
      });

      return this.months.map((month) => {
        const credits = groups[month.toISODate()] || [];
        return lodash.sum(credits.map((credit) => credit.amount));
      });
    },

    lineChartLabels() {
      return this.months.map((month) => month.toFormat("MMM y"));
    },

    sortedSubcategories() {
      return lodash.sortBy(this.subcategories, "name");
    },
  },

  methods: {
    onDataLoaded(responses) {
      const creditsResponse = responses[0];
      const categoryResponse = responses[1];

      this.categoryTitle = categoryResponse.category;
      this.subcategories = categoryResponse.subcategories;
      if (this.subcategory) {
        this.subcategoryTitle = categoryResponse.subcategory;
        document.title = `${this.categoryTitle} / ${this.subcategoryTitle} | Khaganate`;
      } else {
        this.subcategoryTitle = "";
        document.title = `${this.categoryTitle} | Khaganate`;
      }

      this.credits = creditsResponse.filter((credit) => {
        if (this.subcategory) {
          return (
            credit.category.category === this.categoryTitle &&
            credit.category.subcategory === this.subcategoryTitle
          );
        } else {
          return credit.category.category === this.categoryTitle;
        }
      });
    },
  },
};
</script>
