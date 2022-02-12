const vuePlugin = require("esbuild-vue");

const mode = process.argv[2];
const isDevMode = mode === "dev" || mode === "watch";
const isWatchMode = mode === "watch";

require("esbuild")
  .build({
    nodePaths: ["frontend"],
    entryPoints: ["frontend/router.js"],
    bundle: true,
    minify: !isDevMode,
    outfile: "server/static/bundle/bundle.js",
    plugins: [vuePlugin()],
    sourcemap: isDevMode,
    watch: isWatchMode
      ? {
          onRebuild(error, result) {
            if (!error) {
              console.log(`[${Date.now()}] Watch build succeeded`);
            }
          },
        }
      : false,
  })
  .then(() => {
    if (isWatchMode) {
      console.log("Watching files for changes...");
    }
  })
  .catch(() => {
    process.exit(1);
  });
