"""M2 face_detection: MediaPipe Face Landmarker (VIDEO mode), 478 landmarks per frame;
flags frames with 0 or 2+ faces.

Owner: Member 2. Inputs: frames + timestamps.
Outputs: landmarks (N, 478, 2) in pixels, one_face (N,) bool.
See README.md in this folder and docs/contracts.md.
"""
