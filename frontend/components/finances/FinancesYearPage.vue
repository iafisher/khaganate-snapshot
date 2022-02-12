<template>
  <loading-box class="page-full" :url="apiUrls" @data-loaded="onDataLoaded">
    <h1 class="text-center">Finances for {{ year }}</h1>

    <month-nav
      :year="year"
      url="finances-month"
      year-url="finances-year"
      :earliest="earliest"
    />

    <p class="main-point">
      <span class="text-success">{{ totalDebited | usd }}</span> debited -
      <span class="text-danger">{{ totalCredited | usd }}</span> credited =
      <strong :class="netIncome > 0 ? 'text-success' : 'text-danger'">
        {{ netIncome | usd }}
      </strong>
      net income
    </p>

    <category-chart
      :entries="credits"
      :width="400"
      :height="400"
      css-classes="mx-auto"
      :styles="{ width: '400px' }"
    />

    <b-row>
      <b-col>
        <h1 class="text-center">Net income</h1>
        <year-bar-chart
          :data="netIncomeByMonth"
          :width="400"
          :height="400"
          css-classes="mx-auto"
          :styles="{ width: '400px' }"
        />
      </b-col>
      <b-col>
        <h1 class="text-center">Aggregate income</h1>
        <year-bar-chart
          :data="aggregateIncomeByMonth"
          :width="400"
          :height="400"
          css-classes="mx-auto"
          :styles="{ width: '400px' }"
        />
      </b-col>
    </b-row>
    <b-row>
      <b-col>
        <h1 class="text-center">Total credited</h1>
        <year-bar-chart
          :data="totalCreditedByMonth"
          :positive-is-good="false"
          :width="400"
          :height="400"
          css-classes="mx-auto"
          :styles="{ width: '400px' }"
        />
      </b-col>
      <b-col>
        <h1 class="text-center">Total debited</h1>
        <year-bar-chart
          :data="totalDebitedByMonth"
          :width="400"
          :height="400"
          css-classes="mx-auto"
          :styles="{ width: '400px' }"
        />
      </b-col>
    </b-row>
  </loading-box>
</template>

<script>
import * as lodash from "lodash";

import { EARLIEST_MONTH_OF_DATA } from "./finances.js";
import CategoryChart from "./CategoryChart.js";
import YearBarChart from "./YearBarChart.js";

export default {
  components: {
    CategoryChart,
    YearBarChart,
  },
  props: {
    year: { type: Number, required: true },
  },

  data() {
    return {
      credits: [],
      debits: [],
      earliest: EARLIEST_MONTH_OF_DATA,
    };
  },

  computed: {
    apiUrls() {
      const filter = `date_incurred__startswith=${this.year}`;
      return [
        `/api/db/list/credits?${filter}`,
        `/api/db/list/debits?${filter}`,
      ];
    },

    totalCredited() {
      return lodash.sum(this.credits.map((credit) => credit.amount));
    },

    totalDebited() {
      return lodash.sum(this.debits.map((debit) => debit.amount));
    },

    netIncome() {
      return this.totalDebited - this.totalCredited;
    },

    netIncomeByMonth() {
      const netIncome = [];

      const groupedCredits = this.groupByMonth(this.credits);
      const groupedDebits = this.groupByMonth(this.debits);
      for (const [credits, debits] of lodash.zip(
        groupedCredits,
        groupedDebits
      )) {
        const totalCredited = credits ? lodash.sum(credits) : 0;
        const totalDebited = debits ? lodash.sum(debits) : 0;
        netIncome.push(totalDebited - totalCredited);
      }
      return netIncome;
    },

    aggregateIncomeByMonth() {
      const aggregateIncome = [];
      let aggregate = 0;

      for (const netIncome of this.netIncomeByMonth) {
        aggregate += netIncome;
        aggregateIncome.push(aggregate);
      }
      return aggregateIncome;
    },

    totalCreditedByMonth() {
      return this.groupByMonth(this.credits).map(lodash.sum);
    },

    totalDebitedByMonth() {
      return this.groupByMonth(this.debits).map(lodash.sum);
    },
  },

  methods: {
    groupByMonth(entries) {
      const months = [[], [], [], [], [], [], [], [], [], [], [], []];
      for (const entry of entries) {
        const month = parseInt(entry.dateIncurred.split("-")[1]);
        const monthIndex = month - 1;
        months[monthIndex].push(entry.amount);
      }
      return months;
    },

    onDataLoaded(responses) {
      this.credits = responses[0];
      this.debits = responses[1];
    },
  },
};
</script>
