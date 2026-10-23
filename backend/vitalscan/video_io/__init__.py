"""M1 video_io: Decode an uploaded .webm/.mp4 into RGB frames plus real per-frame timestamps.

Owner: Member 2. Inputs: video file path.
Outputs: frames (N, H, W, 3) uint8 RGB, timestamps (N,) in seconds.
See README.md in this folder and docs/contracts.md.
"""
