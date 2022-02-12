<template>
  <div ref="root" class="markdown" v-html="getMarkdown()"></div>
</template>

<script>
import MarkdownIt from "markdown-it";
import MarkdownItFootnote from "markdown-it-footnote";
import MarkdownItKatex from "markdown-it-katex";

import { MARKDOWN_OPTIONS, preprocessMarkdown } from "common.js";

const md = MarkdownIt(MARKDOWN_OPTIONS)
  .use(MarkdownItFootnote)
  .use(MarkdownItKatex);

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
      return md.render(this.preprocessedText);
    },
  },
};
</script>

<!-- These styles can't be scoped because of the use of `v-html`.
     See https://stackoverflow.com/questions/64066272/ for details. -->
<style>
.markdown img {
  width: 100%;
}

.markdown h1,
.markdown h2,
.markdown h3,
.markdown h4,
.markdown h5,
.markdown h6 {
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}

.markdown h1 {
  text-align: center;
  font-size: 2.5rem;
}

.markdown h2 {
  font-size: 2rem;
}

.markdown h3 {
  font-size: 1.5rem;
}

.markdown h4 {
  font-size: 1.25rem;
}

.markdown table {
  margin: 0 auto;
  margin-bottom: 1rem;
}

.markdown td {
  border: 1px solid black;
}

.markdown th,
.markdown td {
  padding: 5px;
}

.markdown th {
  padding-bottom: 1px;
  text-align: center;
}

.markdown blockquote {
  background-color: whitesmoke;
  border-left: 10px solid #ccc;
  padding: 0.5rem;
}

.markdown p:last-child {
  margin-bottom: 0;
}
</style>
