#  Copyright 2022 Diagnostic Image Analysis Group, Radboudumc, Nijmegen, The Netherlands
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import json
import os
from tqdm import tqdm

from picai_prep.data_utils import PathLike


def generate_mha2nnunet_settings(
    archive_dir: PathLike = "tests/output-expected/mha/ProstateX/",
    output_path: PathLike = "tests/output/mha2nnunet_settings.json"
):
    """
    Create mha2nnunet_settings.json for ProstateX sample (without annotations)
    """
    ignore_files = [
        ".DS_Store",
        "LICENSE",
    ]

    archive_list = []

    # traverse MHA archive
    for patient_id in tqdm(sorted(os.listdir(archive_dir))):
        # traverse each patient
        if patient_id in ignore_files:
            continue

        # collect list available studies
        patient_dir = os.path.join(archive_dir, patient_id)
        files = os.listdir(patient_dir)
        files = [fn.replace(".mha", "") for fn in files if ".mha" in fn and "._" not in fn]
        subject_ids = ["_".join(fn.split("_")[0:2]) for fn in files]
        subject_ids = sorted(list(set(subject_ids)))

        # check which studies are complete
        for subject_id in subject_ids:
            patient_id, study_id = subject_id.split("_")

            # construct scan paths
            scan_paths = [
                f"{patient_id}/{subject_id}_{modality}.mha"
                for modality in ["t2w", "adc", "hbv"]
            ]
            all_scans_found = all([
                os.path.exists(os.path.join(archive_dir, path))
                for path in scan_paths
            ])

            if all_scans_found:
                # store info for complete studies
                archive_list += [{
                    "patient_id": patient_id,
                    "study_id": study_id,
                    "scan_paths": scan_paths,
                }]

    mha2nnunet_settings = {
        "dataset_json": {
            "task": "Task100_test",
            "description": "bpMRI scans from ProstateX dataset to test mha2nnunet",
            "tensorImageSize": "4D",
            "reference": "",
            "licence": "",
            "release": "0.3",
            "modality": {
                "0": "T2W",
                "1": "CT",
                "2": "HBV"
            },
            "labels": {
                "0": "background",
                "1": "lesion"
            }
        },
        "preprocessing": {
            "matrix_size": [
                20,
                160,
                160
            ],
            "spacing": [
                3.0,
                0.5,
                0.5
            ]
        },
        "archive": archive_list
    }

    with open(output_path, "w") as fp:
        json.dump(mha2nnunet_settings, fp, indent=4)


if __name__ == '__main__':
    generate_mha2nnunet_settings()
