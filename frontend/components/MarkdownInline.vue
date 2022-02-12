<template>
  <span v-html="getMarkdown()"></span>
</template>

<script>
import MarkdownIt from "markdown-it";

import { MARKDOWN_OPTIONS, preprocessMarkdown } from "common.js";

const md = MarkdownIt(MARKDOWN_OPTIONS);
export default {
  props: {
    text: { type: String, required: true },
  },

  computed: {
    preprocessedText() {
      return preprocessMarkdown(this.text);
    },
  },

  methods: {
    getMarkdown() {
      return md.renderInline(this.preprocessedText);
    },
  },
};
</script>
