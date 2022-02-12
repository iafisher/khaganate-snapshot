<template>
  <div class="page-wide">
    <template v-if="loading">
      <div class="text-center">
        <b-spinner />
      </div>
    </template>
    <!-- We use v-show here and below because we need to make sure that the
         <textarea> is created as soon as the Vue instance is mounted, so that
         we can hook in the Textcomplete library. -->
    <div v-show="!loading">
      <h2 class="path">
        <b-icon
          class="finish-button"
          icon="check-circle"
          @click="onFinish"
        ></b-icon>
        <linked-path :path="pathAsString" />
      </h2>
      <b-alert v-if="error" show variant="danger">{{ error }}</b-alert>
      <div v-show="body">
        <p>
          <template v-if="edited">Unsaved changes.</template
          ><template v-else>All changes saved.</template>
        </p>
        <b-overlay :show="finishing">
          <b-form-textarea
            v-model="body"
            :rows="lineCount + 1"
          ></b-form-textarea>
        </b-overlay>
      </div>
    </div>
  </div>
</template>

<script>
import * as lodash from "lodash";

import LinkedPath from "./LinkedPath.vue";

export default {
  components: {
    LinkedPath,
  },
  props: {
    path: { type: [Array, String], required: true },
  },

  data() {
    return {
      body: "",
      lastSavedBody: "",
      error: false,
      finishing: false,
      loading: true,
      timeoutId: null,
    };
  },

  computed: {
    pathAsString() {
      return lodash.isString(this.path) ? this.path : this.path.join("/");
    },

    lineCount() {
      let n = 0;
      for (let i = 0; i < this.body.length; i++) {
        if (this.body[i] === "\n") {
          n++;
        }
      }
      return n;
    },

    edited() {
      return this.body !== this.lastSavedBody;
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

  mounted() {
    window.addEventListener("keydown", (event) => {
      if (
        event.ctrlKey &&
        String.fromCharCode(event.which).toLowerCase() === "s"
      ) {
        this.save(false);
        event.preventDefault();
      }
    });
  },

  methods: {
    fetchData() {
      this.loading = true;
      this.$apiGet("/api/files/get/" + this.pathAsString).then((file) => {
        this.loading = false;
        if (file.error) {
          this.error = "The file does not exist.";
        } else {
          if (file.isDirectory) {
            this.error = "Directories cannot be edited.";
          } else {
            this.body = file.body;
            this.lastSavedBody = this.body;
          }
        }
      });
    },

    save(redirect) {
      const payload = { path: this.pathAsString, body: this.body };
      this.$apiPost("/api/files/save", payload)
        .then((file) => {
          this.finishing = false;
          if (file.error) {
            this.error = `Could not save file: ${file.error}.`;
          } else {
            this.lastSavedBody = this.body;
            if (redirect) {
              this.$router.push({
                name: "file",
                params: { path: this.pathAsString },
              });
            }
          }
        })
        .catch(() => {
          this.error = "Could not save file.";
          this.finishing = false;
        });
    },

    onFinish() {
      if (this.edited) {
        this.finishing = true;
        this.save(true);
      } else {
        this.$router.push({
          name: "file",
          params: { path: this.pathAsString },
        });
      }
    },
  },
};
</script>

<style scoped>
.path {
  font-size: 1.2rem;
}

.finish-button {
  float: right;
  cursor: pointer;
}
</style>
