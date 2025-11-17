import os
import pickle
import numpy as np
import torch
from smplx import SMPLX
from measure import MeasureBody
from measurement_definitions import STANDARD_LABELS

def round_measurements(data: dict):
    """Round all values to 2 decimals"""
    return {k: round(float(v), 2) for k, v in data.items()}

def load_pixie_pkl(pkl_path: str):
    with open(pkl_path, "rb") as f:
        params = pickle.load(f)
    return params

def build_canonical_smplx(params, smplx_model_dir: str):
    """
    Convert PIXIE .pkl output → Canonical SMPL-X mesh
    """
    # PIXIE shape = 200 components, SMPL-X uses 10
    betas = torch.tensor(params["shape"][:10]).float().unsqueeze(0)

    # Zero pose everywhere
    body_pose = torch.zeros((1, 63))
    global_orient = torch.zeros((1, 3))
    jaw_pose = torch.zeros((1, 3))
    leye_pose = torch.zeros((1, 3))
    reye_pose = torch.zeros((1, 3))
    left_hand_pose = torch.zeros((1, 45))
    right_hand_pose = torch.zeros((1, 45))
    expression = torch.zeros((1, 10))

    # Load SMPL-X Model
    model = SMPLX(
        model_path=smplx_model_dir,
        gender="female",          # Change to "neutral" if required
        use_pca=False
    )

    output = model(
        betas=betas,
        body_pose=body_pose,
        global_orient=global_orient,
        jaw_pose=jaw_pose,
        leye_pose=leye_pose,
        reye_pose=reye_pose,
        left_hand_pose=left_hand_pose,
        right_hand_pose=right_hand_pose,
        expression=expression
    )

    verts = output.vertices[0].detach().cpu().numpy()
    return verts


def measure_body(verts: np.ndarray, height_cm: float):
    """
    Runs SMPL Anthropometry measurements
    """
    verts_t = torch.tensor(verts).float().unsqueeze(0)

    measurer = MeasureBody("smplx")
    measurer.from_verts(verts_t)

    # Run all default measurements
    names = measurer.all_possible_measurements
    measurer.measure(names)

    # Label the output
    measurer.label_measurements(STANDARD_LABELS)

    # Height normalization
    measurer.height_normalize_measurements(height_cm)

    # APPLY ROUNDING (2 decimals)
    mesh = round_measurements(measurer.measurements)
    scaled = round_measurements(measurer.height_normalized_measurements)

    return {
        "mesh_measurements": mesh,
        "scaled_measurements": scaled
    }


def run_full_pipeline(pkl_path: str, height_cm: float):
    params = load_pixie_pkl(pkl_path)

    verts = build_canonical_smplx(
        params=params,
        smplx_model_dir="/workspace/SMPL-Anthropometry/models/smplx"
    )

    result = measure_body(verts, height_cm)
    return result
