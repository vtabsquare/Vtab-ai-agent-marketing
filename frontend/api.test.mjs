import {test} from 'node:test';
import assert from 'node:assert/strict';
import {api} from './src/api.js';
test('plain text 500 becomes a useful error',async()=>{
  global.fetch=async()=>new Response('Internal Server Error',{status:500,headers:{'content-type':'text/plain'}});
  await assert.rejects(api('/test'),/Internal Server Error/);
});
test('HTML error page is not displayed as markup',async()=>{
  global.fetch=async()=>new Response('<html>proxy error</html>',{status:502});
  await assert.rejects(api('/test'),/server could not complete/);
});
test('malformed JSON is handled',async()=>{
  global.fetch=async()=>new Response('{broken',{headers:{'content-type':'application/json'}});
  await assert.rejects(api('/test'),/unreadable/);
});
test('structured success is returned',async()=>{
  global.fetch=async()=>new Response('{"ok":true}',{headers:{'content-type':'application/json'}});
  assert.deepEqual(await api('/test'),{ok:true});
});
