# Mr. P — gate report

Updated 2026-10-31T16:11:24Z by `run-20261031T1549-41216655253` (last 7 days of data). Read-only recorder — it never places orders.
Kit and docs: `mrp/README.md` on the `mrp` branch. Per-window detail: `mrp/windows.csv`.

```
Traceback (most recent call last):
  File "/home/runner/work/predictionbots/predictionbots/mrp/mrp_analyze.py", line 411, in <module>
    main()
  File "/home/runner/work/predictionbots/predictionbots/mrp/mrp_analyze.py", line 164, in main
    for r in load(args.data_dir, args.days):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/predictionbots/predictionbots/mrp/mrp_analyze.py", line 98, in load
    yield json.loads(line)
          ^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/json/decoder.py", line 338, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/json/decoder.py", line 354, in raw_decode
    obj, end = self.scan_once(s, idx)
               ^^^^^^^^^^^^^^^^^^^^^^
MemoryError
(report skipped: analyzer over memory or time budget)
```
