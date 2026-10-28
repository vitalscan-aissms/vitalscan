"""M8 ml_models: Pulse-shape features (features.py, shared with training) and, later, the
BP ONNX model that predicts an experimental SBP/DBP estimate with an error band.
Training scripts live in training/ and import features from here.

Owner: Member 2. Inputs: pulse features + age/sex/BMI. Outputs: BP estimate + error band.
See README.md in this folder and docs/contracts.md.
"""
