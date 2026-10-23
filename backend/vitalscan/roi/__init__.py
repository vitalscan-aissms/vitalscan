"""M3 roi: Forehead + cheek polygons from landmarks, YCrCb skin mask, mean R,G,B per ROI
per frame.

Owner: Member 2. Inputs: frames + landmarks.
Outputs: RGB traces (N, 3, 3) + valid (N, 3) bool.
See README.md in this folder and docs/contracts.md.
"""
