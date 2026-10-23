# VitalScan — Final Year Project (contactless vitals from facial video)

This file is read automatically by Claude at the start of every session in this folder.
It carries the project context that was built up in the original claude.ai chat.

## What we are building

"Non-Contact Blood Pressure Analysis Using Live Video Feed" — a final-year engineering project
(AISSMS College of Engineering, Pune; SPPU) that will also be written up as a research paper
and deployed on the web for real users.

A user records a 30-second face video in the browser. The server extracts the remote
photoplethysmography (rPPG) signal from skin-colour changes and returns heart rate,
respiratory rate, HRV, an **experimental** blood-pressure estimate, derived metrics, and a PDF report.
Everything is stored in a database.

## Non-negotiables (scientific and legal)

- Educational/research use only. **Never present BP as a clinical or medically validated measurement.**
  Every results screen and PDF carries: "For education and research only. Not a medical device.
  Confirm any reading with a certified BP monitor and a doctor."
- Always distinguish measured (camera estimate) / estimated / experimental / calculated-by-formula values.
- Scientific validity over impressive numbers: split train/test **by subject** (GroupKFold / LOSO),
  report MAE, RMSE, R², Pearson r, Bland–Altman, and compare BP against AAMI/ISO 81060-2 (±5 mmHg mean, SD ≤ 8).
- Real users → India's DPDP Act 2023: explicit consent, privacy policy, delete-my-data, 18+ only.
  Raw face video is deleted right after processing unless the user gave separate research consent.
- The PDF report follows the *structure* of the CarePlix/Glenmark "BPIC" Digital Health Assessment
  report (our commercial baseline), but **never** uses Glenmark/CarePlix names, logos, colours or
  licence line. Our novelty: show every formula and confidence score the commercial report hides.
- SpO2 is excluded or marked experimental (RGB webcams have no IR channel).

## Team (3 people) and ownership

| Person | Role | Modules |
| --- | --- | --- |
| Sidd (lead) | Signal & integration lead, paper lead, reviews every PR | M5 rppg, M6 signal_processing, M7 vitals, M10 pipeline, M15 evaluation |
| Member 2 | Vision & ML engineer (beginner) | M1 video_io, M2 face_detection, M3 roi, M4 quality, M8 ml_models (BP model) |
| Member 3 | Web & data engineer (beginner) | M9 derived, M11 api, M12 db, M13 reports, M14 frontend, deployment |

Teammates start from zero and have weak laptops: heavy work (datasets, training) runs on
**Google Colab** (Kaggle as backup); laptops only edit code and run tests on short clips.
When helping teammates, explain from first principles and keep code readable for beginners.

## Architecture decisions (already made — don't relitigate without reason)

- **Record-and-upload**, not live streaming: browser MediaRecorder (30 s, `facingMode: "user"`) → FastAPI upload → background pipeline → result JSON → dashboard + PDF.
- **Python 3.11** (chosen over 3.12 for ML-library compatibility).
- **MediaPipe Face Landmarker (Tasks API, VIDEO mode, 478 landmarks)** — not legacy `mp.solutions.face_mesh`.
- ROIs: forehead + left/right cheek polygons from landmark indices (kept in `configs/roi.yaml`), YCrCb skin mask.
- rPPG: implement GREEN, CHROM, **POS (default)**; comparing them is RQ1.
- Signal: resample to uniform 30 Hz from real timestamps, detrend, Butterworth band-pass 0.7–4 Hz with filtfilt, FFT HR, peak HR cross-check, SNR (de Haan) → confidence.
- BP model: pulse-shape features + age/sex/BMI; trained on **PulseDB** (MATLAB v7.3 .mat, load with `mat73`) on Colab; RF / XGBoost / LightGBM / MLP / CNN-LSTM compared; best exported to **ONNX** and run with ONNX Runtime on CPU. Model files go to GitHub Releases, never into git.
- HR validation datasets: UBFC-rPPG, PURE (request), VitalVideos (face video + BP, request), own volunteer data with a cuff monitor.
- Backend: **FastAPI** + Pydantic; **SQLAlchemy 2.0 + Alembic**; **SQLite locally, PostgreSQL in production** (Neon/Supabase); argon2 passwords, JWT tokens.
- PDF: **ReportLab** + Matplotlib charts + QR code.
- Frontend: plain HTML/CSS/JS served by FastAPI (PWA, HTTPS required for camera); Chart.js for trends.
- **Streamlit** only as an internal "lab console" for the viva demo, not the product.
- Deploy: one Docker container (Hugging Face Spaces / Render for beta), managed Postgres, object storage for PDFs/traces.
- Team works in parallel through **contracts** (`docs/contracts.md`), fixtures (`backend/tests/fixtures/`), a mocked API and a walking-skeleton pipeline — nobody waits on another module.

## Research questions (results chapter)

RQ1 best rPPG method (GREEN/CHROM/POS) · RQ2 best ROI · RQ3 domain gap: BP model trained on contact PPG applied to facial rPPG · RQ4 BP model vs trivial age/sex baseline · RQ5 value of one-time cuff calibration.

## Repo map

```
backend/vitalscan/   one sub-package per module (M1–M13), pipeline.py = M10
backend/tests/       pytest; fixtures/ holds mock_result.json and sample data
frontend/            M14 website
training/            scripts Colab runs (features, train_bp.py, export_onnx.py)
evaluation/          M15 dataset evaluation scripts
notebooks/           thin Colab notebooks that call training/ and evaluation/
configs/             YAML: ROI indices, filter bands, quality thresholds
lab_console/         Streamlit viva demo
paper/               paper source
docs/                build-plan.md, starter-guide.md, contracts.md, decisions.md, TEAM.md
```

## Coding standards

- Type hints everywhere; small modular classes/functions; docstrings with Purpose, Inputs, Outputs, Example.
- `logging`, never `print`, inside the package. Proper exceptions with clear messages.
- No placeholder code when a real implementation is possible. No duplicated logic.
- Every module: a README (purpose, inputs, outputs, dependencies, example) + at least one test.
- `ruff check .` and `pytest` must pass. Datasets, videos, `.env`, `*.onnx` never committed.

## How Sidd wants feature requests handled

1. Explain the approach first (compare options when there are several; recommend one).
2. Show only the files that change.
3. Write complete, working code.
4. Explain how to test it.
5. Suggest improvements.

Sidd prefers detailed explanations over brief ones.

## Status (as of 24 Oct 2026)

- Done: concept, literature survey (14 sources), synopsis, master build plan, team starter guide.
- This folder: initial scaffold only (structure, docs, contracts, mock result). No module implemented yet.
- Git initialised locally on `main` (no commits, no remote yet). CI lives in `.github/workflows/ci.yml` (ruff, mypy, pytest).
  Local venv: `.venv` on Python 3.11 (the machine's default `py` is 3.14, so always use `py -3.11`).
- Next: create the GitHub org + repo and push this scaffold; Week-1 checklist in `docs/build-plan.md` §11;
  build the walking-skeleton pipeline and synthetic-signal generator.
- Online versions of the docs (with diagrams): build plan https://claude.ai/artifact/Bmsp6bJ4QtnCGzDdiBzvZD ·
  starter guide https://claude.ai/artifact/PxEbWSN1ShWNRQtFTFLBDv
