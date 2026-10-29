import { createRequire } from 'node:module';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const modules = process.env.MARKETING_BUILD_MODULES;
const esbuild = modules ? require(path.join(modules, 'esbuild')) : require('esbuild');
await mkdir(path.join(root, 'dist/assets'), {recursive: true});
await esbuild.build({entryPoints: [path.join(root, 'src/main.jsx')], bundle: true, minify: true,
  outdir: path.join(root, 'dist/assets'), entryNames: 'app', loader: {'.jsx':'jsx'},
  nodePaths: modules ? [modules] : [], define: {'process.env.NODE_ENV': '"production"'}});
const cssFiles=['styles.css','modern.css','control.css','community.css','pilot-demo-end.css'];
const css=(await Promise.all(cssFiles.map(name=>readFile(path.join(root,'src',name),'utf8')))).join('\n');
await writeFile(path.join(root,'dist/assets/app.css'),css);
const v = Date.now().toString(36);
await writeFile(path.join(root, 'dist/index.html'), `<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Marketing Manager</title><link rel="stylesheet" href="/assets/app.css?v=${v}"></head><body><div id="root"></div><script type="module" src="/assets/app.js?v=${v}"></script></body></html>`);
console.log('Dashboard built with cache busting. Version:', v);
