<template>
  <div :class="isDirectory ? 'page-very-wide' : 'page-wide'">
    <h2 v-if="!loading" class="path">
      <router-link
        v-if="!isDirectory && !isImage"
        class="edit-button"
        :to="{ name: 'edit-file', params: { path: pathAsArray } }"
      >
        <b-icon icon="pencil-fill"></b-icon>
      </router-link>
      <linked-path :path="pathAsString" />
      <template v-if="!isDirectory">
        @ <code>{{ revision || "HEAD" }}</code>
      </template>
    </h2>
    <details v-if="!isDirectory && revisions.length > 0">
      <summary>history</summary>
      <ul>
        <li><a href="?r=HEAD">HEAD</a></li>
        <li v-for="r in revisions" :key="r.hash">
          <span v-if="revision.startsWith(r.hash)">{{ r.dateTime }}</span>
          <a v-else :href="'?r=' + r.hash">{{ r.dateTime }}</a>
        </li>
      </ul>
    </details>
    <template v-if="loading">
      <div class="text-center">
        <b-spinner />
      </div>
    </template>
    <template v-else-if="error">
      <b-alert show variant="danger">The file does not exist.</b-alert>
    </template>
    <template v-else>
      <template v-if="isSpecial">
        <hr />
        <p class="text-center">
          <b-form-checkbox v-model="displayAsText">
            Display as text
          </b-form-checkbox>
        </p>
      </template>

      <template v-if="isDirectory">
        <directory-entry :files="files" />
      </template>
      <template v-else-if="!displayAsText && isCsv">
        <b-table striped hover outlined :fields="rowFields" :items="rows" />
      </template>
      <template v-else-if="isImage">
        <b-img fluid :src="'/api/files/raw/' + pathAsString" />
      </template>
      <template v-else-if="!displayAsText && isMarkdown">
        <div class="markdown">
          <markdown-block :text="body" />
        </div>
      </template>
      <template v-else>
        <plaintext-file :body="body" />
      </template>
    </template>
  </div>
</template>

<script>
import * as lodash from "lodash";

import DirectoryEntry from "./DirectoryEntry.vue";
import LinkedPath from "./LinkedPath.vue";
import PlaintextFile from "./PlaintextFile.vue";

export default {
  components: {
    DirectoryEntry,
    LinkedPath,
    PlaintextFile,
  },
  props: {
    path: { type: [Array, String], required: false, default: "" },
    revision: { type: String, required: false, default: "" },
  },

  data() {
    return {
      body: "",
      displayAsText: false,
      error: false,
      files: [],
      isCsv: false,
      isDirectory: false,
      loading: true,
      revisions: [],
      rows: [],
      rowFields: [],
      selectedSort: "default",
      sortOptions: ["default", "chronological", "reverse chronological"],
    };
  },

  computed: {
    pathAsString() {
      return lodash.isString(this.path) ? this.path : this.path.join("/");
    },

    pathAsArray() {
      return lodash.isArray(this.path) ? this.path : this.path.split("/");
    },

    isImage() {
      return /\.(jpg|jpeg|png|svg)$/.test(this.pathAsString);
    },

    isMarkdown() {
      return this.pathAsString.endsWith(".md");
    },

    isSpecial() {
      return this.isCsv || this.isMarkdown;
    },
  },

  watch: {
    $route() {
      this.fetchData();
    },
  },

  created() {
    this.fetchData();
  },

  methods: {
    fetchData() {
      this.error = false;

      if (this.isImage) {
        this.isCsv = false;
        this.isDirectory = false;
        return;
      }

      const queryString = this.revision ? `?r=${this.revision}` : "";
      this.loading = true;
      this.$apiGet("/api/files/get/" + this.pathAsString + queryString).then(
        (file) => {
          this.loading = false;
          if (file.error) {
            this.error = true;
          } else {
            if (file.isDirectory) {
              this.isCsv = false;
              this.isDirectory = true;
              this.files = file.files;
            } else {
              this.isDirectory = false;
              this.body = file.body;
              this.revisions = file.revisions;
              if (file.isCsv) {
                this.isCsv = true;
                this.rows = file.rows;
                this.rowFields = file.fields;
              } else {
                this.isCsv = false;
              }
            }
          }
        }
      );
    },
  },
};
</script>

<style scoped>
.path {
  font-size: 1.2rem;
}

.edit-button {
  float: right;
  cursor: pointer;
}

details {
  border: 1px solid #ccc;
  border-radius: 4px;
  background: whitesmoke;
  padding: 0.5em;
}

details summary {
  text-align: center;
}
</style>
