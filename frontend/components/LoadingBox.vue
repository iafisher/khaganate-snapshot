<template>
  <div>
    <template v-if="failed">
      <p class="text-center">
        The component could not be loaded due to an API error.
      </p>
    </template>
    <template v-else-if="loading">
      <p class="text-center"><b-spinner style="width: 4rem; height: 4rem" /></p>
    </template>
    <template v-else>
      <slot></slot>
    </template>
  </div>
</template>

<script>
import { isString } from "lodash";

export default {
  props: {
    sql: { type: String, required: false, default: "" },
    url: { type: [Array, String], required: false, default: "" },
    refresh: { type: Number, required: false, default: 0 },
    refreshSilently: { type: Number, required: false, default: 0 },
  },
  emits: ["data-loaded"],

  data() {
    return { failed: false, loading: false };
  },

  watch: {
    $route() {
      this.fetchData();
    },

    refresh() {
      this.fetchData(/* silently= */ false);
    },

    refreshSilently() {
      this.fetchData(/* silently= */ true);
    },
  },

  created() {
    this.fetchData();
  },

  methods: {
    fetchData(silently) {
      if (!silently) {
        this.loading = true;
      }

      const promises = [];
      let multiple = false;
      if (this.sql !== "") {
        promises.push(this.$dbQuery(this.sql));
      } else {
        if (this.url === "") {
          throw "sql and url props to LoadingPage cannot both be empty";
        }

        if (isString(this.url)) {
          promises.push(this.$apiGet(this.url));
        } else {
          multiple = true;
          for (const url of this.url) {
            promises.push(this.$apiGet(url));
          }
        }
      }

      Promise.all(promises)
        .then((data) => {
          this.loading = false;
          this.$emit("data-loaded", multiple ? data : data[0]);
        })
        .catch(() => {
          this.failed = true;
        });
    },
  },
};
</script>
