import { bundle } from "@remotion/bundler";
import { selectComposition, renderMedia } from "@remotion/renderer";
import { readFile, writeFile } from "fs/promises";
import { createReadStream } from "fs";
import { fileURLToPath } from "url";
import { dirname, join, resolve } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));

const [,, schemaPath, outputPath, uploadUrl] = process.argv;

if (!schemaPath || !outputPath) {
  console.error(JSON.stringify({ error: "Usage: node render.mjs <schema_json_path> <output_mp4_path> [upload_url]" }));
  process.exit(1);
}

async function main() {
  const schemaJson = await readFile(resolve(schemaPath), "utf-8");
  const schema = JSON.parse(schemaJson);

  process.stdout.write(JSON.stringify({ status: "bundling" }) + "\n");
  const bundleLocation = await bundle({
    entryPoint: join(__dirname, "src/index.ts"),
    webpackOverride: (config) => config,
  });

  process.stdout.write(JSON.stringify({ status: "selecting_composition" }) + "\n");
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: "PipelineAComposition",
    inputProps: { schema },
  });

  process.stdout.write(JSON.stringify({ status: "rendering", total_frames: composition.durationInFrames }) + "\n");
  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: "h264",
    outputLocation: resolve(outputPath),
    inputProps: { schema },
    onProgress: ({ progress }) => {
      process.stdout.write(JSON.stringify({ progress: Math.round(progress * 100) }) + "\n");
    },
  });

  let video_url = outputPath;
  if (uploadUrl) {
    const fileData = await readFile(resolve(outputPath));
    const protocol = uploadUrl.startsWith("https") ? (await import("https")).default : (await import("http")).default;
    await new Promise((resolve_p, reject) => {
      const url = new URL(uploadUrl);
      const req = protocol.request({
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: "PUT",
        headers: { "Content-Type": "video/mp4", "Content-Length": fileData.length },
      }, (res) => {
        if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) resolve_p(undefined);
        else reject(new Error(`Upload failed: ${res.statusCode}`));
      });
      req.on("error", reject);
      req.write(fileData);
      req.end();
    });
    video_url = uploadUrl.split("?")[0];
  }

  process.stdout.write(JSON.stringify({ done: true, video_path: resolve(outputPath), video_url }) + "\n");
}

main().catch((err) => {
  process.stderr.write(JSON.stringify({ error: String(err) }) + "\n");
  process.exit(1);
});
