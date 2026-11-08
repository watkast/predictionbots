/* The Floor widget. Put <div data-floor data-kind="post" data-key="2026-11-08-free-money-that-wasnt" data-title="…"></div> on a
   page and this renders the two-sided thread: tally bar, Defend and Deviate columns, votes, report, and a post form.
   Reading needs nothing. Posting needs a session: Clerk when window.PB_CLERK_PK is set (one tap: Google, Apple, email
   link); in development a ?devuser=name query parameter is sent as x-dev-user. */
(function () {
  var hosts = document.querySelectorAll('[data-floor]');
  if (!hosts.length) return;
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); };
  var devUser = (new URLSearchParams(location.search)).get('devuser');
  var clerkReady = null;
  function clerk() {
    if (!window.PB_CLERK_PK || !window.PB_CLERK_FAPI) return Promise.resolve(null);
    if (clerkReady) return clerkReady;
    clerkReady = new Promise(function (resolve) {
      var s = document.createElement('script');
      s.src = 'https://' + window.PB_CLERK_FAPI + '/npm/@clerk/clerk-js@5/dist/clerk.browser.js'; s.async = true; s.crossOrigin = 'anonymous';
      s.setAttribute('data-clerk-publishable-key', window.PB_CLERK_PK);
      s.onload = function () { window.Clerk.load().then(function () { resolve(window.Clerk); }, function () { resolve(null); }); };
      s.onerror = function () { resolve(null); };
      document.head.appendChild(s);
    });
    return clerkReady;
  }
  function authHeaders() {
    if (devUser) return Promise.resolve({ 'x-dev-user': devUser });
    return clerk().then(function (C) {
      if (!C) return null;
      if (!C.session) { C.openSignIn(); return null; }
      return C.session.getToken().then(function (t) { return t ? { Authorization: 'Bearer ' + t } : null; });
    });
  }
  function api(method, path, body, headers) {
    return fetch('/api/floor/' + path, { method: method, headers: Object.assign({ 'Content-Type': 'application/json' }, headers || {}), body: body ? JSON.stringify(body) : undefined })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || 'Something went wrong.'); return j; }); });
  }
  function render(host, data) {
    var kind = host.dataset.kind, key = host.dataset.key, title = host.dataset.title || key;
    var t = data.tally || { defend: 0, deviate: 0 }, total = (t.defend + t.deviate) || 1;
    var col = function (side, label, note, color) {
      var ps = (data.posts || []).filter(function (p) { return p.side === side; });
      return '<section class="floor-col"><h3 style="color:' + color + ';margin:0 0 8px">' + label + ' <span class="q-where">' + note + '</span></h3>' +
        (ps.map(function (p) { return '<article class="floor-post" data-id="' + p.id + '" style="border-left-color:' + color + '"><div class="q-where"><b>' + esc(p.handle) + '</b>' + (p.badge ? ' <span class="badge">' + esc(p.badge) + '</span>' : '') + ' · ' + esc(String(p.created).slice(0, 10)) + ' · <button type="button" class="linkish" data-vote="' + p.id + '" aria-label="Agree with this post">▲ ' + p.votes + '</button> · <button type="button" class="linkish" data-report="' + p.id + '">report</button></div><p>' + esc(p.body).replace(/\n/g, '<br>') + '</p>' + (p.data_url ? '<div class="q-where">Data: <a href="' + esc(p.data_url) + '" rel="noopener nofollow">' + esc(p.data_url) + '</a> (counts double)</div>' : '') + '</article>'; }).join('') || '<p class="q-where">No posts yet. Be the first to ' + label.toLowerCase() + '.</p>') + '</section>';
    };
    host.innerHTML = '<div class="floor-head"><h2 style="margin:0">The Floor: deviants vs defenders</h2><a class="q-where" href="/floor/' + esc(kind) + '/' + esc(key) + '">permalink</a></div>' +
      '<p class="q-where" style="margin:4px 0 10px">' + esc(title) + '. Defenders argue it holds; deviants argue it doesn\'t. Posts with a data file count double. Read free; post with one tap.</p>' +
      '<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px"><b style="color:var(--win)">Defend ' + t.defend + '</b><div class="bar" style="flex:1" aria-hidden="true"><i style="width:' + Math.round(t.defend / total * 100) + '%;background:var(--win)"></i><i style="width:' + Math.round(t.deviate / total * 100) + '%;background:var(--loss)"></i></div><b style="color:var(--loss)">Deviate ' + t.deviate + '</b></div>' +
      '<div class="floor">' + col('defend', 'Defend', 'it holds, or close', 'var(--win)') + col('deviate', 'Deviate', "it doesn't, and here's why", 'var(--loss)') + '</div>' +
      '<form class="floor-form"><label>Your case<textarea name="body" maxlength="2000" rows="3" placeholder="Numbers travel; adjectives don\'t."></textarea></label><label>Link to a data file (optional, counts double)<input name="data_url" type="url" placeholder="https://"></label>' +
      '<div class="sim-actions"><button type="submit" class="btn" data-side="defend" style="border-color:var(--win);color:var(--win)">Post as Defend</button><button type="submit" class="btn" data-side="deviate" style="border-color:var(--loss);color:var(--loss)">Post as Deviate</button><span class="q-where floor-msg" aria-live="polite"></span></div>' +
      '<p class="fine" style="margin-top:8px">House rules: patterns and public records, never a private person\'s name without a court or exchange filing; vendors wear a badge; no referral links. Posts are public and indexed.</p></form>';
    var form = host.querySelector('form'), msg = host.querySelector('.floor-msg'), side = null;
    host.querySelectorAll('button[data-side]').forEach(function (b) { b.addEventListener('click', function () { side = b.dataset.side; }); });
    form.addEventListener('submit', function (e) {
      e.preventDefault(); msg.textContent = '';
      var body = form.body.value.trim(), data_url = form.data_url.value.trim();
      if (!body) { msg.textContent = 'Write something first.'; return; }
      authHeaders().then(function (h) {
        if (!h) { msg.textContent = window.PB_CLERK_PK ? 'Sign in (one tap) to post.' : 'Sign-in is being set up; the Floor is read-only for a few days.'; return; }
        return api('POST', kind + '/' + key, { side: side, body: body, data_url: data_url, title: title }, h).then(function () { return load(host); }).then(function () { msg.textContent = 'Posted.'; });
      }).catch(function (err) { msg.textContent = err.message; });
    });
    host.querySelectorAll('[data-vote]').forEach(function (b) { b.addEventListener('click', function () { authHeaders().then(function (h) { if (!h) { msg.textContent = 'Sign in to agree.'; return; } return api('POST', 'vote', { post_id: Number(b.dataset.vote) }, h).then(function (j) { b.textContent = '▲ ' + j.votes; }); }).catch(function (err) { msg.textContent = err.message; }); }); });
    host.querySelectorAll('[data-report]').forEach(function (b) { b.addEventListener('click', function () { authHeaders().then(function (h) { if (!h) { msg.textContent = 'Sign in to report.'; return; } return api('POST', 'report', { post_id: Number(b.dataset.report) }, h).then(function (j) { msg.textContent = j.message; }); }).catch(function (err) { msg.textContent = err.message; }); }); });
  }
  function load(host) {
    return fetch('/api/floor/' + host.dataset.kind + '/' + host.dataset.key, { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : { posts: [], tally: { defend: 0, deviate: 0 } }; })
      .catch(function () { return { posts: [], tally: { defend: 0, deviate: 0 }, offline: true }; })
      .then(function (d) { render(host, d); });
  }
  hosts.forEach(load);
})();
