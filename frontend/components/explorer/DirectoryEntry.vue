<template>
  <div>
    <b-row>
      <b-col v-for="(items, index) in columns" :key="index">
        <b-list-group>
          <b-list-group-item v-for="item in items" :key="item.path">
            <b-icon v-if="item.isDirectory" icon="folder-fill" variant="info" />
            <b-icon v-else icon="file-earmark" />
            <router-link
              :to="{ name: 'file', params: { path: item.path.split('/') } }"
            >
              {{ item.name }}
            </router-link>
          </b-list-group-item>
        </b-list-group>
      </b-col>
    </b-row>

    <p v-if="hiddenFileCount > 0" class="hidden-files-checkbox text-center">
      <b-form-checkbox v-model="showHidden">
        Show hidden files ({{ hiddenFileCount }})
      </b-form-checkbox>
    </p>
  </div>
</template>

<script>
export default {
  props: {
    files: { type: Array, required: true },
  },

  data() {
    return { showHidden: false };
  },

  computed: {
    columns() {
      const columns = [];
      const size = Math.ceil(this.filteredFiles.length / 4);
      columns.push(this.filteredFiles.slice(0, size));
      columns.push(this.filteredFiles.slice(size, size * 2));
      columns.push(this.filteredFiles.slice(size * 2, size * 3));
      columns.push(this.filteredFiles.slice(size * 3));
      return columns;
    },

    filteredFiles() {
      return this.files.filter(
        (file) => this.showHidden || !file.name.startsWith(".")
      );
    },

    hiddenFileCount() {
      let count = 0;
      for (const file of this.files) {
        if (file.name.startsWith(".")) {
          count++;
        }
      }
      return count;
    },
  },
};
</script>

<style scoped>
.hidden-files-checkbox {
  margin-top: 15px;
}
</style>
