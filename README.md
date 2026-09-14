# SPAN Corner Test Kit

A behavioral testing framework for automated analysis of animal behavior in corner tests, leveraging DeepLabCut for pose estimation. This tool provides a command-line interface to watch video analysis in real-time or batch-process videos to generate annotated output videos and CSV reports.

![rat_example.gif](images/rat_example.gif)
![mouse_example.gif](images/mouse_example.gif)

## Requirements

- **Operating System:** Linux (recommended, based on file structure) or Windows (some Windows-specific packages in environment.yml).
- **Python:** 3.8.16
- **Package Manager:** Conda (for environment management).
- **Core Dependencies:**
  - DeepLabCut 2.3.4
  - OpenCV
  - Click (CLI)
  - TensorFlow 2.10.0
  - PySide6 (for GUI elements)
  - NumPy, Pandas, Matplotlib
 
### Input Data Requirements

CTAT expects a single animal to be visible throughout the recording. Videos should provide sufficient spatial resolution to clearly distinguish the animal's head and body orientation. Uniform lighting and adequate contrast between the animal and the background are recommended. The software has been validated on SPAN corner test recordings and may require additional model training for substantially different acquisition setups.

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aglee-prog/span_corner_test
    cd span_corner_test
    ```

2.  **Create the Conda environment:**
    ```bash
    conda env create -f conda_env/environment.portable.yml
    ```

3.  **Activate the environment:**
    ```bash
    conda activate DEEPLABCUT_KIT
    ```
### Verifying Correct Installation

To verify correct installation, run the software on one of the example videos included in the repository:
```bash
python span-kit.py watch --path data/example.mp4 --model mice
```
Successful execution should display the analyzed video with pose tracking overlays and detected behavioral events. Running the create command should produce an annotated output video and a CSV report containing detected turns and associated metrics.

### Trained Models

The repository includes pretrained DeepLabCut models for both rat and mouse corner test analysis. The desired model can be selected using the --model argument:
```bash
python span-kit.py watch --path video.mp4 --model rats
```
or
```bash
python span-kit.py watch --path video.mp4 --model mice
```
Users working with substantially different recording conditions, species, or experimental setups may need to retrain the DeepLabCut model using their own annotated data.

### GPU support on Linux

GPU acceleration is optional. The toolkit can run on CPU without CUDA.

The provided environment uses:

- TensorFlow 2.10
- CUDA 11.2
- cuDNN 8.1

On Linux systems that also have a newer system-wide CUDA installation, TensorFlow may fail to detect the CUDA libraries installed inside the Conda environment.

If GPU acceleration is not detected, activate the environment and add its library directory to `LD_LIBRARY_PATH`:

```bash
conda activate DEEPLABCUT_KIT

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
```

### Verifying the installation

The repository ships a ready-to-run example so you can confirm the setup works end to end:

| File | Role |
|------|------|
| `data/video-rats.mp4` | Input example (rat corner test) |
| `data/video-rats-output.mp4` | Expected annotated output |
| `data/report_Sep_14_2026_13_22span.csv` | Expected CSV report (status `OK`) |

1.  **Watch the analysis live:**
    ```bash
    python span-kit.py watch --path data/video-rats.mp4 --model rats
    ```
    A window opens showing the detected pose, the arena ROI, and live turn counts. Press `q` to close.

2.  **Batch-process and export a report** (note: `create` takes a directory):
    ```bash
    python span-kit.py create --path data --model rats
    ```
    This regenerates `data/video-rats-output.mp4` and a timestamped CSV (e.g. `data/report_...span.csv`) in the same directory.

3.  **Compare against the expected output.** The shipped CSV for this example reports:

    ```
    File,Trails,Left turns,Right turns,Left tendency,Right tendency,Detection percent,Satus
    data/video-rats.mp4,10,3,7,8,91,82,OK
    ```

    A successful run gives a status of `OK` (the animal is detected in at least 60% of frames and exactly 10 turns are counted) and an annotated video that matches `data/video-rats-output.mp4`.

> Note: `create` only writes a new report when the `-output.mp4` for that video is absent, so delete `data/video-rats-output.mp4` first if you want to force a fresh run.

## Usage

The main entry point is the `span-kit.py` script.

### CLI Commands

The tool uses `click` for its command-line interface.

#### 1. Watch Analysis
To watch the behavior analysis in real-time for a specific video:
```bash
python span-kit.py watch --path /path/to/video.mp4 --model [rats|mice]
```
- `--path`: Path to the input video file.
- `--model`: Select the model to use (`rats` or `mice`). Default is `mice`.

#### 2. Create Reports
To batch-process videos in a directory, generate annotated output videos, and export CSV reports:
```bash
python span-kit.py create --path /path/to/directory --model [rats|mice]
```
- `--path`: Path to a directory containing `.mp4` files (it will recursively search for videos). Must be a directory, not a single video file.
- `--model`: Select the model to use (`rats` or `mice`). Default is `mice`.

Annotated videos will be saved with an `-output.mp4` suffix. CSV reports will be saved in the same directory with a timestamped filename (e.g., `report_Oct_31_2025_02_16span.csv`).

## Project Structure

- `span-kit.py`: Main CLI entry point.
- `behaviour_tests/`: Contains specific behavioral test implementations.
    - `corner_ext/`: Corner test extension logic, models, and processors.
    - `common/`: Shared processors and themes.
- `classes/`: Core framework classes (Factory, Process, DataExtractors, etc.).
- `conda_env/`: Conda environment configuration files.
- `data/`: Bundled example (input video, expected annotated output, expected CSV report) and generated reports.
- `utils/`: Common utility functions.
- `assets/`: Project assets like logos.

## Troubleshooting

### TensorFlow cannot detect GPU
Verify that the installed CUDA and TensorFlow versions are compatible.

### DLC model not found
Ensure that the trained model files are present in the expected model directory.

### No turns detected
Verify that the correct species model (rats or mice) was selected and that the animal remains visible throughout the recording.

## Contact

For questions about the software or its use, please open a GitHub issue.

For research-related questions, contact:
Vitalii Kuznetsov — [vitalii.kuznetsov.dev@gmail.com]

## License

This project is primarily licensed under the GNU Lesser General Public License v3.0. Note that the software is provided “as is”, without warranty of any kind, express or implied.

