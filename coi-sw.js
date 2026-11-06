// 楽曲アナライザ：クロスオリジン分離（crossOriginIsolated）のための Service Worker。
// GitHub Pages などヘッダーを設定できない場所でも、同じオリジンのページとスクリプトへの応答に
// COOP / COEP を付けて分離された状態にする。分離されると SharedArrayBuffer が使え、
// AI のパート分離（ONNX Runtime Web の WASM）を複数のスレッドで動かせる。
// 何もキャッシュせず、応答の中身も変えない（ヘッダーを足すだけ）。外部（別オリジン）への通信には触れない。
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (e) => {
  const r = e.request;
  if (r.cache === "only-if-cached" && r.mode !== "same-origin") return;
  if (new URL(r.url).origin !== self.location.origin) return;
  e.respondWith(
    fetch(r).then((res) => {
      if (res.status === 0) return res;
      const h = new Headers(res.headers);
      h.set("Cross-Origin-Opener-Policy", "same-origin");
      h.set("Cross-Origin-Embedder-Policy", "require-corp");
      h.set("Cross-Origin-Resource-Policy", "same-origin");
      return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
    })
  );
});
