# rPPG Vitals FYP — Master Build Plan

Oct 24, 2026 · @Siddhanth Waghmare

## 0. Reality check before we build

We build a real, deployed web system that measures heart rate and breathing rate reliably, and gives blood pressure as an **experimental estimate** — never as a clinical reading. That framing is what makes the project publishable and safe to put in front of real users.

| Output | How solid it is from a webcam | How we label it |
| --- | --- | --- |
| Heart rate (HR) | Strong. Good methods reach about 2–5 bpm error in decent light | "Measured (camera estimate)" |
| Respiratory rate (RR) | Moderate. Works when the person sits still | "Estimated" |
| HRV (SDNN, RMSSD) | Weak to moderate. Needs 60 s and clean peaks | "Experimental" |
| Blood pressure (SYS/DIA) | Weak. Published webcam BP errors are often 8–15 mmHg, worse on new people | "Experimental estimate — not a medical reading" |
| Derived metrics (BMI, MAP, VO2max, HR zones) | Exact formulas on the inputs above | "Calculated from formula X" |

- **Our research contribution** (from the earlier synopsis work): commercial face-scan reports such as the CarePlix/Glenmark BPIC report show 20+ "vitals", but most are standard formulas on just HR, BP, age, height and weight. Our system shows every formula and every confidence score openly. That transparency is the novelty.
- **Every screen and every PDF** carries the line: *For education and research only. Not a medical device. Confirm any reading with a certified BP monitor and a doctor.*
- **Real users means legal duties.** Facial video and health readings are personal data under India's Digital Personal Data Protection Act 2023, so we need explicit consent, a privacy policy, and deletion on request. Software that claims to diagnose BP can count as a medical device under CDSCO rules, so we never claim diagnosis — we claim research estimate.
- **Team change:** the synopsis assumed four people with four roles. We are now three, so the Frontend role is merged into the other three roles (section 3).

## 1. System architecture

The browser records a 30-second face clip and uploads it; the server runs the pipeline (M1–M13) on CPU and returns numbers plus a PDF; Colab trains the BP model offline and hands the server a single `model.onnx` file.

*(Architecture diagram: see the online version of this doc, https://claude.ai/artifact/Bmsp6bJ4QtnCGzDdiBzvZD)*

Read it top to bottom, snaking through the server: a clip that fails the quality gate stops at M4 and the user gets retry tips (more light, keep still) instead of numbers. The highlighted BP box is the only experimental output, and the only part that depends on Colab.

## 2. Module breakdown

The system splits into 15 modules. Each one is a Python package (or a frontend folder) with one clear input and one clear output, so three people can build them in parallel and test them alone.

| # | Module | What it does | Input → Output | Owner | Difficulty | Runs on |
| --- | --- | --- | --- | --- | --- | --- |
| M1 | `video_io` | Decodes the uploaded clip, fixes the frame rate, drops corrupt frames | .webm/.mp4 file → frames + timestamps | Member 2 | Easy | Laptop |
| M2 | `face_detection` | MediaPipe Face Landmarker (478 points); rejects 0 or 2+ faces | frame → landmarks | Member 2 | Medium | Laptop |
| M3 | `roi` | Builds forehead + left/right cheek polygons from landmarks, applies a skin mask, averages R,G,B per frame | frames + landmarks → RGB traces (3 ROIs × 3 channels × N frames) | Member 2 | Medium | Laptop |
| M4 | `quality` | Scores lighting (brightness, clipping), head motion (landmark drift), face-lost frames, blur | frames + landmarks → quality report + pass/fail | Member 2 | Medium | Laptop |
| M5 | `rppg` | GREEN, CHROM and POS methods turn RGB traces into one pulse wave | RGB traces → pulse signal | Sidd | Hard | Laptop |
| M6 | `signal_processing` | Detrend, band-pass 0.7–4 Hz, FFT, peak detection, SNR | raw pulse → clean pulse + peaks + SNR | Sidd | Hard | Laptop |
| M7 | `vitals` | HR (FFT + peaks), RR (0.1–0.5 Hz band), HRV (SDNN, RMSSD, pNN50), confidence score | clean pulse → HR, RR, HRV + confidence | Sidd | Hard | Laptop |
| M8 | `ml_models` (BP model) | Pulse-shape features (rise time, width, area ratios, HR, HRV) + age/sex/BMI → SYS/DIA estimate | features → BP estimate + error band | Member 2 | Hard | Colab (train), laptop (run ONNX) |
| M9 | `derived` | Exact formulas: BMI, MAP, HR max, HR reserve, Karvonen zones, VO2max (Uth–Sørensen) | vitals + profile → derived metrics + the formula used | Member 3 | Easy | Laptop |
| M10 | `pipeline` | Runs M1→M9 in order, stops early with a clear error if quality fails | video + profile → one result JSON | Sidd | Medium | Laptop |
| M11 | `api` | FastAPI routes: sign-up/login, upload scan, get result, get report, delete my data | HTTP → JSON / PDF | Member 3 | Medium | Laptop / server |
| M12 | `db` | SQLAlchemy models + Alembic migrations (users, scans, measurements, reports) | Python objects → SQLite (dev) / PostgreSQL (prod) | Member 3 | Medium | Laptop / cloud DB |
| M13 | `reports` | Builds the PDF health-assessment report with charts | result JSON → PDF | Member 3 | Medium | Laptop / server |
| M14 | `frontend` | Consent, profile form, camera capture with live guide, results page, history, PDF download | user ↔ API | Member 3 (Sidd helps) | Medium | Browser |
| M15 | `evaluation` | Runs the pipeline on UBFC-rPPG / PURE / own data, computes MAE, RMSE, r, Bland–Altman | dataset → tables + plots for the paper | Sidd + Member 2 | Medium | Colab |

**Key technical choices, with the reason:**

- **POS as the default rPPG method,** with CHROM and GREEN kept for the comparison chapter. POS handled motion best in the Wang et al. 2017 benchmarks and in the Feature-selection paper in our project files. We still prove it on our own data (RQ1) instead of assuming it.
- **MediaPipe Face Landmarker (Tasks API)** instead of the old `mp.solutions.face_mesh`, which Google has marked legacy. Same 468+ landmarks, maintained API.
- **Python 3.11** for the backend, as decided in the synopsis, for ML library compatibility (MediaPipe, ONNX Runtime and the training libraries). Revisit 3.12 only once every dependency is confirmed on it, and log the change in `docs/decisions.md`.
- **Record-and-upload, not live streaming.** The browser records a 30-second clip and uploads it. This was decided in the synopsis because it works on weak laptops and every phone, and keeps one Python codebase as the single source of truth.
- **Streamlit becomes a lab console, not the product.** Sidd can build a small Streamlit page that shows the live waveform and ROI overlay for the viva demo. Real users get the web app (M14), because Streamlit is not built for login, many users, or mobile.
- **SpO2 is dropped from the main report** or shown as "experimental". A normal RGB webcam has no infrared channel, so SpO2 from it is poorly validated. The BPIC report shows it; we explain why we don't.

## 3. Team split (3 people)

Sidd owns the signal core and the integration; Member 2 owns everything from video to features and the BP model; Member 3 owns everything the user touches and everything that is stored. Each person can work alone for days because the three parts only meet at two JSON contracts: **RGB traces** (M3 → M5) and **result JSON** (M10 → M11).

| Person | Role | Owns | Learns first (weeks 1–2) | Done when |
| --- | --- | --- | --- | --- |
| Sidd (lead) | Signal & integration lead | M5, M6, M7, M10, M15, GitHub admin, code review, paper lead | Already has the background; prepares the teaching sessions below | HR within 5 bpm MAE on UBFC-rPPG; pipeline runs end-to-end |
| Member 2 | Vision & ML engineer | M1, M2, M3, M4, M8 | Python + NumPy, OpenCV basics, MediaPipe, pandas, scikit-learn, Colab | ROI traces stable on a still face; BP model trained with subject-wise cross-validation |
| Member 3 | Web & data engineer | M9, M11, M12, M13, M14, deployment | Python basics, FastAPI, SQL + SQLAlchemy, HTML/CSS/JS, Git | A stranger can sign up, scan, see results and download a PDF on the live site |

**How Sidd teaches the other two** — one 90-minute session per week for the first four weeks, then a 30-minute weekly sync:

1. **Week 1 — Git and the repo.** Clone, branch, commit, push, open a PR, fix a merge conflict on purpose. Everyone ships one tiny PR (their name in `docs/TEAM.md`).
2. **Week 2 — How rPPG works.** Blood absorbs green light; each heartbeat changes skin colour by about 0.1%; averaging thousands of pixels makes it visible. Live demo: green-channel average of your own forehead, FFT, see the peak at your pulse.
3. **Week 3 — The contracts.** Walk through the two JSON schemas and the mocked API, so Member 3 can build the website against fake data while the real pipeline is unfinished.
4. **Week 4 — Testing and Colab.** Write a pytest, run CI, run a training notebook on Colab that pulls the repo and saves to Drive.

**Rules that keep a 3-person team moving:**

- Every module gets a short `README.md` (purpose, inputs, outputs, example) and at least one test before its PR is merged.
- Nobody waits on anybody: Member 3 builds on `mock_result.json` from week 3; Sidd builds on recorded sample traces; Member 2 builds on dataset videos.
- Pair programming once a week on the hardest open problem, rotating who drives.

## 4. GitHub workflow

One repo under a GitHub organisation (free), `main` protected, every change through a pull request that Sidd reviews, and CI that runs tests on every PR.

**Repo layout** (adapts the folder list in the project instructions so backend, frontend and training stay apart):

```
vitalscan/
├── backend/
│   ├── vitalscan/
│   │   ├── video_io/          M1
│   │   ├── face_detection/    M2
│   │   ├── roi/               M3
│   │   ├── quality/           M4
│   │   ├── rppg/              M5  (green.py, chrom.py, pos.py)
│   │   ├── signal_processing/ M6
│   │   ├── vitals/            M7
│   │   ├── ml_models/         M8  (inference only, loads .onnx)
│   │   ├── derived/           M9
│   │   ├── pipeline.py        M10
│   │   ├── api/               M11
│   │   ├── db/                M12 (+ alembic/)
│   │   ├── reports/           M13
│   │   └── utils/             logging, config
│   ├── tests/
│   └── pyproject.toml
├── frontend/                  M14
├── training/                  scripts Colab runs (features, train_bp.py, export_onnx.py)
├── evaluation/                M15
├── notebooks/                 thin Colab notebooks that call training/ and evaluation/
├── datasets/                  loaders only — data itself is gitignored
├── configs/                   YAML: ROI indices, filter bands, thresholds
├── lab_console/               Streamlit demo for the viva
├── paper/                     LaTeX source (or link to Overleaf)
├── docs/                      architecture, API contract, module READMEs
├── .github/workflows/ci.yml
├── docker-compose.yml
└── README.md
```

**Branching and PRs:**

1. Pick an issue from the GitHub Projects board, move it to *In progress*.
2. Branch from `main`: `feat/m5-pos`, `fix/roi-mask`, `docs/api-contract`.
3. Small commits with clear messages (`feat(rppg): add POS method`).
4. Open a PR linked to the issue (`Closes #12`). CI must pass: `ruff` (lint), `pytest`, and a type check with `mypy`.
5. Sidd reviews; one approval required; squash-merge; delete the branch.

**Settings to switch on once:**

- Branch protection on `main`: require PR, 1 approval, passing CI, no force-push.
- `CODEOWNERS` so each PR auto-requests the right reviewer.
- `pre-commit` hooks: ruff, black, and `nbstripout` (removes notebook outputs, which otherwise cause constant merge conflicts).
- `.gitignore` for `datasets/`, `outputs/`, `*.onnx`, `*.mp4`, `.env`. Model files go to **GitHub Releases** or the **Hugging Face Hub**, never into git.
- Secrets (DB password, JWT key) live in `.env` locally and in GitHub/host secrets in production — never committed.
- Issue templates: *Feature*, *Bug*, *Experiment* (hypothesis, dataset, metric, result) — the Experiment issues become your paper's lab notebook.

## 5. Compute: laptops vs Google Colab

Laptops write and test code on short clips; Colab does anything that touches a whole dataset or trains a model. Running the finished pipeline on one 30-second scan is light (CPU only), so the production server never needs a GPU.

| Task | Where | Why |
| --- | --- | --- |
| Writing code, unit tests, the website, the API, SQLite DB | Laptop | Light; needs only Python + a browser |
| Running the pipeline on one 30 s clip | Laptop / server CPU | About 900 frames through MediaPipe; seconds, not minutes |
| Processing UBFC-rPPG / PURE / Vital Videos (all subjects) | Colab | Many GB of video; hours of CPU |
| Extracting BP features from PulseDB | Colab | Hundreds of thousands of pulse segments |
| Training BP models (RF, XGBoost, LightGBM, CNN-LSTM) | Colab GPU (Kaggle as backup) | The neural models need a GPU |
| Hyper-parameter search, cross-validation | Colab | Many repeated fits |

**The Colab workflow — notebooks stay thin, the logic lives in the repo:**

```python
# cell 1 — setup
from google.colab import drive
drive.mount('/content/drive')
!git clone https://github.com/<org>/vitalscan.git
%cd vitalscan/backend
!pip install -q -e .

# cell 2 — run a script that lives in the repo
!python ../training/train_bp.py \
    --data /content/drive/MyDrive/vitalscan/datasets/pulsedb \
    --out  /content/drive/MyDrive/vitalscan/outputs/bp_v1

# cell 3 — export the model the server will load
!python ../training/export_onnx.py --run /content/drive/MyDrive/vitalscan/outputs/bp_v1
```

- **One shared Drive folder** (`vitalscan/datasets`, `vitalscan/outputs`) owned by Sidd and shared with both members, so a dataset is downloaded once.
- **Colab sessions disconnect.** Scripts save checkpoints and results to Drive every epoch or every N subjects, and resume from the last checkpoint.
- **Model hand-off:** train on Colab → export to ONNX → upload as a GitHub Release asset → the backend downloads that exact version at start-up. ONNX Runtime then runs the model on a plain CPU.
- **Fix random seeds** and log every run (params + metrics) to a CSV or to free MLflow/Weights & Biases, so every number in the paper can be reproduced.

**Datasets — what each is for and the preprocessing it needs:**

| Dataset | What it contains | Use in our project | Access | Preprocessing |
| --- | --- | --- | --- | --- |
| UBFC-rPPG | Face videos + finger-oximeter PPG/HR | Validate HR (RQ1, RQ2) | Free download from the authors' site | Read video, align ground-truth PPG timestamps, compute reference HR per 30 s window |
| PURE | Image sequences with 6 head-motion setups + pulse oximeter | Test HR under motion | Request from TU Ilmenau | Convert PNG frames to arrays at 30 fps, resample reference to frame times |
| Vital Videos | Face videos with reference BP and other vitals | The only one here that pairs **face video with BP** — key for RQ3 | Request access; read the licence terms | Same as UBFC, plus attach the cuff BP reading per video |
| PulseDB | Cleaned 10 s segments of finger PPG + ECG + arterial BP (from MIMIC-III and VitalDB) | Train the BP model on large data | Free from its GitHub. Ready-made Subset files are **not** hosted (generated with a MATLAB script from very large Segment files); the **VitalDB part is on Kaggle** as "PulseDB Supplementary Subsets" — start there | `camera_match` (125 → 30 Hz, same detrend + band-pass as M6), pulse-shape features, group by subject for splits. MIMIC-III subjects have no height/weight, so BMI exists only for VitalDB |
| iPPG + BP from CN-BP and VV-Small ([Mendeley](https://data.mendeley.com/datasets/3nmj5v5nrh/1)) | Already-extracted facial iPPG signals (3 × 250 samples per person, ~30 Hz) + SBP/DBP, 85 people (43 Asian from CN-BP) | Quick first check of RQ3 (finger-trained model on real face signals) before Vital Videos arrives | Free, CC BY 4.0 | No videos, so it tests the BP model only, not our pipeline. No subject IDs: group by order (3 segments per person) and verify. The VV-Small half derives from Vital Videos; confirm it may be used before relying on it |
| VIPL-HR | Large face-video set, varied devices | Optional extra HR test | Request from the authors | As UBFC |
| CLBP-300 ([Mendeley](https://data.mendeley.com/datasets/8xpbdtctpv/2)) | 300 adults, face video + clinical BP monitor + HR, indoor/outdoor lighting, 58 GB | **Backup only**, if Vital Videos refuses | Data Use Agreement + institutional email + an unpublished fee; CC BY-NC-ND 4.0 | Only after the guide confirms the college will pay; too large for free Drive |
| Own data | Team + consenting volunteers with an Omron-type cuff | Calibration study (RQ5) and a real-world test set | We collect it | Record 30 s clip + cuff reading at the same time; consent form signed |

**Big caveat for the paper:** PulseDB is contact finger PPG from hospital patients; our input is a noisy facial webcam signal. That domain gap is exactly RQ3, and measuring it honestly is a stronger result than hiding it.

## 6. Database design

PostgreSQL in production, SQLite on laptops, both through SQLAlchemy 2.0 with Alembic migrations — the same Python code talks to both, and weak laptops never need Docker or a database server.

**Why PostgreSQL:** free managed hosting exists (Neon, Supabase), it has a JSON column type for flexible result data, and it is what a reviewer expects in a "production" claim. MongoDB was considered and rejected: our data is relational (a user has many scans, a scan has many measurements), and SQL is also what your DBMS syllabus examines.

| Table | Key columns | Notes |
| --- | --- | --- |
| `users` | id (UUID), email (unique), password\_hash (argon2), role (user/researcher/admin), created\_at | Never store plain passwords |
| `profiles` | user\_id (FK), date\_of\_birth, sex, height\_cm, weight\_kg, updated\_at | Needed for BMI, VO2max, HR zones, and as BP model inputs |
| `consents` | id, user\_id, consent\_type (processing / research\_use / video\_retention), version, granted\_at, withdrawn\_at | Legal record; one row per consent given or withdrawn |
| `scans` | id, user\_id, started\_at, duration\_s, fps, device\_info, status (processing/done/failed), failure\_reason, pipeline\_version, model\_version | One row per 30 s scan; versions let you reproduce any old result |
| `quality_metrics` | scan\_id, brightness, motion\_score, face\_lost\_ratio, snr\_db, passed | Explains *why* a scan was rejected |
| `measurements` | id, scan\_id, metric (hr, rr, sdnn, sbp, dbp…), value, unit, confidence (0–1), method (pos/chrom/formula), is\_experimental | One row per number shown to the user; long format makes adding new vitals a no-schema-change job |
| `signal_traces` | scan\_id, storage\_key, format (npz) | Points to the compressed RGB + pulse traces in object storage, not inside the DB |
| `calibrations` | id, user\_id, cuff\_sbp, cuff\_dbp, device\_model, measured\_at, linked\_scan\_id | User-entered cuff readings for the per-user calibration study (RQ5) |
| `reports` | id, scan\_id, storage\_key, sha256, generated\_at | The PDF file lives in storage; the hash proves it wasn't edited |
| `audit_log` | id, user\_id, action (login, view, export, delete), at, ip\_hash | Who did what; needed for data-protection requests |

**Privacy-first storage rule:** the raw face video is **deleted right after processing** unless the user ticked the separate *research use* consent. We keep only the numeric traces and results. This shrinks storage costs, reduces risk if the server is breached, and is a strong point in the paper's ethics section.

**DBMS concepts this lets you show in the viva:** normalisation to 3NF, foreign keys with `ON DELETE CASCADE` (deleting a user wipes their data), indexes on `scans(user_id, started_at)`, transactions (a scan and its measurements save together or not at all), migrations, and role-based access.

## 7. PDF report (modelled on the Glenmark BPIC report)

Our PDF follows the same section order as the CarePlix/Glenmark BPIC "Digital Health Assessment Report" in the project files, so users find it familiar — but every number also shows its confidence and, for derived values, the formula that produced it. That side-by-side is our paper's novelty made visible.

**Branding rule:** we copy the *structure*, never the Glenmark or CarePlix name, logo, colours or licence line. Their report carries a medical-device manufacturing licence number; ours is not a licensed device, so putting their branding on our output would misrepresent it. We cite the BPIC report in the paper as the commercial baseline.

**Page layout:**

1. **Header** — our project name/logo, user name, sex, age, height, weight, scan date/time, scan ID, pipeline + model version.
2. **Key vitals** — HR, RR, BP estimate, each with value, normal range, confidence bar, and label ("Measured" / "Experimental estimate").
3. **BP category chart** — the estimate plotted on the AHA categories (Normal, Elevated, Stage 1, Stage 2) with its error band drawn around it, so the user sees the uncertainty, not a single sharp dot.
4. **Heart health** — SDNN, RMSSD, pNN50 (marked experimental), plus derived metrics with their formulas (table below).
5. **Signal quality** — lighting, motion and SNR scores, and the pulse waveform plot from the scan.
6. **History** — trend chart of the user's last 10 scans (a trend is more meaningful than one reading).
7. **Explanations** — a plain-language line per vital.
8. **Disclaimer + QR code** — research-only statement; QR links to the online copy and verifies the file's SHA-256.

| Derived metric | Formula we show on the report | Check against Sidd's 7 Aug 2026 BPIC report |
| --- | --- | --- |
| BMI | weight\_kg ÷ height\_m² | 50 ÷ 1.75² = 16.33 — matches |
| Mean arterial pressure | DBP + (SBP − DBP) ÷ 3 | 82 + 43 ÷ 3 = 96.33 — matches |
| HR max | 208 − 0.7 × age (Tanaka) | 208 − 15.4 = 192.6 ≈ 193 — matches |
| HR reserve | HR max − resting HR | 193 − 91 = 102 — matches |
| VO2max | 15.3 × HR max ÷ resting HR (Uth–Sørensen) | 15.3 × 193 ÷ 91 = 32.4 vs 32.31 reported — near match |
| Target HR (Karvonen) | resting HR + intensity × HR reserve | to confirm which intensity gives their "< 111" |

This reverse-engineering becomes an automatic unit test in M9: feed in the BPIC inputs, assert our outputs match their report.

**Tooling:** ReportLab (pure Python, works the same on Windows laptops and the Linux server) for the layout, Matplotlib for the charts rendered to PNG, `qrcode` for the QR. WeasyPrint makes nicer HTML-to-PDF layouts but is awkward to install on Windows, so it is a later option.

## 8. Production deployment

Ship one Docker container (FastAPI + the pipeline + the frontend files) to a cloud host, connect a managed PostgreSQL and an object store, and serve everything over HTTPS — browsers only allow camera access on HTTPS pages.

| Piece | Beta choice (free / near-free) | Later, if real users grow |
| --- | --- | --- |
| App server | Hugging Face Spaces (Docker) or Render | A small VPS (e.g. DigitalOcean, Hetzner) or AWS/GCP student credits |
| Database | Neon or Supabase PostgreSQL | Same, paid tier with backups |
| File storage (PDFs, traces) | Supabase Storage or Cloudflare R2 | Same |
| Frontend | Served by FastAPI as static files | Separate CDN host (Cloudflare Pages / Vercel) |
| Domain + HTTPS | Host's free subdomain | Own domain (\~₹800/year) via Cloudflare |
| Errors / uptime | Logs + a free uptime monitor | Sentry |

Free tiers change often — Member 3 confirms current limits (RAM, sleep-on-idle, storage) before picking one. MediaPipe + ONNX need roughly 1–2 GB RAM, which rules out the smallest free instances.

**Processing flow on the server:** upload → save to a temp folder → put a job in a queue → a background worker runs the pipeline → results saved → video deleted → the browser polls `/scans/{id}` until status is *done*. Start with FastAPI `BackgroundTasks`; move to a proper queue (RQ + Redis) only if many users scan at the same time.

**Security and compliance checklist before real users:**

- [ ] Consent screen before the camera turns on, with separate tick-boxes for processing and research use
- [ ] Privacy policy + terms page; users must be 18+
- [ ] Passwords hashed with argon2; JWT access tokens with short expiry; HTTPS only
- [ ] Upload limits: max 60 s, max \~30 MB, video types only; rate limit per user
- [ ] "Delete my account and data" button that really deletes (FK cascade + storage cleanup)
- [ ] Daily DB backups; secrets only in host environment variables
- [ ] Disclaimer on every results page and PDF
- [ ] College ethics/guide approval and signed consent forms for the volunteer data study

**Stretch goal (strong for the paper):** move face detection and ROI averaging into the browser with MediaPipe's JavaScript version, and upload only the RGB traces (a few KB) instead of video. The face never leaves the user's device. Do this only after the Python pipeline is validated, and test that both versions give the same traces.

## 9. Research paper plan

The paper answers the five research questions from the synopsis with real numbers; each RQ maps to one experiment, one table or figure, and one owner. Working title: *"Transparent Contactless Vital-Sign Estimation from Facial Video: An Open rPPG Pipeline and an Audit of Commercial Face-Scan Reports."*

| RQ | Question | Experiment | Data | Metrics | Owner |
| --- | --- | --- | --- | --- | --- |
| RQ1 | Which rPPG method is most accurate for HR: GREEN, CHROM or POS? | Run all three on the same clips | UBFC-rPPG, PURE | MAE, RMSE, Pearson r, Bland–Altman | Sidd |
| RQ2 | Which face region gives the best signal: forehead, cheeks, or both? | Same method, different ROIs | UBFC-rPPG, PURE | MAE, SNR | Member 2 |
| RQ3 | How much accuracy is lost when a BP model trained on contact PPG is used on facial rPPG? | Train on PulseDB, test on Vital Videos + own data | PulseDB, Vital Videos, own | MAE, SD of error, r | Member 2 |
| RQ4 | Does our BP model beat a trivial baseline (predicting the population average by age/sex)? | Compare against the AHA/age-sex mean baseline | Vital Videos, own | MAE vs baseline MAE | Member 2 + Sidd |
| RQ5 | Does a one-time cuff calibration per user reduce BP error? | Calibrate with 1 cuff reading, test on later scans | Own data (repeat visits) | MAE before vs after | Sidd + Member 3 |

**Rules that make the results credible:**

- **Split by subject, never by clip.** If one person's clips sit in both train and test, the model memorises the person and error looks far better than it really is. Use leave-one-subject-out or GroupKFold.
- **Report against the medical standard.** AAMI/ISO 81060-2 accepts a BP device whose mean error is within ±5 mmHg with standard deviation ≤ 8 mmHg. State plainly whether we meet it — most webcam BP studies do not, and saying so is honest science.
- **Compare BP models fairly:** Random Forest, XGBoost, LightGBM, a small MLP, and CNN-LSTM on the raw waveform; same splits, same features, report MAE, RMSE, R² and r with mean ± SD over folds.
- **Report failures:** how many scans were rejected by the quality gate, and accuracy split by skin tone (Fitzpatrick type, where the dataset records it) and lighting.

**Paper structure (IEEE conference format, 6–8 pages):** Abstract → Introduction (gap: opaque commercial reports) → Related work (the 14-source survey) → Method (pipeline, M1–M9) → Experiments (RQ1–RQ5) → Results → Commercial-report audit (section 7 table) → Limitations & ethics → Conclusion.

**Tools and venue:** write in Overleaf with the IEEE template, references in Zotero. Target an IEEE-indexed conference (check the guide's preference and upcoming deadlines, e.g. IEEE India Council conferences) and post a preprint on arXiv. Avoid journals that ask for payment with fast "guaranteed" acceptance — they are usually predatory and can hurt a Master's application.

## 10. Timeline

About 25 weeks from 26 Oct 2026 to mid-April 2027, with the end-to-end demo on 28 Feb as the gate: no new features after it, only beta fixes, results and writing.

*(Timeline diagram: see the online version of this doc, https://claude.ai/artifact/Bmsp6bJ4QtnCGzDdiBzvZD)*

The three workstreams overlap from mid-November because of the mocked API: Member 3 never waits for the pipeline. Confirm the dates against your university exam calendar and your guide's review dates, then copy each row into the GitHub Projects board as a milestone.

## 11. Week 1 kickoff checklist

By the end of week 1 everyone has the repo running locally, has merged one PR, and has seen their own pulse on a graph.

**Sidd**

- [ ] Create the GitHub organisation + `vitalscan` repo with the layout from section 4, branch protection, CI, CODEOWNERS, issue templates
- [ ] Create the GitHub Projects board with every module M1–M15 as an issue
- [ ] Write `docs/contracts.md`: the RGB-trace schema and the result-JSON schema, plus `mock_result.json`
- [ ] Create the shared Drive folder; request PURE, Vital Videos and VIPL-HR access (requests take days to weeks)
- [ ] Write the 40-line "green channel → FFT → HR" demo script for the week-2 teaching session
- [ ] Talk to the project guide about ethics approval for volunteer recordings

**Member 2**

- [ ] Install Python 3.11, VS Code, Git; clone the repo; `pip install -e backend`
- [ ] Merge the first PR (name in `docs/TEAM.md`)
- [ ] Download UBFC-rPPG into the shared Drive folder
- [ ] Get MediaPipe Face Landmarker drawing the 478 points on their own webcam

**Member 3**

- [ ] Same setup + first PR
- [ ] Finish the official FastAPI tutorial up to "SQL databases"
- [ ] Build a one-page HTML file that opens the camera and records 10 s with MediaRecorder
- [ ] Compare 2 free hosting options and 2 free PostgreSQL options; write findings in `docs/hosting.md`

**All three**

- [ ] Agree on a weekly sync slot and a group chat channel for PR notifications
- [ ] Read Wang et al. 2017 (POS) and de Haan & Jeanne 2013 (CHROM) — the two core papers
