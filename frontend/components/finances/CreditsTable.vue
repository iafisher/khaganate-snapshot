<template>
  <b-table
    striped
    hover
    outlined
    :fields="creditFields"
    :items="credits"
    sort-by="dateIncurred"
    :sort-desc="true"
  >
    <template #cell(dateIncurred)="data">
      <span :title="'Actual date of payment: ' + data.item.datePaid">
        <date-link :date="data.value" />
      </span>
    </template>

    <template #cell(category)="data">
      <router-link
        :to="{
          name: 'finances-category',
          params: { category: data.value.categorySlug },
        }"
      >
        {{ data.value.category }}
      </router-link>
    </template>

    <template #cell(subcategory)="data">
      <router-link
        :to="{
          name: 'finances-subcategory',
          params: {
            category: data.item.category.categorySlug,
            subcategory: data.item.category.subcategorySlug,
          },
        }"
      >
        {{ data.item.category.subcategory }}
      </router-link>
    </template>

    <template #cell(vendor)="data">
      <router-link
        v-if="!!data.value"
        :to="{ name: 'finances-vendor', params: { vendor: data.value.id } }"
      >
        {{ data.value.name }}
      </router-link>
    </template>
  </b-table>
</template>

<script>
import { formatDollarAmount } from "common.js";

export default {
  props: {
    credits: { type: Array, required: true },
  },

  data() {
    return {
      creditFields: [
        { key: "id", label: "" },
        { key: "dateIncurred", label: "Date", sortable: true },
        { key: "category", sortable: true },
        { key: "subcategory", sortable: true },
        { key: "vendor", sortable: true },
        { key: "amount", formatter: formatDollarAmount, sortable: true },
        { key: "paymentMethod", label: "Method", sortable: true },
        { key: "notes" },
      ],
    };
  },

  methods: {
    getMonthLink(isoDate) {
      const year = isoDate.slice(0, 4);
      const month = isoDate.slice(5, 7);
      return { name: "finances-month", params: { year, month } };
    },
  },
};
</script>

<style scoped>
table {
  font-size: 0.9rem;
}
</style>
