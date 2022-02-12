<template>
  <loading-box
    class="page-wide"
    :url="apiUrl"
    :refresh="refresh"
    @data-loaded="onDataLoaded"
  >
    <h1>
      Bibliography for <code>{{ topic }}</code>
    </h1>
    <p><router-link :to="parentLink">Go to parent</router-link>.</p>

    <h2>Bookmarks</h2>
    <template v-if="sortedBookmarks.length > 0">
      <b-form-radio-group
        v-model="selectedSort"
        class="mb-1"
        :options="sortOptions"
      ></b-form-radio-group>
      <ul class="bookmarks">
        <li v-for="bookmark in sortedBookmarks" :key="bookmark.id">
          <biblio-bookmark-entry
            :bookmark="bookmark"
            @bookmark-updated="refresh++"
          />
        </li>
      </ul>
    </template>
    <p v-else>No bookmarks for this topic.</p>

    <h2>Subtopics</h2>
    <ul v-if="sortedSubtopics.length > 0">
      <li v-for="subtopic in sortedSubtopics" :key="subtopic.id">
        <router-link
          :to="{ name: 'biblio-topic', params: { topic: subtopic.path } }"
        >
          {{ stripPrefix(subtopic.path) }}
        </router-link>
      </li>
    </ul>
    <p v-else>No subtopics for this topic.</p>
  </loading-box>
</template>

<script>
import * as lodash from "lodash";

import BiblioBookmarkEntry from "./BiblioBookmarkEntry.vue";

export default {
  components: {
    BiblioBookmarkEntry,
  },
  props: {
    topic: { type: String, required: true },
  },

  data() {
    return {
      bookmarks: [],
      subtopics: [],
      refresh: 0,

      // Sort options
      selectedSort: "default",
      sortOptions: [
        "default",
        "chronological",
        "reverse chronological",
        "annotated",
      ],
    };
  },

  computed: {
    apiUrl() {
      return `/api/bookmarks/topics/get/${this.topic}`;
    },

    parentLink() {
      const parts = this.topic.split("/");
      if (parts.length === 1) {
        return { name: "biblio-home" };
      } else {
        return {
          name: "biblio-topic",
          params: {
            topic: parts.slice(0, parts.length - 1).join("/"),
          },
        };
      }
    },

    sortedBookmarks() {
      if (this.selectedSort === "chronological") {
        return lodash.orderBy(this.bookmarks, ["createdAt"]);
      } else if (this.selectedSort === "reverse chronological") {
        return lodash.orderBy(this.bookmarks, ["createdAt"], ["desc"]);
      } else if (this.selectedSort === "annotated") {
        return lodash.orderBy(
          this.bookmarks,
          [(bookmark) => bookmark.annotation !== "", "createdAt"],
          ["desc", "asc"]
        );
      } else {
        return lodash.orderBy(
          this.bookmarks,
          ["quality", (bookmark) => bookmark.annotation !== "", "createdAt"],
          ["desc", "desc", "desc"]
        );
      }
    },

    sortedSubtopics() {
      return lodash.sortBy(this.subtopics, ["path"]);
    },
  },

  methods: {
    onDataLoaded(response) {
      this.bookmarks = response.bookmarks;
      this.subtopics = response.subtopics;
      document.title = `Biblio - ${this.topic} | Khaganate`;
    },

    stripPrefix(subtopic) {
      return subtopic.slice(this.topic.length + 1);
    },
  },
};
</script>

<style scoped>
.bookmarks {
  list-style-type: none;
}

.bookmarks li {
  position: relative;
}
</style>
