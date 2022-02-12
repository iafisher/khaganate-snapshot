<template>
  <loading-box
    class="page-very-wide"
    :url="apiUrl"
    @data-loaded="diff = $event"
  >
    <div v-if="diff !== ''" v-html="diffHtml" />
    <p v-else class="text-center">
      No staged changes were found. Are there changes which are unstaged?
    </p>
  </loading-box>
</template>

<script>
import * as Diff2Html from "diff2html";
import * as lodash from "lodash";
import "diff2html/bundles/css/diff2html.min.css";

export default {
  props: {
    path: { type: [Array, String], required: false, default: "" },
  },

  data() {
    return { diff: "" };
  },

  computed: {
    apiUrl() {
      return "/api/git/diff/" + this.path;
    },

    diffHtml() {
      if (this.diff === "") {
        return "";
      }

      return Diff2Html.html(this.diff, {
        drawFileList: true,
        matching: "lines",
        outputFormat: "side-by-side",
      });
    },

    pathAsString() {
      return lodash.isString(this.path) ? this.path : this.path.join("/");
    },
  },
};
</script>
