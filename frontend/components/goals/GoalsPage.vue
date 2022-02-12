<template>
  <div class="page">
    <month-nav
      :year="year"
      :month="month"
      url="goals-month"
      :earliest="earliest"
    />
    <goals-card :year="year" :month="month" />
  </div>
</template>

<script>
import { DateTime } from "luxon";

import GoalsCard from "./GoalsCard.vue";

export default {
  components: {
    GoalsCard,
  },
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: true },
  },

  computed: {
    earliest() {
      return DateTime.fromObject({ year: 2022, month: 2 });
    },
  },
};
</script>
