<template>
  <div class="root">
    <div class="line-numbers">
      <pre v-for="i in lines.length" :key="i">{{ i }}</pre>
    </div>

    <div class="body">
      <pre><code>{{ body }}</code></pre>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    body: { type: String, required: true },
  },

  computed: {
    lines() {
      const trimmed = this.body.endsWith("\n")
        ? this.body.slice(0, this.body.length - 1)
        : this.body;
      return trimmed.split("\n");
    },
  },
};
</script>

<style scoped>
.root {
  width: 100%;
  background-color: whitesmoke;
  padding: 10px;
}

.line-numbers,
.body {
  display: inline-block;
}

.line-numbers {
  width: 5%;
  padding-right: 5px;
  border-right: 1px solid black;
  text-align: right;
  vertical-align: top;
}

.body {
  width: 94%;
  padding-left: 10px;
  overflow-x: scroll;
}

.line-numbers pre,
.body pre {
  margin-bottom: 0;
  overflow: visible;
}

.line-numbers pre {
  color: gray;
}
</style>
