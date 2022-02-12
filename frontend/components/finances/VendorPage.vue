<template>
  <loading-box class="page-wide" :url="apiUrls" @data-loaded="onDataLoaded">
    <h1 v-if="vendorTitle" class="text-center">
      {{ vendorTitle }}
    </h1>

    <p class="main-point">
      <strong>{{ totalLast12Months | usd }}</strong> spent in
      <strong>
        {{ creditsLast12Months.length | pluralize("transaction") }}
      </strong>
      in the past 12 months
    </p>

    <credits-table :credits="credits" :links-to-month-pages="true" />
  </loading-box>
</template>

<script>
import * as lodash from "lodash";
import { DateTime } from "luxon";

import CreditsTable from "./CreditsTable.vue";

export default {
  components: {
    CreditsTable,
  },
  props: {
    vendor: { type: Number, required: true },
  },

  data() {
    return {
      credits: [],
      vendorTitle: "",
    };
  },

  computed: {
    apiUrls() {
      return [
        `/api/db/list/credits?vendor=${this.vendor}`,
        `/api/db/get/vendors/${this.vendor}`,
      ];
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
  },

  methods: {
    onDataLoaded(responses) {
      this.credits = responses[0];
      this.vendorTitle = responses[1].name;
      document.title = `${this.vendorTitle} | Khaganate`;
    },
  },
};
</script>
