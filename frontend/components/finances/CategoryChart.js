import * as lodash from "lodash";
import { Doughnut } from "vue-chartjs";

import { formatDollarAmount } from "common.js";

export default {
  props: {
    entries: { type: Array, required: true },
    subcategories: { type: Boolean, default: false },
  },
  extends: Doughnut,

  data() {
    return {
      options: {
        responsive: false,
        tooltips: {
          callbacks: {
            label: this.getTooltipLabel,
          },
        },
      },
    };
  },

  computed: {
    totalCredited() {
      return lodash.sum(this.entries.map((entry) => entry.amount));
    },
  },

  watch: {
    entries: function () {
      this.render();
    },
  },

  methods: {
    render() {
      const categoryAmounts = new Map();
      for (const entry of this.entries) {
        const key = this.subcategories
          ? entry.category.subcategory
          : entry.category.category;
        if (!categoryAmounts.has(key)) {
          categoryAmounts.set(key, entry.amount);
        } else {
          categoryAmounts.set(key, categoryAmounts.get(key) + entry.amount);
        }
      }

      // Sort the categories by amount, in descending order.
      const labeledData = [];
      for (const [category, amount] of categoryAmounts) {
        labeledData.push({ label: category, data: amount });
      }
      labeledData.sort((a, b) => b.data - a.data);

      // Split the labeled data into separate arrays for the labels and the data.
      const labels = [];
      const innerData = [];
      for (const labeledItem of labeledData) {
        labels.push(labeledItem.label);
        innerData.push(labeledItem.data);
      }

      const data = {
        labels: labels,
        datasets: [
          {
            data: innerData,
            backgroundColor: [
              // Courtesy of https://learnui.design/tools/data-color-picker.html#divergent
              "#00876c",
              "#51a472",
              "#89bf77",
              "#c2d980",
              "#fff18f",
              "#fcc76b",
              "#f59b56",
              "#e96d4e",
              "#de425b",
            ],
          },
        ],
      };

      this.renderChart(data, this.options);
    },

    getTooltipLabel(tooltip, dataset) {
      const data = dataset.datasets[0].data[tooltip.index];
      const label = dataset.labels[tooltip.index];
      const perc = 100 * (data / this.totalCredited);
      return `${label}: ${formatDollarAmount(data)} (${perc.toFixed(1)}%)`;
    },
  },

  mounted() {
    this.render();
  },
};
