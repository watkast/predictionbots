import glob, yaml

def test_workflows_parse_and_are_paper_only():
    files = glob.glob(".github/workflows/*.yml")
    assert len(files) >= 4
    for f in files:
        d = yaml.safe_load(open(f))
        assert "jobs" in d and (True in d or "on" in d), f
        txt = open(f).read()
        assert "LIVE_TRADING" not in txt, f
