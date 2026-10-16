export async function api(path, method='GET', data) {
  let response;
  try {
    response = await fetch('/api'+path, {method, headers:{'Content-Type':'application/json'},
      ...(data===undefined?{}:{body:JSON.stringify(data)})});
  } catch { throw new Error('Unable to reach your workspace. Check the server connection and retry.'); }
  const raw = await response.text();
  let body;
  if ((response.headers.get('content-type')||'').includes('json')) {
    try { body=JSON.parse(raw); }
    catch { throw new Error('The server returned an unreadable response. Please retry.'); }
  }
  if (!response.ok) {
    const message=typeof body?.detail==='string'?body.detail:
      raw && !raw.trim().startsWith('<')?raw.slice(0,400):'The server could not complete this request. Please retry.';
    throw new Error(message);
  }
  if (body===undefined) throw new Error('The server returned an unexpected response. Please retry.');
  return body;
}
