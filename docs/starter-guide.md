# VitalScan FYP — Team Starter Guide (from zero)

Oct 24, 2026 · @Siddhanth Waghmare

## 0. How to use this guide

You do not need any prior knowledge. Follow sections 1–4 together in the first two weeks, then switch to your own section (5, 6 or 7). By week 4 you will be shipping real code for the project.

We are building **VitalScan**: a website where a user records a 30-second video of their face, and our system estimates heart rate, breathing rate and (experimentally) blood pressure from tiny colour changes in the skin, then gives a PDF report. The full plan is in the *rPPG Vitals FYP — Master Build Plan* doc; this guide is the "how do I actually start" companion.

| Who | Role | Read | Your modules |
| --- | --- | --- | --- |
| Everyone | — | Sections 0–4, 8, 9, 11 | — |
| Member 2 | Vision & ML engineer | Section 5 | M1 video, M2 face, M3 ROI, M4 quality, M8 BP model |
| Member 3 | Web & data engineer | Section 6 | M9 formulas, M11 API, M12 database, M13 PDF, M14 website |
| Sidd | Signal & integration lead | Section 7 | M5 rPPG, M6 filters, M7 vitals, M10 pipeline, M15 evaluation |

**The path from zero to contributor:**

1. **Week 1 — Set up.** Accounts, software, repo cloned, first pull request merged (sections 1–2).
2. **Weeks 1–2 — Foundations.** Python basics, plus your role's first library (section 3 + your section).
3. **Week 2 — Understand the idea.** Run the pulse demo on your own face (section 4). Seeing your heartbeat on a graph makes everything else make sense.
4. **Week 3 onward — Build.** Pick the first issue for your module on the GitHub board and follow the build steps in your section.

**Three rules for beginners:**

- **Type the code, don't copy-paste it** for the first few weeks. Typing it is how you learn it.
- **Stuck for more than 45 minutes? Ask** (section 9 shows how). Being stuck alone for a day wastes the team's time.
- **Small steps.** Make one thing work, commit it, then add the next. Never write 200 lines before running anything.

You can use AI assistants (Claude, ChatGPT) to *explain* code and errors. Don't paste code you can't explain: in the viva, the examiner will ask you to walk through your own module line by line.

## 1. Day 0 setup (everyone, about 2 hours)

At the end of this section your laptop runs Python 3.11, Git and VS Code, and you have the team repo on your machine. Do it together on a call the first time, so one person can fix problems for all three.

**Step 1 — Create accounts**

- [ ] **GitHub** account at github.com, using your college email. Then apply for the free **GitHub Student Developer Pack** (education.github.com/pack). It gives you GitHub Copilot and cloud credits.
- [ ] Send your GitHub username to Sidd so he can add you to the team organisation. Accept the invite email.
- [ ] A **Google account** for Google Colab and the shared Drive folder.

**Step 2 — Install software (Windows)**

- [ ] **Python 3.11** from python.org/downloads (pick the newest 3.11.x Windows installer). On the first installer screen, **tick "Add python.exe to PATH"**. This is the most common beginner mistake.
- [ ] **Git for Windows** from git-scm.com. Keep all default options.
- [ ] **VS Code** from code.visualstudio.com. Inside VS Code, open Extensions (Ctrl+Shift+X) and install: *Python*, *Pylance*, *Jupyter*, *GitLens*.
- [ ] Optional: **GitHub Desktop**, if the command line feels scary at first. Learn the commands in section 2 anyway.

On a Mac: install Python 3.11 from python.org, run `xcode-select --install` in Terminal for Git, then install VS Code. The commands below are the same except `source .venv/bin/activate` instead of `.venv\Scripts\activate`.

**Step 3 — Check the installs.** Open *PowerShell* and type:

```powershell
python --version      # should print Python 3.11.x
git --version         # should print git version 2.x
code --version        # should print a VS Code version
```

If `python` opens the Microsoft Store or prints nothing, the PATH tick-box was missed: reinstall Python and tick it.

**Step 4 — Tell Git who you are** (once per laptop):

```powershell
git config --global user.name "Your Name"
git config --global user.email "the-email-on-your-github-account"
```

**Step 5 — Get the project and its libraries**

```powershell
cd D:\                          # or any folder you like
git clone https://github.com/<team-org>/vitalscan.git
cd vitalscan
py -3.11 -m venv .venv          # creates a private Python just for this project
.venv\Scripts\activate          # your prompt now starts with (.venv)
python -m pip install --upgrade pip
pip install -e backend[dev]     # installs our package + all libraries
```

If PowerShell says *running scripts is disabled*, run this once and try again: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

**What is a virtual environment (`.venv`)?** It is a separate box of libraries for this one project. It stops our project's library versions from clashing with anything else on your laptop. **Activate it every time** you open a new terminal for this project.

**Step 6 — Prove it works**

```powershell
python -c "import cv2, mediapipe, numpy, scipy; print('all good')"
pytest                          # runs the team's tests; all should pass
```

Then open the folder in VS Code (`code .`). Press Ctrl+Shift+P → *Python: Select Interpreter* → choose the one inside `.venv`.

**Laptop too weak or low on disk?** That is fine. You only need the code and small test files locally. Datasets and training live on Google Colab (section 8).

## 2. Git and GitHub from zero

Git saves snapshots of the code, and GitHub is where the team shares them. You only need about 10 commands, and you use the same loop every day: **update → branch → code → commit → push → pull request → review → merge**.

**The ideas in one minute:**

- **Repository (repo):** the project folder plus its full history.
- **Commit:** a saved snapshot with a message ("add POS method"). Commit often, as small checkpoints.
- **Branch:** your own copy of the code to work on without breaking anyone else's. `main` is the shared, always-working version. Nobody pushes to `main` directly.
- **Pull request (PR):** "please review my branch and merge it into `main`". Sidd reviews every PR.
- **Merge conflict:** two people changed the same lines. Git asks you to choose. It is normal, not a disaster.

**Your daily loop (copy this onto a sticky note):**

```powershell
# 1. Start of the day: get everyone's latest work
git checkout main
git pull

# 2. Start a new task on its own branch (name it after the issue)
git checkout -b feat/m3-forehead-roi

# 3. ...write code, run it, run pytest...

# 4. Save a checkpoint
git status                  # see what changed
git add backend/vitalscan/roi/forehead.py
git commit -m "feat(roi): add forehead polygon from landmarks"

# 5. Upload your branch
git push -u origin feat/m3-forehead-roi

# 6. On github.com: click "Compare & pull request", write what you did,
#    add "Closes #12" (the issue number), request Sidd as reviewer.

# 7. After it is merged: go back to main and clean up
git checkout main
git pull
git branch -d feat/m3-forehead-roi
```

**Branch names:** `feat/...` for new features, `fix/...` for bug fixes, `docs/...` for documentation, `exp/...` for experiments.

**Commit messages:** `type(module): what you did`, in present tense. For example: `fix(api): reject videos longer than 60 s`.

**Your first PR (week 1 homework):**

1. Create the branch `docs/add-<yourname>`.
2. Add one line to `docs/TEAM.md`: your name, role, GitHub username.
3. Commit, push, open the PR, get it reviewed and merged.
4. Then fix a merge conflict on purpose. Sidd and you both edit the same line of `docs/TEAM.md` on different branches, and you resolve it in VS Code (it shows *Accept Current / Accept Incoming / Accept Both* buttons).

**Never commit these** (`.gitignore` already blocks them, but know why): datasets and videos (too big), `.venv/` (everyone makes their own), `.env` files (passwords and keys), model files `*.onnx` / `*.pkl` (these go to GitHub Releases).

**When Git confuses you:**

- `git status` tells you where you are and what to do next. Read it slowly.
- `git log --oneline -10` shows the last 10 commits.
- Made a mess before committing? `git restore <file>` throws away your changes to that file.
- Really stuck? Don't delete the folder. Message the team with the output of `git status`.

## 3. Python foundations (2 weeks, about 1.5 hours a day)

You need enough Python to read and write small, tidy modules, plus NumPy, because every video frame and every signal in this project is a NumPy array. You don't need to master all of Python before starting: learn the list below, then learn the rest while you build.

| Days | Learn | Free resource (links in section 10) | Prove it with this exercise |
| --- | --- | --- | --- |
| 1–2 | Variables, types, if/else, loops, functions | CS50P lectures 0–2, or Kaggle Learn *Python* | Function `bpm_from_interval(seconds)` that turns 0.8 s between beats into 75 bpm |
| 3–4 | Lists, dicts, strings, f-strings, list comprehensions | CS50P lecture 2, Python official tutorial ch. 3–5 | Store 5 fake scans as dicts, print the one with the highest heart rate |
| 5 | Files, `pathlib`, JSON, exceptions (`try/except`) | CS50P lectures 3 and 6 | Read `mock_result.json`, print the heart rate, handle a missing file politely |
| 6–7 | Classes, dataclasses, type hints, modules and imports | CS50P lecture 8, Real Python *dataclasses* | A `@dataclass ScanResult` with `hr: float`, `rr: float`, `confidence: float` |
| 8–9 | **NumPy**: arrays, shapes, slicing, `mean`, `axis=` | NumPy *absolute beginners* guide | Make a fake video `np.zeros((300, 480, 640, 3))`, take the mean of a 50×50 patch in every frame → shape `(300,)` |
| 10 | Matplotlib plotting | Matplotlib *quick start* | Plot a sine wave at 1.2 Hz for 10 s and label the axes |
| 11 | `logging`, virtual environments, `pip` | Real Python *logging* | Replace every `print` in your exercises with `logger.info` |
| 12 | **pytest** | pytest *get started* | Write 3 tests for `bpm_from_interval` |

**Shapes are the most important idea in this project.** A colour video is a 4D array: `(frames, height, width, 3)`. Averaging the pixels of a face region in every frame gives `(frames, 3)`: one R, G, B value per frame. Most of our bugs will be shape bugs, so print `arr.shape` often.

```python
import numpy as np

video = np.random.rand(300, 480, 640, 3)      # 10 s of fake 30 fps video
forehead = video[:, 100:150, 300:350, :]      # same 50x50 patch in every frame
rgb_trace = forehead.mean(axis=(1, 2))        # average over height and width
print(rgb_trace.shape)                        # (300, 3)  <- one RGB value per frame
green = rgb_trace[:, 1]                       # (300,)    <- the green channel over time
```

**Coding style our repo expects** (CI checks this automatically, so learn it early):

- Type hints on every function: `def estimate_hr(signal: np.ndarray, fps: float) -> float:`
- A docstring saying what goes in and what comes out.
- `logging`, never `print`, inside the package.
- Small functions (under about 40 lines), with clear names over clever ones.
- Run `ruff check .` and `pytest` before every push.

## 4. The science in plain words + your first pulse demo

Every heartbeat pushes a little more blood into the skin of your face. Blood absorbs green light strongly, so with each beat your skin becomes a tiny bit darker in green: far too little for eyes to see, but a camera averaging thousands of pixels can measure it. That colour signal is called **rPPG** (remote photoplethysmography). Counting its peaks gives heart rate.

**The whole project in 7 ideas:**

1. **Find the face** in every frame (MediaPipe gives 478 landmark points on the face).
2. **Pick skin regions** with good blood flow and little hair: forehead and cheeks. These are the **ROIs** (regions of interest).
3. **Average the colour** of each ROI per frame. A 30 s clip at 30 fps gives 900 R, G, B values per ROI.
4. **Combine R, G, B cleverly** to cancel lighting changes and small movements. This is what **GREEN, CHROM and POS** do; POS is usually best.
5. **Filter:** a human pulse lies between 42 and 240 bpm (0.7–4 Hz), so keep only those frequencies and throw away slow light drift and fast noise.
6. **Measure:** the strongest frequency (found with an FFT) × 60 = heart rate. Slow waves riding on the signal give breathing rate. The gaps between peaks give HRV.
7. **Estimate BP (experimental):** the *shape* of each pulse wave (how fast it rises, how wide it is) relates loosely to blood pressure. A machine-learning model learns that relation from data. It is much less reliable than heart rate, so we always label it as an estimate.

**Demo for everyone (week 2):** see your own pulse in 40 lines. Save as `pulse_demo.py`, sit still facing a window or a bright lamp, run `python pulse_demo.py`, and keep still for 20 seconds. Then check against your real pulse: two fingers on your wrist, count for 30 s, × 2.

```python
"""pulse_demo.py — estimate heart rate from the green channel of your forehead."""
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, detrend, filtfilt

SECONDS = 20
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)
green_values, start = [], time.time()

while time.time() - start < SECONDS:
    ok, frame = cap.read()
    if not ok:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    if len(faces) == 1:
        x, y, w, h = faces[0]
        fy1, fy2 = y + int(0.08 * h), y + int(0.22 * h)   # forehead band
        fx1, fx2 = x + int(0.30 * w), x + int(0.70 * w)
        roi = frame[fy1:fy2, fx1:fx2]
        green_values.append(roi[:, :, 1].mean())          # OpenCV order is B, G, R
        cv2.rectangle(frame, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)
    cv2.imshow("Keep still - press Esc to stop", frame)
    if cv2.waitKey(1) == 27:
        break

elapsed = time.time() - start
cap.release()
cv2.destroyAllWindows()

fps = len(green_values) / elapsed                          # real frame rate of YOUR webcam
signal = detrend(np.array(green_values))                   # remove slow drift
b, a = butter(3, [0.7 / (fps / 2), 4.0 / (fps / 2)], btype="band")
signal = filtfilt(b, a, signal)                            # keep 42-240 bpm

freqs = np.fft.rfftfreq(len(signal), d=1 / fps)
power = np.abs(np.fft.rfft(signal)) ** 2
band = (freqs >= 0.7) & (freqs <= 4.0)
hr_bpm = freqs[band][np.argmax(power[band])] * 60
print(f"Frames: {len(green_values)}, fps: {fps:.1f}, estimated HR: {hr_bpm:.0f} bpm")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6))
ax1.plot(np.arange(len(signal)) / fps, signal)
ax1.set(title="Your pulse wave (filtered green channel)", xlabel="seconds")
ax2.plot(freqs[band] * 60, power[band])
ax2.set(title="Frequency spectrum - the peak is your heart rate", xlabel="bpm")
plt.tight_layout()
plt.show()
```

If the estimate is off by more than about 10 bpm, try better light (facing a window, no light behind you), keep completely still, and run for 30 s. **Discuss as a team:** why does moving your head ruin it? Why does dim light make it worse? The answers to these two questions are what the real modules M3–M7 are designed to fix.

**Read next (in this order, the first two are short):** Poh, McDuff & Picard 2010/2011 (the first webcam pulse papers); then Wang et al. 2017 (POS) and de Haan & Jeanne 2013 (CHROM). The DOIs are in the project literature table.

## 5. Member 2 guide — Vision & ML engineer

You turn a video into clean colour signals (M1–M4), and you train the blood-pressure model (M8). Your work is the "eyes" of the system: if the face regions jitter or include hair, nothing downstream can fix it.

**Learning path**

| Week | Learn | Resource (section 10) | Done when you can… |
| --- | --- | --- | --- |
| 1–2 | Python + NumPy (section 3) | CS50P, NumPy beginners | Slice a 4D video array and average a patch |
| 2 | OpenCV basics: read video/webcam, BGR vs RGB, draw shapes, `fillPoly` masks | OpenCV-Python tutorials: *Getting started*, *Image processing* | Show your webcam with a rectangle drawn on it |
| 3 | MediaPipe Face Landmarker | MediaPipe Face Landmarker Python guide | Draw all 478 points on your face live |
| 5 | pandas + scikit-learn basics | Kaggle Learn *Pandas* and *Intro to ML* | Train a Random Forest on any CSV and report MAE |
| 6 | Google Colab + Drive (section 8) | Colab welcome notebook | Run a repo script on Colab that saves output to Drive |

### M1 — `video_io`: video file → frames + timestamps

Browsers record `.webm` files whose frame rate is often uneven, and the stored fps value can be wrong. So never trust the fps number: keep each frame's **real timestamp**.

```python
def read_video(path: Path, max_seconds: float = 60.0) -> tuple[np.ndarray, np.ndarray]:
    """Return frames (N, H, W, 3) in RGB uint8 and timestamps (N,) in seconds."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise VideoReadError(f"Cannot open {path}")
    frames, times = [], []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        times.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if times[-1] > max_seconds:
            break
    cap.release()
    return np.stack(frames), np.array(times)
```

- Steps: read → convert BGR→RGB → downscale to 640 px wide if bigger (saves memory) → reject clips under 15 s.
- Test with: a 10 s clip from your phone, a webm recorded in the browser (Member 3's test page), and one UBFC-rPPG video.
- **Done when:** returns correct shapes for all three, and raises a clear error for a corrupt or empty file.

### M2 — `face_detection`: frame → 478 landmarks

Download `face_landmarker.task` from the *Models* section of the MediaPipe Face Landmarker overview page and keep it in `models/` (gitignored). Use **VIDEO mode**, which tracks the face between frames and is smoother than detecting each frame from scratch.

```python
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="models/face_landmarker.task"),
    running_mode=RunningMode.VIDEO,
    num_faces=2,                     # ask for 2 so we can DETECT the "two people" error
)
with FaceLandmarker.create_from_options(options) as landmarker:
    for frame, t in zip(frames, times):
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = landmarker.detect_for_video(image, int(t * 1000))
        faces = result.face_landmarks          # list of faces; each = 478 points (x, y, z in 0..1)
        if len(faces) != 1:
            ...                                # record "no face" / "multiple faces" for this frame
```

- Landmark `x, y` are fractions of the image width/height: multiply by width/height to get pixels.
- Output: an array `(N, 478, 2)` in pixels, plus a boolean `(N,)` saying whether exactly one face was found.
- **Done when:** runs on a UBFC video, a video with no face, and a video with two people, and reports each case correctly.

### M3 — `roi`: frames + landmarks → RGB traces

This is the most important module you own. For each frame: build a polygon for each region → keep only skin pixels → average R, G, B.

1. **Polygons from landmark indices.** Start with these commonly used sets, then **draw them on your own face to check** and adjust (keep eyebrows, hair and eyes out):
   - Forehead: `[10, 338, 297, 332, 284, 251, 21, 54, 103, 67, 109]`, then shrink the lower edge so it stays above the eyebrows
   - Left cheek: `[118, 119, 100, 126, 209, 49, 129, 203, 205, 50]`
   - Right cheek: `[347, 348, 329, 355, 429, 279, 358, 423, 425, 280]`
   - Keep the final lists in `configs/roi.yaml`, not hard-coded.
2. **Mask:** `cv2.fillPoly(mask, [polygon_pixels], 255)` on a blank image.
3. **Skin filter:** convert to YCrCb and keep pixels with Cr in about 133–173 and Cb in about 77–127. This removes hair, glasses and shadows. Tune on your team's faces and note the values in the README.
4. **Average:** mean R, G, B of pixels that are inside the mask and are skin. If fewer than \~200 pixels survive, mark the frame invalid.
5. **Output:** an array `(N, 3 ROIs, 3 channels)` + a validity flag per frame, saved as `.npz`. This is **the RGB-trace contract** Sidd's code reads, so match `docs/contracts.md` exactly.
6. **Smoothing:** landmarks wobble by a pixel or two between frames. Average each landmark over the last 3 frames before building polygons; this noticeably cleans the signal.

**Done when:** on a still UBFC subject, the green trace of the forehead shows visible periodic waves after Sidd's filter, and the traces from all three ROIs look similar.

### M4 — `quality`: is this scan good enough?

Compute a few numbers per clip; if any fails, the pipeline stops and tells the user how to fix it.

| Check | How to compute | Starting threshold (tune it) | Message to the user |
| --- | --- | --- | --- |
| Too dark | Mean brightness (Y channel) inside the ROIs | below 60 of 255 | "Face a window or a lamp" |
| Overexposed | % of ROI pixels above 250 | more than 5% | "Too much direct light" |
| Head motion | Std. dev. of the nose-tip landmark (index 1) position ÷ face width | above about 0.03 | "Keep your head still" |
| Face lost | % of frames without exactly one face | above 10% | "Keep your face in the frame" |
| Multiple faces | Any frame with 2+ faces | above 5% of frames | "Only one person in the frame" |

Keep the thresholds in `configs/quality.yaml`. Record yourself in good light, dim light, moving and still, and set thresholds that separate those clips. That small experiment is also a figure for the paper.

### M8 — `ml_models` (BP model): pulse features → BP estimate (train on Colab, run on the server)

1. **Get PulseDB** from its GitHub page (section 10). The files are MATLAB v7.3 `.mat` files with 10-second segments of ECG, PPG and arterial BP, plus SBP/DBP labels and age, gender, height, weight. Load them in Python with the `mat73` package. Start with the ready-made `Train_Subset.mat` and `CalFree_Test_Subset.mat`.
2. **Extract features per segment** (write these as functions in `training/features.py` so the server reuses the exact same code):
   - Heart rate and beat-to-beat interval variation
   - Per beat: rise time (foot → peak), pulse width at 25/50/75% height, peak amplitude ratio, systolic vs diastolic area ratio
   - From the first and second derivative of the wave (VPG/APG): position and height of their main peaks
   - Demographics: age, sex, BMI
   - The *Feature selection* paper in our project files lists the 24 features it used; compare against it.
3. **Split by subject, never by segment.** The same person must never be in both training and test data, or the scores will look far better than reality. Use scikit-learn `GroupKFold` with the subject ID as the group.
4. **Train and compare:** a baseline that always predicts the training mean → Linear regression → Random Forest → XGBoost → LightGBM. Later, a small neural net or CNN-LSTM on the raw wave. Report MAE, RMSE, R² and Pearson r as mean ± SD over folds.
5. **Export** the best tree model to ONNX (`skl2onnx` for scikit-learn models; `onnxmltools` for XGBoost/LightGBM). Check that the ONNX model gives the same predictions as the Python model on 100 samples.
6. **Done when:** a results table in `docs/experiments/bp_v1.md`, and `bp_v1.onnx` attached to a GitHub Release.

**Honest expectation:** errors of 8–15 mmHg are normal in this field, and they get worse on facial rPPG than on finger PPG. A clear, honest table beats an impressive-looking but leaky one: examiners and reviewers check for subject leakage first.

## 6. Member 3 guide — Web & data engineer

You build everything a real user touches and everything we store: the website, the API, the database, the PDF report and the live deployment. You start on day one against **`mock_result.json`** (fake but realistic results), so you never wait for the vision or signal code.

**Learning path**

| Week | Learn | Resource (section 10) | Done when you can… |
| --- | --- | --- | --- |
| 1–2 | Python (section 3) | CS50P | Read and write JSON, write a dataclass |
| 1–2 | HTML, CSS, JavaScript basics, `fetch` | MDN *Learn web development*, freeCodeCamp | Make a page with a form that shows what you typed |
| 2–3 | FastAPI | Official FastAPI tutorial (up to *Request Files* and *Background Tasks*) | Run an API with 3 endpoints and test it in `/docs` |
| 3 | SQL | SQLBolt (interactive), PostgreSQL tutorial | Write JOIN, GROUP BY and a foreign key |
| 4 | SQLAlchemy 2.0 ORM + Alembic migrations | SQLAlchemy *Unified tutorial*, Alembic tutorial | Create tables from Python classes and migrate a change |
| 6 | ReportLab | ReportLab user guide (*Platypus* chapter) | Generate a 1-page PDF with a table |
| 8 | Docker basics | Docker *Get started* | Run our backend in a container |

### M9 — `derived`: formulas (start here, week 3)

The easiest module, and the perfect first one: pure functions, no libraries.

```python
def mean_arterial_pressure(sbp: float, dbp: float) -> float:
    """MAP = DBP + (SBP - DBP) / 3, in mmHg."""
    return dbp + (sbp - dbp) / 3

def hr_max_tanaka(age_years: float) -> float:
    """Predicted maximum heart rate (Tanaka 2001): 208 - 0.7 x age."""
    return 208 - 0.7 * age_years
```

Write BMI, MAP, HR max, HR reserve, VO2max (15.3 × HRmax ÷ HRrest) and Karvonen target zones. Each function returns its value **and** the formula text, because the PDF prints the formula. Test them against the BPIC report in the project files: inputs age 22, 175 cm, 50 kg, HR 91, BP 125/82 should give BMI 16.33, MAP 96.33, HR max ≈ 193, HR reserve ≈ 102.

### M11 — `api`: FastAPI endpoints

| Method + path | What it does | Week |
| --- | --- | --- |
| `POST /auth/register`, `POST /auth/login` | Create account / get a token | 5 |
| `PUT /me/profile` | Save age, sex, height, weight | 5 |
| `POST /scans` | Upload the video, returns a scan ID immediately | 3 (mock), 9 (real) |
| `GET /scans/{id}` | Status (*processing / done / failed*) + results | 3 (mock) |
| `GET /scans` | The user's history | 6 |
| `GET /scans/{id}/report.pdf` | Download the PDF | 7 |
| `DELETE /me` | Delete the account and all data | 8 |

```python
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="VitalScan API")

@app.post("/scans", status_code=202)
async def create_scan(background: BackgroundTasks, video: UploadFile = File(...)) -> dict:
    if video.content_type not in {"video/webm", "video/mp4"}:
        raise HTTPException(status_code=415, detail="Upload a webm or mp4 video")
    scan_id = save_upload_and_create_scan_row(video)        # your DB code (M12)
    background.add_task(process_scan, scan_id)               # mock now, real pipeline later
    return {"scan_id": scan_id, "status": "processing"}
```

- Needs `pip install python-multipart` for file uploads. Define request/response shapes with **Pydantic** models; FastAPI then documents everything at `http://localhost:8000/docs` for free.
- Week 3 version: `process_scan` just waits 3 seconds and stores `mock_result.json`. The website team (you) can build the whole flow with it.
- Passwords: hash with **argon2** (`argon2-cffi`), never store them plain. Tokens: JWT with `PyJWT`, short expiry.
- **Done when:** every endpoint has a pytest using FastAPI's `TestClient`.

### M12 — `db`: database

Tables are listed in the Master Build Plan (section 6 there). SQLite on your laptop, PostgreSQL in production: the same code works on both through SQLAlchemy.

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    scans: Mapped[list["Scan"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(default="processing")
    user: Mapped[User] = relationship(back_populates="scans")
```

- Every schema change goes through Alembic: `alembic revision --autogenerate -m "add scans"` then `alembic upgrade head`. Never edit the database by hand.
- The database URL comes from an environment variable (`DATABASE_URL`), never from the code.
- **Done when:** a test creates a user, two scans and measurements, deletes the user, and checks that everything else was deleted too.

### M13 — `reports`: the PDF

Follow the page layout in the Master Build Plan (section 7). Build it from `mock_result.json` first.

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table

def build_report(result: dict, out_path: str) -> None:
    styles = getSampleStyleSheet()
    story = [Paragraph("VitalScan — Health Assessment (research estimate)", styles["Title"]),
             Spacer(1, 12),
             Table([["Vital", "Value", "Normal range", "Confidence"],
                    ["Heart rate", f"{result['hr']:.0f} bpm", "60–100 bpm", f"{result['hr_conf']:.0%}"]]),
             Spacer(1, 12),
             Image("outputs/pulse_plot.png", width=450, height=150),   # made with matplotlib
             Paragraph("For education and research only. Not a medical device.", styles["Italic"])]
    SimpleDocTemplate(out_path, pagesize=A4).build(story)
```

- Use our own name and colours. **Never** Glenmark's or CarePlix's logo, name or licence line.
- **Done when:** the PDF looks right with normal values, with a rejected (low quality) scan, and with very long user names.

### M14 — `frontend`: the website

Pages: Home → Sign up / Log in → Consent → Profile → **Scan** → Results → History. Plain HTML + CSS + JavaScript, served by FastAPI, is enough; add a framework later only if you feel confident.

```javascript
// Scan page: open the front camera and record 30 seconds
const stream = await navigator.mediaDevices.getUserMedia({
  video: { facingMode: "user", width: 640, height: 480, frameRate: 30 }, audio: false,
});
document.querySelector("video").srcObject = stream;

const type = MediaRecorder.isTypeSupported("video/webm") ? "video/webm" : "video/mp4"; // Safari = mp4
const recorder = new MediaRecorder(stream, { mimeType: type });
const chunks = [];
recorder.ondataavailable = (e) => chunks.push(e.data);
recorder.onstop = async () => {
  const form = new FormData();
  form.append("video", new Blob(chunks, { type }), "scan");
  const res = await fetch("/scans", { method: "POST", body: form,
                                      headers: { Authorization: `Bearer ${token}` } });
  const { scan_id } = await res.json();
  pollUntilDone(scan_id);           // GET /scans/{id} every 2 s until status is "done"
};
recorder.start();
setTimeout(() => recorder.stop(), 30_000);
```

- The camera only works on `https://` pages or `localhost`. That's why production needs HTTPS.
- Show a face-outline overlay and a 30-second countdown, and tell the user to sit still in good light.
- Results page: big numbers with confidence bars, the "Experimental estimate" badge on BP, a Chart.js trend graph of history, and a *Download PDF* button.
- Test on Chrome (Windows, Android) and Safari (iPhone) early; Safari behaves differently.

### Deployment (weeks 9–10)

1. Write a `Dockerfile` for the backend (Python 3.11 slim image, install the package, run `uvicorn`).
2. Create a free PostgreSQL database (Neon or Supabase), copy its URL into the host's environment variables.
3. Deploy the container (Hugging Face Spaces Docker or Render), confirm HTTPS works, run `alembic upgrade head`.
4. Run the security checklist in the Master Build Plan (section 8) before inviting any real users.

## 7. Sidd guide — Signal & integration lead

You own the signal core that turns colour traces into vitals (M5–M7), the pipeline that joins everyone's work (M10), the evaluation that produces the paper's numbers (M15), and the team itself. Until Member 2's ROI traces arrive, build against synthetic signals and UBFC's ground-truth PPG.

### Week 1–2: the scaffolding only you can do

- [ ] Repo, CI, branch protection, Projects board (Master Build Plan, section 4)
- [ ] `docs/contracts.md` + `tests/fixtures/mock_result.json` + `tests/fixtures/sample_traces.npz`
- [ ] `training/synthetic.py`: makes fake RGB traces with a known heart rate, so every signal function can be tested against a known answer:

```python
def synthetic_traces(hr_bpm: float = 72, seconds: float = 30, fps: float = 30,
                     noise: float = 0.3, seed: int = 0) -> np.ndarray:
    """Fake (N, 3) RGB trace: a pulse mostly in green, plus light drift and noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * fps)) / fps
    pulse = np.sin(2 * np.pi * hr_bpm / 60 * t)
    drift = 0.5 * np.sin(2 * np.pi * 0.05 * t)                # slow lighting change
    base = np.array([150.0, 110.0, 90.0])                      # typical skin R, G, B
    weights = np.array([0.3, 1.0, 0.15])                       # pulse strongest in green
    return base + np.outer(pulse, weights) + drift[:, None] * 2 + rng.normal(0, noise, (len(t), 3))
```

### M5 — `rppg`: RGB traces → one pulse wave

Implement all three; the comparison between them is RQ1.

- **GREEN:** just the green channel, normalised: `g / g.mean() - 1`.
- **CHROM** (de Haan & Jeanne 2013): normalise each channel by its mean, then `X = 3R − 2G`, `Y = 1.5R + G − 1.5B`, band-pass both, `S = X − (std(X) / std(Y)) · Y`.
- **POS** (Wang et al. 2017), with overlap-add over short windows:

```python
def pos(rgb: np.ndarray, fps: float, window_s: float = 1.6) -> np.ndarray:
    """Plane-Orthogonal-to-Skin pulse extraction. rgb: (N, 3) -> pulse (N,)."""
    n, l = len(rgb), int(window_s * fps)
    projection = np.array([[0.0, 1.0, -1.0], [-2.0, 1.0, 1.0]])
    pulse = np.zeros(n)
    for start in range(0, n - l + 1):
        window = rgb[start:start + l].T                          # (3, l)
        normed = window / window.mean(axis=1, keepdims=True)     # temporal normalisation
        s = projection @ normed                                  # (2, l)
        h = s[0] + (s[0].std() / (s[1].std() + 1e-9)) * s[1]    # alpha tuning
        pulse[start:start + l] += h - h.mean()                   # overlap-add
    return pulse
```

**Done when:** on synthetic traces, all three methods find the true HR within 1 bpm, and POS still does at high noise.

### M6 — `signal_processing`

1. **Resample** to a steady 30 Hz using the real timestamps from M1 (`np.interp`). Browser videos have uneven frame times, and the FFT assumes even spacing.
2. **Detrend** (`scipy.signal.detrend`, or the smoothness-priors method of Tarvainen et al. for a better result).
3. **Band-pass** 0.7–4 Hz, Butterworth order 3, applied with `filtfilt` (no time shift).
4. **SNR** (de Haan's definition): power within ±0.1 Hz of the HR peak and of its first harmonic, divided by all other power in 0.7–4 Hz, in dB. This number becomes the confidence score.
5. **Peaks:** `scipy.signal.find_peaks` with a minimum distance of 0.25 s (no faster than 240 bpm).

### M7 — `vitals`

- **HR:** the FFT peak over the whole clip, plus a sliding 10 s window to see if it is stable. Cross-check against `60 / mean(peak intervals)`; if the two disagree by more than 5 bpm, lower the confidence.
- **RR:** breathing slowly changes the pulse's baseline and amplitude. Look for the strongest frequency in 0.1–0.5 Hz (6–30 breaths/min) of the detrended (not band-passed) signal. A second source is the slow up-and-down motion of the face landmarks; compare both.
- **HRV:** SDNN, RMSSD, pNN50 from peak-to-peak intervals, after removing intervals that differ by more than 20% from their neighbours. Mark as experimental.
- **Confidence:** combine SNR, the M4 quality scores and the two-method agreement into a 0–1 number. Keep the formula simple and document it, since you'll defend it in the viva.
- **Check your HRV/peak code** against HeartPy or NeuroKit2 on the same signal.

### M10 — `pipeline` and M15 — `evaluation`

- Week 3: the **walking skeleton** (every stage a stub with the real interface), so the whole system runs end to end from early on. Swap in real stages as teammates finish them.
- Each stage logs its time; the full pipeline must handle a 30 s clip in under \~30 s on a normal CPU.
- Evaluation script: for every dataset video, run the pipeline in 30 s windows, compare with the ground-truth HR from the reference PPG, and save a CSV. A second script turns the CSV into the paper's tables (MAE, RMSE, Pearson r) and Bland–Altman plots.
- Before trusting your numbers, run **rPPG-Toolbox** or **pyVHR** on the same UBFC videos as a sanity check. If our POS is far worse than theirs, there's a bug.

### Lead duties (about 4 hours a week)

- Review every PR within 24 hours. Be specific and kind ("this crashes when the face is lost at frame 0, add a test"), never just "looks wrong".
- Run the weekly sync (section 9), update the board, and unblock people by adding fixtures or clarifying contracts.
- Own the shared Drive, dataset access requests, and the ethics/consent paperwork with the project guide.
- Keep a running `docs/decisions.md`: date, decision, why. It writes half the thesis methodology chapter for you.

## 8. Google Colab for weak laptops

Colab is a free Jupyter notebook running on Google's computers, with a GPU if you ask for one. Anything heavy (whole datasets, model training) runs there; your laptop only edits code and pushes it to GitHub.

**First-time setup (15 minutes):**

1. Open colab.research.google.com with your Google account. *File → New notebook*.
2. For training: *Runtime → Change runtime type → T4 GPU*. For dataset processing (MediaPipe, feature extraction) the CPU runtime is usually enough, and it saves your GPU quota.
3. Accept Sidd's invite to the shared Drive folder `vitalscan/`, then in Drive right-click it → *Organize → Add shortcut* → *My Drive*, so it appears in your Colab.

**The standard first cells of every notebook:**

```python
# 1. Connect Drive (datasets + outputs live here)
from google.colab import drive
drive.mount("/content/drive")
DATA = "/content/drive/MyDrive/vitalscan/datasets"
OUT = "/content/drive/MyDrive/vitalscan/outputs"

# 2. Get the latest team code (private repo -> use a GitHub token stored in Colab Secrets)
from google.colab import userdata
token = userdata.get("GITHUB_TOKEN")
!git clone -q https://{token}@github.com/<team-org>/vitalscan.git
%cd vitalscan
!pip install -q -e backend

# 3. Run a script from the repo - the logic lives in the repo, not in the notebook
!python training/train_bp.py --data {DATA}/pulsedb --out {OUT}/bp_v1 --seed 42
```

Create the token on GitHub (*Settings → Developer settings → Fine-grained tokens*, read-only access to the repo) and add it in Colab's key icon (*Secrets*) as `GITHUB_TOKEN`. Never type a token directly into a notebook cell.

**Rules that save you pain:**

- **Notebooks stay thin.** Real code goes in `training/` or `evaluation/` as `.py` files, reviewed through PRs like everything else. A notebook only calls them and plots results.
- **Colab disconnects** after about 90 minutes idle and after several hours in total on the free tier. Save checkpoints and partial results to Drive regularly, and make scripts resume from where they stopped.
- **Copy big datasets to the local Colab disk** at the start (`!cp -r {DATA}/ubfc /content/ubfc`). Reading thousands of small files straight from Drive is very slow.
- **GPU quota is limited** and varies. If you run out, use **Kaggle Notebooks** (free GPU with a weekly allowance) with the same scripts.
- **Record every run:** date, git commit, parameters, results, in `docs/experiments/` or a shared sheet. If a result isn't recorded, it can't go in the paper.
- **Don't download datasets to personal laptops.** One copy in the shared Drive, used by everyone.

## 9. Staying on track

The project stays on track with three habits: one short sync a week, every task as a GitHub issue, and a clear "done" rule. If something isn't an issue on the board, it isn't happening.

**Weekly rhythm**

| When | What | Who | Time |
| --- | --- | --- | --- |
| Monday | Pick this week's issues from the board, move them to *In progress* | Each person | 10 min |
| Daily | One-line update in the group chat: *done yesterday / doing today / blocked by* | Each person | 2 min |
| Wednesday | Pair programming on the hardest open problem | Two people, rotating | 1 hour |
| Friday or Saturday | Sync call: demo what works (show it running, not slides), plan next week, update the board | All three | 30–45 min |
| Weeks 1–4 | Teaching session (topics in the Master Build Plan, section 3) | Sidd leads | 90 min |

**Definition of done** — an issue is closed only when all of these are true:

- [ ] The code is merged into `main` through a reviewed PR
- [ ] It has at least one test, and CI is green
- [ ] The module README says what it does, its inputs and outputs, and has an example
- [ ] It handles the obvious failure (empty input, missing file, no face) with a clear error, not a crash
- [ ] For experiments: the result is written in `docs/experiments/` with the commit hash

**How to ask for help (so you get a fast answer):** post in the group chat with (1) what you're trying to do, (2) what you tried, (3) the exact error text or a screenshot, (4) the branch name. "It's not working" gets no answer; this format gets one in minutes.

**Monthly checkpoints** — if a checkpoint slips by more than a week, the team cuts scope rather than adding late nights:

| By | Checkpoint | If it slips, cut first |
| --- | --- | --- |
| End of Nov 2026 | Everyone has merged PRs; the pulse demo works for all three; mock API + skeleton pipeline run end to end | Nothing: this is the foundation |
| End of Dec 2026 | Real ROI traces + POS give HR from our own videos; DB + login work | CHROM comparison moves to January |
| End of Jan 2027 | UBFC HR results table; first BP model; PDF from real results | CNN-LSTM BP model (keep the tree models) |
| End of Feb 2027 | End-to-end demo on the live website | Browser-side processing stretch goal; respiratory rate if unstable |
| End of Mar 2027 | Public beta with volunteers; calibration data collected | Per-user calibration study (RQ5) becomes "future work" |
| Mid-Apr 2027 | Paper submitted, thesis draft done | — |

**Warning signs to raise immediately:** a PR open for more than 3 days; someone silent in the chat for 2 days; a module whose contract keeps changing; "it works on my laptop" but not in CI. Each one costs a week if ignored, and an hour if caught early.

## 10. Resource library

Everything here is free. The *For* column says who needs it; "All" means everyone in weeks 1–2.

| Topic | Resource | For |
| --- | --- | --- |
| Python | [CS50's Introduction to Programming with Python (CS50P)](https://cs50.harvard.edu/python/) — videos + problem sets | All |
| Python | [Official Python tutorial](https://docs.python.org/3.11/tutorial/) | All |
| Python | [Kaggle Learn: Python, Pandas, Intro to Machine Learning](https://www.kaggle.com/learn) — short, in-browser | All / Member 2 |
| Python | [Real Python](https://realpython.com/) — articles on dataclasses, logging, pytest | All |
| Tools | [The Missing Semester (MIT)](https://missing.csail.mit.edu/) — shell, Git, debugging | All |
| Git | [Pro Git book, chapters 1–3](https://git-scm.com/book/en/v2) | All |
| Git | [GitHub Skills](https://skills.github.com/) — interactive courses inside GitHub | All |
| Git | [GitHub Student Developer Pack](https://education.github.com/pack) | All |
| NumPy | [NumPy: the absolute basics for beginners](https://numpy.org/doc/stable/user/absolute_beginners.html) | All |
| Plots | [Matplotlib quick start](https://matplotlib.org/stable/users/explain/quick_start.html) | All |
| Testing | [pytest: get started](https://docs.pytest.org/en/stable/getting-started.html) | All |
| OpenCV | [OpenCV-Python tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html) | Member 2 |
| MediaPipe | [Face Landmarker guide for Python](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python) (model file under *Models* on the [overview page](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/index#models)) | Member 2 |
| ML | [scikit-learn: getting started](https://scikit-learn.org/stable/getting_started.html) and [GroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html) | Member 2 |
| ML | [XGBoost docs](https://xgboost.readthedocs.io/) · [LightGBM docs](https://lightgbm.readthedocs.io/) | Member 2 |
| ML | [ONNX Runtime docs](https://onnxruntime.ai/docs/) · [skl2onnx](https://onnx.ai/sklearn-onnx/) | Member 2 |
| Colab | [Google Colab](https://colab.research.google.com/) · [Kaggle Notebooks](https://www.kaggle.com/code) as backup | Member 2, Sidd |
| Web | [MDN: Learn web development](https://developer.mozilla.org/en-US/docs/Learn) | Member 3 |
| Web | [MDN: getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia) · [MDN: MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder) | Member 3 |
| Web | [freeCodeCamp](https://www.freecodecamp.org/learn) — Responsive Web Design, JavaScript | Member 3 |
| Web | [Chart.js docs](https://www.chartjs.org/docs/latest/) | Member 3 |
| API | [FastAPI tutorial — user guide](https://fastapi.tiangolo.com/tutorial/) | Member 3, Sidd |
| SQL | [SQLBolt](https://sqlbolt.com/) — interactive SQL lessons | Member 3 |
| SQL | [PostgreSQL tutorial (official)](https://www.postgresql.org/docs/current/tutorial.html) | Member 3 |
| ORM | [SQLAlchemy 2.0 unified tutorial](https://docs.sqlalchemy.org/en/20/tutorial/) · [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) | Member 3 |
| PDF | [ReportLab Platypus chapter](https://docs.reportlab.com/reportlab/userguide/ch5_platypus/) · [full user guide (PDF)](https://www.reportlab.com/docs/reportlab-userguide.pdf) | Member 3 |
| Deploy | [Docker: get started](https://docs.docker.com/get-started/) | Member 3 |
| Signal | [SciPy signal processing guide](https://docs.scipy.org/doc/scipy/tutorial/signal.html) | Sidd |
| Signal | [HeartPy docs](https://python-heart-rate-analysis-toolkit.readthedocs.io/) · [NeuroKit2 docs](https://neuropsychology.github.io/NeuroKit/) — to cross-check peaks and HRV | Sidd |
| rPPG code | [rPPG-Toolbox (Univ. of Washington)](https://github.com/ubicomplab/rPPG-Toolbox) — reference implementations + dataset loaders | Sidd, Member 2 |
| rPPG code | [pyVHR](https://github.com/phuselab/pyVHR) — Python framework with GREEN/CHROM/POS | Sidd |
| Dataset | [UBFC-rPPG](https://sites.google.com/view/ybenezeth/ubfcrppg) — face videos + ground-truth PPG | Sidd, Member 2 |
| Dataset | [PulseDB on GitHub](https://github.com/pulselabteam/PulseDB) — PPG/ECG/ABP segments for BP models; [paper](https://www.frontiersin.org/articles/10.3389/fdgth.2022.1090854) | Member 2 |
| Dataset | [VitalVideos-Europe paper](https://arxiv.org/abs/2306.11891) — face videos with PPG and BP ground truth; request access from the authors | Member 2, Sidd |
| Dataset | PURE (TU Ilmenau) — request by email to the dataset authors; Sidd sends the request in week 1 | Sidd |
| Papers | Wang et al. 2017 (POS), de Haan & Jeanne 2013 (CHROM), Poh/McDuff/Picard 2010–11 — DOIs in the project literature table | All |
| Paper writing | [Overleaf](https://www.overleaf.com/) (IEEE conference template) · [Zotero](https://www.zotero.org/) for references | All |

Dataset, MediaPipe, ReportLab and rPPG-code links were checked on 24 Oct 2026; the rest are long-standing official pages. If one breaks, search the resource name: these projects move pages, not content.

## 11. Glossary

| Term | Plain meaning |
| --- | --- |
| rPPG | Remote photoplethysmography: measuring the pulse from skin-colour changes in a camera video |
| PPG | The same signal measured by a clip on the finger (pulse oximeter); used as "ground truth" |
| ROI | Region of interest: the patch of skin we average (forehead, cheeks) |
| Landmarks | Fixed points on the face (MediaPipe gives 478) used to place the ROIs |
| Trace | A value per frame over time, e.g. the forehead's average green value for 900 frames |
| GREEN / CHROM / POS | Three ways of combining R, G, B into one pulse signal; POS usually handles motion and lighting best |
| fps | Frames per second; our target is 30 |
| Detrend | Removing slow drift (e.g. light slowly changing) from a signal |
| Band-pass filter | Keeps only frequencies in a range; for pulse, 0.7–4 Hz (42–240 bpm) |
| FFT | Fast Fourier Transform: finds which frequencies are in a signal; the strongest one in the pulse band is the heart rate |
| SNR | Signal-to-noise ratio: how much stronger the pulse is than the noise; our main confidence input |
| HR / RR | Heart rate (beats/min) / respiratory rate (breaths/min) |
| HRV, SDNN, RMSSD, pNN50 | Heart-rate variability: how much the time between beats changes; three standard ways to measure it |
| SBP / DBP / MAP | Systolic (top) / diastolic (bottom) blood pressure / mean arterial pressure |
| Feature | A number computed from the signal (e.g. pulse rise time) that a model learns from |
| MAE / RMSE / r | Mean absolute error / root-mean-square error / Pearson correlation: how close estimates are to the truth |
| Bland–Altman plot | A plot of the difference vs the average of two methods; the standard way to compare a new measurement method |
| Subject leakage | The same person in both training and test data, making a model look better than it is |
| GroupKFold / LOSO | Cross-validation that keeps each person's data in only one fold / leave-one-subject-out |
| ONNX | A file format for trained models that runs fast on any CPU with ONNX Runtime |
| API / endpoint | The URLs the website calls on our server, e.g. `POST /scans` |
| ORM | Object-relational mapper (SQLAlchemy): write Python classes instead of raw SQL |
| Migration | A versioned, repeatable change to the database structure (Alembic) |
| Mock / fixture / stub | Fake data or fake functions with the real shape, so we can build and test before the real part exists |
| Contract | The agreed format of data passed between two modules (`docs/contracts.md`) |
| CI | Continuous integration: GitHub automatically runs tests and lint on every PR |
| PR | Pull request: asking for your branch to be reviewed and merged into `main` |
