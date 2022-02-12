<template>
  <span>
    <!-- There can't be any extra whitespace emitted in this loop, to ensure
         that the correct file path can be selected and copy-pasted. -->
    <template v-if="path !== ''"
      ><router-link class="pathlink" :to="{ name: 'file-home' }"
        >files</router-link
      ></template
    ><template v-else>files</template
    ><span v-for="part in parts" :key="part.cumulative.join('/')"
      ><span class="slash">/</span
      ><router-link
        v-if="part.cumulative.length > 0"
        class="pathlink"
        :to="{ name: 'file', params: { path: part.cumulative } }"
        >{{ part.part }}</router-link
      ><template v-else>{{ part.part }}</template></span
    >
  </span>
</template>

<script>
export default {
  props: {
    path: { type: String, required: true },
  },

  computed: {
    parts() {
      const parts = [];
      let index = 0;
      while (true) {
        const nextIndex = this.path.indexOf("/", index);
        if (nextIndex === -1) {
          parts.push({ part: this.path.slice(index), cumulative: [] });
          break;
        } else {
          const cumulative = this.path.slice(0, nextIndex).split("/");
          parts.push({ part: this.path.slice(index, nextIndex), cumulative });
          index = nextIndex + 1;
        }
      }
      return parts;
    },
  },
};
</script>

<style scoped>
.slash,
.pathlink {
  font-weight: normal;
}

.slash {
  opacity: 50%;
  margin-left: 2px;
  margin-right: 4px;
}
</style>
