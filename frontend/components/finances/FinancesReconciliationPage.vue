<template>
  <loading-box class="page-full" :url="apiUrls" @data-loaded="onDataLoaded">
    <h1>Reconciliation for {{ monthName }} {{ year }}</h1>

    <p>
      See
      <router-link :to="{ name: 'finances-recurring' }">
        the recurring charges page
      </router-link>
      for details about recurring charges.
    </p>

    <b-row class="mt-3">
      <b-col>
        <div class="header-row">
          <h2>Credits</h2>
          <b-button
            size="sm"
            variant="outline-primary"
            :disabled="creditsUndoStack.length === 0"
            @click="onUndoCredit"
          >
            undo
          </b-button>
        </div>

        <!-- Although BootstrapVue requires us to set the `sort-by` attribute,
             sorting is wholly determined by the `creditsSortCompare` method.
        -->
        <b-table
          striped
          hover
          outlined
          :fields="creditFields"
          :items="credits"
          :filter-function="filterCredit"
          filter="yes"
          sort-by="datePaid"
          :sort-compare="creditsSortCompare"
          :sort-desc="true"
        >
          <template #cell(datePaid)="data">
            <date-link :date="data.value" />
          </template>
          <template #cell(vendor)="data">
            {{ data.value.name }}
          </template>
          <template #cell(button)="data">
            <b-button variant="primary" @click="onHideCredit(data.item.id)">
              Done
            </b-button>
          </template>
        </b-table>
      </b-col>
      <b-col>
        <div class="header-row">
          <h2>Debits</h2>
          <b-button
            size="sm"
            variant="outline-primary"
            :disabled="debitsUndoStack.length === 0"
            @click="onUndoDebit"
          >
            undo
          </b-button>
        </div>

        <b-table
          striped
          hover
          outlined
          :fields="debitFields"
          :items="debits"
          sort-by="datePaid"
          :sort-desc="true"
        >
          <template #cell(datePaid)="data">
            <date-link :date="data.value" />
          </template>
          <template #cell(source)="data">
            {{ data.value.name }}
          </template>
          <template #cell(button)="data">
            <b-button variant="primary" @click="onHideDebit(data.item.id)">
              Done
            </b-button>
          </template>
        </b-table>
      </b-col>
    </b-row>
  </loading-box>
</template>

<script>
import { formatDollarAmount, getMonthName } from "common.js";

export default {
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
  },

  data() {
    return {
      credits: [],
      creditsUndoStack: [],
      creditFields: [
        { key: "id", label: "" },
        { key: "datePaid", label: "Date" },
        { key: "vendor" },
        { key: "amount", formatter: formatDollarAmount },
        { key: "paymentMethod", label: "Method" },
        { key: "notes" },
        { key: "button", label: "" },
      ],
      debits: [],
      debitsUndoStack: [],
      debitFields: [
        { key: "id", label: "" },
        { key: "datePaid", label: "Date" },
        { key: "source" },
        { key: "amount", formatter: formatDollarAmount },
        { key: "notes" },
        { key: "button", label: "" },
      ],
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

    monthName() {
      return getMonthName(this.month);
    },

    nextMonthName() {
      return this.month === 12 ? "January" : getMonthName(this.month + 1);
    },
  },

  methods: {
    onDataLoaded(responses) {
      this.credits = responses[0];
      this.debits = responses[1];
    },

    onHideCredit(id) {
      const index = this.credits.findIndex((row) => row.id === id);
      if (index !== -1) {
        this.creditsUndoStack.push(this.credits[index]);
        this.credits.splice(index, 1);
      }
    },

    onHideDebit(id) {
      const index = this.debits.findIndex((row) => row.id === id);
      if (index !== -1) {
        this.debitsUndoStack.push(this.debits[index]);
        this.debits.splice(index, 1);
      }
    },

    onUndoCredit() {
      const e = this.creditsUndoStack.pop();
      this.credits.push(e);
    },

    onUndoDebit() {
      const e = this.debitsUndoStack.pop();
      this.debits.push(e);
    },

    filterCredit(credit) {
      return credit.paymentMethod !== "Cash";
    },

    creditsSortCompare(a, b) {
      // Ascending sort on payment method, then descending sort on date.
      if (a.paymentMethod < b.paymentMethod) {
        return 1;
      } else if (a.paymentMethod > b.paymentMethod) {
        return -1;
      } else {
        if (a.datePaid < b.datePaid) {
          return -1;
        } else if (a.datePaid > b.datePaid) {
          return 1;
        } else {
          return 0;
        }
      }
    },
  },
};
</script>

<style scoped>
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
</style>
