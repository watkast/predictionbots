# Mr. P — gate report

Updated 2026-10-31T17:46:15Z by `run-20261031T1549-41216655253` (last 7 days of data). Read-only recorder — it never places orders.
Kit and docs: `mrp/README.md` on the `mrp` branch. Per-window detail: `mrp/windows.csv`.

```
Traceback (most recent call last):
  File "/home/runner/work/predictionbots/predictionbots/mrp/mrp_analyze.py", line 411, in <module>
    main()
  File "/home/runner/work/predictionbots/predictionbots/mrp/mrp_analyze.py", line 164, in main
    for r in load(args.data_dir, args.days):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/predictionbots/predictionbots/mrp/mrp_analyze.py", line 93, in load
    for line in fh:
                ^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/gzip.py", line 351, in read1
    return self._buffer.read1(size)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/_compression.py", line 68, in readinto
    data = self.read(len(byte_view))
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/gzip.py", line 551, in read
    buf = self._fp.read(READ_BUFFER_SIZE)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.12.15/x64/lib/python3.12/gzip.py", line 95, in read
    return self.file.read(size)
           ^^^^^^^^^^^^^^^^^^^^
MemoryError
(report skipped: analyzer over memory or time budget)
```
