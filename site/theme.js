/* Theme switch: System / Dark / Light, remembered per device in localStorage. The pre-paint snippet in <head> applies
   the saved choice before the first render so there is no flash; this file only wires the control. */
(function () {
  var KEY = 'pb-theme', root = document.documentElement;
  function apply(v) { if (v === 'dark' || v === 'light') root.setAttribute('data-theme', v); else root.removeAttribute('data-theme'); }
  function saved() { try { return localStorage.getItem(KEY) || 'system'; } catch (e) { return 'system'; } }
  var box = document.getElementById('theme');
  if (!box) return;
  var cur = saved();
  box.querySelectorAll('input[name=theme]').forEach(function (r) {
    r.checked = r.value === cur;
    r.addEventListener('change', function () { if (!r.checked) return; apply(r.value); try { if (r.value === 'system') localStorage.removeItem(KEY); else localStorage.setItem(KEY, r.value); } catch (e) {} });
  });
})();
