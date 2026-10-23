# Decision log

Date · decision · why. Newest first. This becomes part of the thesis methodology chapter.

| Date | Decision | Why |
| --- | --- | --- |
| 2026-10-24 | M8 package is named `ml_models` (not `bp_model`); training code stays in `training/` | Folder already existed; it holds inference only |
| 2026-10-24 | CI runs `ruff`, `mypy` and `pytest` | Type hints are a coding standard; catch errors before review |
| 2026-10-24 | Moved project work to a local repo used from the Claude desktop app Code tab; context lives in `CLAUDE.md` | Keep plan, code and docs together in one place |
| 2026-10-24 | Team reduced to 3; frontend role merged into Web & Data (Member 3) | Team size change |
| 2026-10-24 | Parallel work via contracts, fixtures, mocked API and a walking-skeleton pipeline | Nobody blocks on another module |
| 2026-10-24 | PostgreSQL (prod) + SQLite (dev) via SQLAlchemy 2.0 + Alembic | Relational data, free hosting, no DB server needed on weak laptops |
| 2026-10-24 | ReportLab for PDFs; BPIC report structure, own branding | Cross-platform; avoid misrepresenting a licensed device |
| 2026-10-24 | Raw video deleted after processing unless research consent | DPDP Act 2023, lower breach risk |
| 2026-10-24 | Streamlit only as lab console; product is FastAPI + web frontend | Streamlit is not built for login, many users or mobile |
| Synopsis | Record-and-upload PWA, not native apps or live streaming | Team hardware; one Python codebase |
| Synopsis | Python 3.11 | ML library compatibility |
| Synopsis | Blood glucose excluded | Physics-based feasibility analysis |
| Synopsis | BP framed as trend/experimental estimate | Academic credibility |
