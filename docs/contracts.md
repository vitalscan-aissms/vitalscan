# Data contracts between modules

These two formats are the only places where one person's code meets another's.
Change them only through a PR that Sidd approves, and update the fixtures in the same PR.

## Contract 1: RGB traces (M3 `roi` → M5 `rppg`)

Saved as a compressed NumPy file (`np.savez_compressed`) with these arrays:

| Key | Shape / type | Meaning |
| --- | --- | --- |
| `traces` | `(N, 3, 3)` float32 | Mean colour per frame, per ROI, per channel. Axis 1 = ROI in order `[forehead, left_cheek, right_cheek]`. Axis 2 = channel in order `[R, G, B]` (RGB, not OpenCV's BGR). Values 0–255. |
| `timestamps` | `(N,)` float64 | Real capture time of each frame in seconds from the start of the clip (not assumed from fps). |
| `valid` | `(N, 3)` bool | False where a ROI had too few skin pixels or no single face was found. Downstream code must ignore or interpolate these. |
| `roi_names` | `(3,)` str | `["forehead", "left_cheek", "right_cheek"]` |
| `source_fps` | scalar float | Nominal fps from the container, for information only. |

## Contract 2: Scan result JSON (M10 `pipeline` → M11 `api`, M12 `db`, M13 `reports`, M14 `frontend`)

See the full example in `backend/tests/fixtures/mock_result.json`. Rules:

- `label` is always one of `"measured"`, `"estimated"`, `"experimental"`, `"calculated"`.
- `vitals` has three shapes:

  | Key | Shape | Fields |
  | --- | --- | --- |
  | `hr`, `rr` | one vital object | `value`, `unit`, `confidence` (0–1), `label`, `method` |
  | `hrv` | group of vital objects `sdnn`, `rmssd`, `pnn50` | each has the five fields above; `label` is always `"experimental"` |
  | `bp` | one estimate with two values | `sbp` and `dbp` (each only `value` + `unit`), plus shared `error_band_mmhg`, `confidence`, `label`, `method` for the pair |

- `bp` always has `label: "experimental"` and an `error_band_mmhg` (SBP and DBP come from one
  model run, so they share one confidence and one error band).
- Derived metrics (`derived.*`) carry `value`, `unit`, `label: "calculated"` and the `formula`
  text that produced them; they have no `confidence` of their own.
- If quality fails: `status: "rejected"`, `vitals` is `null`, and `quality.messages` explains how to retry.
- `disclaimer` is always present and must be shown wherever results are shown.
- `schema_version` increases on any breaking change.
