import { Bar } from "vue-chartjs";

import { formatDollarAmount, MONTHS } from "common.js";

const GREEN = "#339900";
const RED = "#ff6666";

export default {
  props: {
    data: { type: Array, required: true },
    positiveIsGood: { type: Boolean, default: true },
  },
  extends: Bar,

  data() {
    return {
      options: {
        legend: {
          display: false,
        },
        responsive: false,
        // Start the y-axis at 0.
        scales: {
          yAxes: [
            {
              display: true,
              ticks: {
                suggestedMin: 0,
                callback: (value) => {
                  return formatDollarAmount(value);
                },
              },
            },
          ],
        },
        tooltips: {
          callbacks: {
            label: this.getTooltipLabel,
          },
        },
      },
    };
  },

  watch: {
    data() {
      this.render();
    },

    positiveIsGood() {
      this.render();
    },
  },

  methods: {
    render() {
      const colors = [];
      for (const datum of this.data) {
        if (
          (this.positiveIsGood && datum > 0) ||
          (!this.positiveIsGood && datum <= 0)
        ) {
          colors.push(GREEN);
        } else {
          colors.push(RED);
        }
      }

      const chartjsData = {
        labels: MONTHS,
        datasets: [
          {
            data: this.data,
            backgroundColor: colors,
          },
        ],
      };

      this.renderChart(chartjsData, this.options);
    },

    getTooltipLabel(tooltip, dataset) {
      const data = dataset.datasets[0].data[tooltip.index];
      const label = dataset.labels[tooltip.index];
      return `${label}: ${formatDollarAmount(data)}`;
    },
  },

  mounted() {
    this.render();
  },
};
