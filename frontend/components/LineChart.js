import { Line } from "vue-chartjs";

import { formatMetricValue } from "common.js";

export default {
  props: {
    labels: { type: Array, required: true },
    data: { type: Array, required: true },
    type: { type: String, required: true, default: "integer" },
    suggestedMin: { type: Number, required: false },
    suggestedMax: { type: Number, required: false },
  },
  extends: Line,

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
                suggestedMin: this.suggestedMin,
                suggestedMax: this.suggestedMax,
                callback: (value) => {
                  return formatMetricValue(this.type, value);
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
    labels() {
      this.render();
    },

    data() {
      this.render();
    },
  },

  methods: {
    render() {
      const chartjsData = {
        labels: this.labels,
        datasets: [
          {
            data: this.data,
            backgroundColor: "transparent",
            borderColor: "lightblue",
            // Draw straight lines instead of curved ones.
            lineTension: 0,
            pointBorderColor: "rgba(0, 99, 132, 1)",
            pointBackgroundColor: "rgba(0, 99, 132, 0.6)",
          },
        ],
      };

      this.renderChart(chartjsData, this.options);
    },

    getTooltipLabel(tooltip, dataset) {
      const data = dataset.datasets[0].data[tooltip.index];
      const label = dataset.labels[tooltip.index];
      return `${label}: ${formatMetricValue(this.type, data)}`;
    },
  },

  mounted() {
    this.render();
  },
};
