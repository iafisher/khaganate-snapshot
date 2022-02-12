<template>
  <b-table
    striped
    hover
    outlined
    :fields="debitFields"
    :items="debits"
    sort-by="dateIncurred"
    :sort-desc="true"
  >
    <template #cell(dateIncurred)="data">
      <date-link :date="data.value" />
    </template>

    <template #cell(category)="data">
      {{ data.value.category }}
    </template>

    <template #cell(source)="data">
      {{ data.value.name }}
    </template>
  </b-table>
</template>

<script>
import { formatDollarAmount } from "common.js";

export default {
  props: {
    debits: { type: Array, required: true },
  },

  data() {
    return {
      debitFields: [
        { key: "id", label: "" },
        { key: "dateIncurred", label: "Date", sortable: true },
        { key: "category", sortable: true },
        { key: "source", sortable: true },
        { key: "amount", formatter: formatDollarAmount, sortable: true },
        { key: "notes" },
      ],
    };
  },
};
</script>
