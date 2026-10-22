// Cloudflare Worker in front of the static files: answers byte-range requests for the films
// (Safari only plays video that can be fetched in ranges); everything else is served as is.
// The asset store sends no Content-Length, so build_pages.py writes the film sizes to sizes.json.
import SIZES from './sizes.json';

export default {
  async fetch(request, env) {
    const res = await env.ASSETS.fetch(request);
    const m = /^bytes=(\d*)-(\d*)$/.exec(request.headers.get('Range') || '');
    const size = SIZES[new URL(request.url).pathname];
    if (!m || !size || res.status !== 200 || !res.body) return res;
    let start = m[1] === '' ? size - Number(m[2]) : Number(m[1]);
    let end = m[1] === '' || m[2] === '' ? size - 1 : Math.min(Number(m[2]), size - 1);
    start = Math.max(0, start);
    const headers = new Headers(res.headers);
    headers.set('Accept-Ranges', 'bytes');
    if (start > end) {
      headers.set('Content-Range', `bytes */${size}`);
      return new Response(null, { status: 416, headers });
    }
    headers.set('Content-Range', `bytes ${start}-${end}/${size}`);
    headers.set('Content-Length', String(end - start + 1));
    return new Response(res.body.pipeThrough(slice(start, end + 1)), { status: 206, headers });
  },
};

// passes on only the bytes [from, to) of a stream
function slice(from, to) {
  let pos = 0;
  return new TransformStream({
    transform(chunk, ctrl) {
      const a = Math.max(from - pos, 0);
      const b = Math.min(to - pos, chunk.byteLength);
      if (b > a) ctrl.enqueue(chunk.subarray(a, b));
      pos += chunk.byteLength;
      if (pos >= to) ctrl.terminate();
    },
  });
}
