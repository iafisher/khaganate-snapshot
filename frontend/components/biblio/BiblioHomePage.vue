<template>
  <loading-box
    class="page-wide"
    url="/api/db/list/bookmark-topics"
    @data-loaded="topics = $event"
  >
    <h1>Bibliography topics</h1>
    <p>
      <b-input
        v-model="searchFilter"
        placeholder="Search (enter at least 3 characters)"
      />
    </p>
    <ul>
      <li v-for="topicGroup in topicGroups" :key="topicGroup.directory">
        <router-link
          :to="{
            name: 'biblio-topic',
            params: { topic: topicGroup.directory },
          }"
        >
          {{ topicGroup.directory }}
        </router-link>
        <template v-if="topicGroup.topics.length > 0 && !searchActive">
          <b-icon
            v-if="isExpanded(topicGroup)"
            icon="caret-right"
            @click="collapseTopicGroup(topicGroup)"
          ></b-icon>
          <b-icon
            v-else
            icon="caret-down"
            @click="expandTopicGroup(topicGroup)"
          ></b-icon>
        </template>

        <ul v-if="topicGroup.topics.length > 0 && isExpanded(topicGroup)">
          <li v-for="topic in topicGroup.topics" :key="topic.id">
            <router-link
              :to="{
                name: 'biblio-topic',
                params: { topic: topic.path },
              }"
            >
              {{ topic.subpath }}
            </router-link>
          </li>
        </ul>
      </li>
    </ul>
  </loading-box>
</template>

<script>
import * as lodash from "lodash";

export default {
  data() {
    return {
      expandedTopicGroups: [],
      searchFilter: "",
      topics: [],
    };
  },

  computed: {
    filteredTopics() {
      if (this.searchActive) {
        const q = this.searchFilter.toLowerCase();
        return this.topics.filter((topic) =>
          topic.path.toLowerCase().includes(q)
        );
      } else {
        return this.topics;
      }
    },

    searchActive() {
      return this.searchFilter.length >= 3;
    },

    topicGroups() {
      const topicGroupMap = new Map();
      for (const topic of lodash.orderBy(this.filteredTopics, ["path"])) {
        const parts = topic.path.split("/");
        const directory = parts[0];
        if (!topicGroupMap.has(directory)) {
          topicGroupMap.set(directory, []);
        }

        if (parts.length > 1) {
          const subpath = parts.slice(1).join("/");
          topicGroupMap.get(directory).push({ subpath, ...topic });
        }
      }

      const topicGroups = [];
      for (const [directory, topics] of topicGroupMap.entries()) {
        topicGroups.push({ directory, topics });
      }
      return lodash.orderBy(topicGroups, ["directory"]);
    },
  },

  methods: {
    collapseTopicGroup(topicGroup) {
      const index = this.expandedTopicGroups.indexOf(topicGroup.directory);
      if (index !== -1) {
        this.expandedTopicGroups.splice(index, 1);
      }
    },

    expandTopicGroup(topicGroup) {
      this.expandedTopicGroups.push(topicGroup.directory);
    },

    isExpanded(topicGroup) {
      return (
        this.searchActive ||
        this.expandedTopicGroups.includes(topicGroup.directory)
      );
    },
  },
};
</script>

<style scoped>
.b-icon {
  cursor: pointer;
}
</style>
