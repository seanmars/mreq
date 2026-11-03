// Render each Mermaid source with the page's own Pele bundle, so the build sees the errors the browser would show.
// Usage: node check.mjs <pele.global.js>, with a JSON list of sources on stdin.
// Prints a JSON list: { "ok": true, "type", "width" } or { "ok": false, "code", "message", "line", "column" }.
import fs from 'node:fs';
import vm from 'node:vm';

const context = vm.createContext({});
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), context);
const pele = context.pele;

const sources = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = sources.map((source, index) => {
  try {
    // The page's LIMITS (skeleton.html): Pele's defaults are smaller than a large diagram can be.
    const result = pele.render(source, { idPrefix: `d${index}`, limit: 1_000_000, outputLimit: 8_000_000, maxEdges: 10_000 });
    return { ok: true, type: result.type, width: result.width };
  } catch (error) {
    return {
      ok: false,
      code: error.code || 'error',
      message: String(error.message || error),
      line: error.line || 0,
      column: error.column || 0,
    };
  }
});
process.stdout.write(JSON.stringify(results));
