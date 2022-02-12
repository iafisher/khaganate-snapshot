<template>
  <loading-box
    class="page-very-wide"
    :url="apiUrls"
    @data-loaded="onDataLoaded"
  >
    <h1 class="text-center">
      Finances for {{ monthName }}
      <router-link :to="{ name: 'finances-year', params: { year } }">
        {{ year }}
      </router-link>
    </h1>

    <month-nav
      :year="year"
      :month="month"
      url="finances-month"
      year-url="finances-year"
      :earliest="earliest"
      :latest="latest"
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
      class="category-chart"
      :entries="credits"
      :width="400"
      :height="400"
    />

    <b-row>
      <b-col>
        <div class="header-row">
          <h2>Credits</h2>
          <b-button
            size="sm"
            variant="outline-primary"
            @click="$bvModal.show('new-credit-modal')"
          >
            <b-icon icon="plus"></b-icon>
          </b-button>
        </div>

        <b-input
          v-model="creditSearchFilter"
          class="search"
          placeholder="Search (enter at least 3 characters)"
        />
        <credits-table :credits="filteredCredits" />
      </b-col>
      <b-col>
        <div class="header-row">
          <h2>Debits</h2>
          <b-button
            size="sm"
            variant="outline-primary"
            @click="$bvModal.show('new-debit-modal')"
          >
            <b-icon icon="plus"></b-icon>
          </b-button>
        </div>

        <b-input
          v-model="debitSearchFilter"
          class="search"
          placeholder="Search (enter at least 3 characters)"
        />
        <debits-table :debits="filteredDebits" />
      </b-col>
    </b-row>

    <b-modal
      id="new-credit-modal"
      size="lg"
      :ok-disabled="true"
      title="New credit"
    >
      <template #default="{ ok }">
        <new-credit-form
          @form-submitted="
            onCreditCreated($event);
            ok();
          "
        />
      </template>

      <template #modal-footer>
        <span></span>
      </template>
    </b-modal>

    <b-modal
      id="new-debit-modal"
      size="lg"
      :ok-disabled="true"
      title="New debit"
    >
      <template #default="{ ok }">
        <new-debit-form
          @form-submitted="
            onDebitCreated($event);
            ok();
          "
        />
      </template>

      <template #modal-footer>
        <span></span>
      </template>
    </b-modal>
  </loading-box>
</template>

<script>
import * as lodash from "lodash";
import { DateTime } from "luxon";

import { getMonthName } from "common.js";
import { EARLIEST_MONTH_OF_DATA } from "./finances.js";
import CategoryChart from "./CategoryChart.js";
import CreditsTable from "./CreditsTable.vue";
import DebitsTable from "./DebitsTable.vue";
import NewCreditForm from "./NewCreditForm.vue";
import NewDebitForm from "./NewDebitForm.vue";

export default {
  components: {
    CategoryChart,
    CreditsTable,
    DebitsTable,
    NewCreditForm,
    NewDebitForm,
  },
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
  },

  data() {
    return {
      earliest: EARLIEST_MONTH_OF_DATA,
      latest: DateTime.local().plus({ months: 1 }),
      credits: [],
      creditSearchFilter: "",
      debits: [],
      debitSearchFilter: "",
    };
  },

  computed: {
    apiUrls() {
      const paddedMonth = (this.month + "").padStart(2, "0");
      const filter = `date_incurred__startswith=${this.year}-${paddedMonth}`;
      return [
        `/api/db/list/credits?${filter}`,
        `/api/db/list/debits?${filter}`,
      ];
    },

    filteredCredits() {
      if (this.creditSearchFilter.length < 3) {
        return this.credits;
      }

      const q = this.creditSearchFilter.toLowerCase();
      return this.credits.filter(
        (credit) =>
          credit.vendor && credit.vendor.name.toLowerCase().includes(q)
      );
    },

    filteredDebits() {
      if (this.debitSearchFilter.length < 3) {
        return this.debits;
      }

      const q = this.debitSearchFilter.toLowerCase();
      return this.debits.filter(
        (debit) => debit.source && debit.source.name.toLowerCase().includes(q)
      );
    },

    monthName() {
      return getMonthName(this.month);
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
  },

  watch: {
    $route() {
      this.creditSearchFilter = "";
      this.debitSearchFilter = "";
    },
  },

  methods: {
    onDataLoaded(responses) {
      this.credits = responses[0];
      this.debits = responses[1];
    },

    onCreditCreated(credit) {
      const dateIncurred = DateTime.fromISO(credit.dateIncurred);
      if (
        dateIncurred.year === this.year &&
        dateIncurred.month === this.month
      ) {
        this.credits.push(credit);
      }
    },

    onDebitCreated(debit) {
      const dateIncurred = DateTime.fromISO(debit.dateIncurred);
      if (
        dateIncurred.year === this.year &&
        dateIncurred.month === this.month
      ) {
        this.debits.push(debit);
      }
    },
  },
};
</script>

<style scoped>
.category-chart {
  margin: auto;
  margin-bottom: 30px;
  width: 400px;
}

.header-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.header-row button {
  margin-left: auto;
}

table {
  margin-top: 10px;
  font-size: 0.9rem;
}

.search {
  max-width: 400px;
}
</style>
