"""The build's last two page-level guarantees: a page names the exact version of our CSS and JS it was built with,
and a markdown table scrolls inside itself on a phone."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "site" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make(dist: Path):
    (dist / "vendor").mkdir(parents=True)
    (dist / "markets" / "kalshi" / "x").mkdir(parents=True)
    (dist / "styles.css").write_text("body{}")
    (dist / "theme.js").write_text("1")
    (dist / "vendor" / "d3.v7.9.0.min.js").write_text("d3")
    page = ('<link href="https://fonts.googleapis.com/css2?family=X" rel="stylesheet"><link rel="stylesheet" href="/styles.css">'
            '<script src="/vendor/d3.v7.9.0.min.js"></script><script src="/theme.js" defer></script><a href="/styles.css.html">x</a>')
    (dist / "index.html").write_text(page)
    (dist / "markets" / "kalshi" / "x" / "index.html").write_text(page)


def test_every_page_names_the_version_of_our_css_and_js(tmp_path):
    S = load("stamp_assets")
    make(tmp_path)
    changed, assets = S.stamp(tmp_path)
    assert changed == 2 and set(assets) == {"styles.css", "theme.js"}
    for page in (tmp_path / "index.html", tmp_path / "markets" / "kalshi" / "x" / "index.html"):
        t = page.read_text()
        assert f'href="/styles.css?v={assets["styles.css"]}"' in t and f'src="/theme.js?v={assets["theme.js"]}"' in t
        assert 'src="/vendor/d3.v7.9.0.min.js"' in t and "fonts.googleapis.com/css2?family=X" in t and 'href="/styles.css.html"' in t
    assert S.main(["x", str(tmp_path)]) == 0
    assert S.stamp(tmp_path)[0] == 0                                   # a second run changes nothing


def test_a_changed_stylesheet_gets_a_new_address(tmp_path):
    S = load("stamp_assets")
    make(tmp_path)
    first = S.stamp(tmp_path)[1]["styles.css"]
    (tmp_path / "styles.css").write_text("body{color:red}")
    changed, assets = S.stamp(tmp_path)
    assert assets["styles.css"] != first and changed == 2
    assert f'/styles.css?v={assets["styles.css"]}"' in (tmp_path / "index.html").read_text()
    assert first not in (tmp_path / "index.html").read_text()


def test_markdown_tables_get_a_scrolling_wrapper_with_a_name_of_their_own():
    B = load("build")
    out = B.wrap_tables("<p>a</p><table><tr><td>1</td></tr></table><p>b</p><table><tr><td>2</td></tr></table>")
    assert out.count('<div class="ledger-wrap" tabindex="0" role="region"') == 2 and out.count("</table></div>") == 2
    assert 'aria-label="Table 1 (' in out and 'aria-label="Table 2 (' in out


def test_every_built_page_names_its_one_address(tmp_path):
    B = load("build")
    (tmp_path / "posts").mkdir(); (tmp_path / "markets" / "kalshi" / "x").mkdir(parents=True); (tmp_path / "ledger").mkdir()
    head = "<html><head><title>t</title></head><body></body></html>"
    for rel in ("index.html", "simulate.html", "posts/a.html", "ledger/index.html"):
        (tmp_path / rel).write_text(head)
    (tmp_path / "markets" / "kalshi" / "x" / "index.html").write_text('<head><link rel="canonical" href="https://predictmenot.com/markets/kalshi/x/"></head>')
    (tmp_path / "markets" / "index.html").write_text(head)          # the market pages are written by their own generator
    assert B.add_canonical(tmp_path) == 4
    assert '<link rel="canonical" href="https://predictmenot.com/"></head>' in (tmp_path / "index.html").read_text()
    assert 'href="https://predictmenot.com/posts/a.html"' in (tmp_path / "posts" / "a.html").read_text()
    assert 'href="https://predictmenot.com/ledger/"' in (tmp_path / "ledger" / "index.html").read_text()
    assert "canonical" not in (tmp_path / "markets" / "index.html").read_text()
    assert B.add_canonical(tmp_path) == 0                             # a second run adds nothing
