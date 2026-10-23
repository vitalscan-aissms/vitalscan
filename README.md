# VitalScan

Contactless vital-sign estimation from a 30-second facial video using remote photoplethysmography (rPPG).
Final Year Project, AISSMS College of Engineering, Pune.

> **For education and research only. Not a medical device.** Blood pressure is an experimental estimate.
> Confirm any reading with a certified BP monitor and a doctor.

- New to the team? Start with [`docs/starter-guide.md`](docs/starter-guide.md).
- The full plan: [`docs/build-plan.md`](docs/build-plan.md).
- Data formats between modules: [`docs/contracts.md`](docs/contracts.md).

## Quick start (Windows)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e "backend[dev]"
pytest backend
```
