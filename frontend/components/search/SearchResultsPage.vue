<template>
  <loading-box class="page-wide" :url="apiUrl" @data-loaded="onDataLoaded">
    <p class="main-point">
      {{ results.length | pluralize("result") }} for '{{ query }}'
    </p>

    <p v-if="typeOptions.length > 1" class="text-center">
      <b-form-checkbox-group
        v-model="selectedTypes"
        :options="typeOptions"
      ></b-form-checkbox-group>
    </p>
    <p class="text-center">
      <b-form-checkbox v-model="showPreviews">Show previews</b-form-checkbox>
    </p>

    <b-list-group>
      <b-list-group-item
        v-for="(result, index) in sortedResults"
        :key="result.path"
      >
        <div class="result-index">{{ index + 1 }}.</div>
        <div class="result-body">
          <b-badge pill :variant="getBadgeVariant(result)">
            {{ result.type }}
          </b-badge>

          <template v-if="result.url">
            <a :href="result.url">
              <markdown-inline
                v-if="result.hasMarkdownTitle"
                :text="result.title"
              />
              <template v-else>{{ result.title }}</template>
            </a>
          </template>
          <template v-else>
            <markdown-inline
              v-if="result.hasMarkdownTitle"
              :text="result.title"
            />
            <template v-else>{{ result.title }}</template>
          </template>

          <template v-if="result.path">
            <br />
            <span class="pathlink">
              Path:
              <router-link
                :to="{
                  name: 'file',
                  params: { path: result.path.split('/') },
                }"
                >files/{{ result.path }}</router-link
              >
            </span>
          </template>

          <pre
            v-show="showPreviews && result.preview"
            class="preview"
            v-html="result.preview"
          ></pre>
        </div>
      </b-list-group-item>
    </b-list-group>

    <p
      v-if="sortedResults.length < results.length"
      class="font-sm mt-2 text-center"
    >
      {{ results.length - sortedResults.length }}
      of
      {{ results.length | pluralize("result") }}
      filtered out.
    </p>
  </loading-box>
</template>

<script>
export default {
  props: {
    query: { type: String, required: true },
  },

  data() {
    return {
      results: [],
      selectedTypes: [],
      showPreviews: true,
      typeOptions: [],
    };
  },

  computed: {
    apiUrl() {
      return "/api/search?q=" + this.query;
    },

    sortedResults() {
      const results = this.results.slice();
      results.sort((a, b) => {
        return b.weight - a.weight;
      });
      return results.filter((r) => {
        return this.selectedTypes.indexOf(r.type) !== -1;
      });
    },
  },

  methods: {
    getBadgeVariant(result) {
      if (result.type === "bookmark") {
        return "info";
      } else if (result.type === "journal") {
        return "dark";
      } else {
        return "secondary";
      }
    },

    onDataLoaded(data) {
      this.results = data;
      const typeOptionsMap = new Map();
      for (const result of this.results) {
        let count = typeOptionsMap.get(result.type);
        if (count === undefined) {
          count = 0;
        }
        typeOptionsMap.set(result.type, count + 1);
      }

      this.typeOptions = [];
      this.selectedTypes = [];
      for (const [key, value] of typeOptionsMap.entries()) {
        this.typeOptions.push({
          text: `${key} (${value})`,
          value: key,
        });
        this.selectedTypes.push(key);
      }
      this.typeOptions.sort((a, b) => {
        if (a.value < b.value) {
          return -1;
        }
        if (a.value > b.value) {
          return 1;
        }
        return 0;
      });
      this.loading = false;
    },
  },
};
</script>

<style scoped>
.pathlink {
  font-size: 0.8rem;
}

.result-index {
  display: inline-block;
  vertical-align: top;
  padding-right: 10px;
  opacity: 50%;
  width: 5%;
}

.result-body {
  display: inline-block;
  width: 94%;
}

.preview {
  font-size: 0.8rem;
  margin-top: 10px;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: whitesmoke;
  white-space: break-spaces;
}
</style>
