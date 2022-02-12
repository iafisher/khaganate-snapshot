<template>
  <p class="text-center">
    <span class="mr-3">
      <template v-if="!earliest || year > earliest.year">
        <router-link :to="previousUrl"> &lt; {{ year - 1 }} </router-link>
      </template>
      <template v-else>&lt; {{ year - 1 }}</template>
    </span>

    <span v-for="monthObj in months" :key="monthObj.name" class="spaced-inline">
      <strong v-if="monthObj.current">{{ monthObj.name }}</strong>
      <router-link v-else-if="monthObj.url" :to="monthObj.url">
        {{ monthObj.name }}
      </router-link>
      <span v-else>{{ monthObj.name }}</span>
    </span>

    <span class="ml-3">
      <template v-if="year < currentYear">
        <router-link :to="nextUrl"> {{ year + 1 }} &gt; </router-link>
      </template>
      <template v-else>{{ year + 1 }} &gt;</template>
    </span>
  </p>
</template>

<script>
import { DateTime } from "luxon";

export default {
  props: {
    year: { type: Number, required: true },
    month: { type: Number, required: false, default: null },
    url: { type: String, required: true },
    yearUrl: { type: String, required: false, default: "" },
    earliest: { type: Object, required: false, default: null },
    latest: { type: Object, required: false, default: null },
  },

  computed: {
    currentYear() {
      return DateTime.local().year;
    },

    months() {
      const names = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
      ];
      const months = [];
      for (let index = 0; index < names.length; index++) {
        const name = names[index];
        const month = {
          name,
          current: this.month && index + 1 === this.month,
          url: {
            name: this.url,
            params: { year: this.year, month: index + 1 },
          },
        };

        const monthAsDateTime = DateTime.fromObject({
          year: this.year,
          month: index + 1,
        });

        // Set the URL to null if the month is before the earliest allowed
        // month.
        if (this.earliest && monthAsDateTime < this.earliest) {
          month.url = null;
        }

        // Set the URL to null if the month is (too far) in the future.
        const latest = this.latest || DateTime.local();
        if (monthAsDateTime > latest) {
          month.url = null;
        }

        months.push(month);
      }
      return months;
    },

    nextUrl() {
      if (this.yearUrl) {
        return { name: this.yearUrl, params: { year: this.year + 1 } };
      } else {
        return { name: this.url, params: { year: this.year + 1, month: 1 } };
      }
    },

    previousUrl() {
      if (this.yearUrl) {
        return { name: this.yearUrl, params: { year: this.year - 1 } };
      } else {
        return { name: this.url, params: { year: this.year - 1, month: 12 } };
      }
    },
  },
};
</script>
