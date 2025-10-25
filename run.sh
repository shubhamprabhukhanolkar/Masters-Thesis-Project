#!/bin/bash
#SBATCH --job-name=data_collection_job
#SBATCH --partition=mtech
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --time=1:00:00
#SBATCH --output=data_collection_%j.log

# --- Environment Setup ---
echo "Initializing Conda..."
# VITAL: Source the conda initialization script
source /csehome/m24cse029/miniconda3/etc/profile.d/conda.sh
if [ $? -ne 0 ]; then
    echo "Failed to source conda.sh. Check the path."
    exit 1
fi

echo "Loading Conda environment..."
conda activate sentiment
if [ $? -ne 0 ]; then
    echo "Failed to activate conda environment 'sentiment'"
    exit 1
fi

# --- Load CUDA Module (Crucial for GPU Node) ---
echo "Loading CUDA module..."
# Replace with the correct module for your HPC if different
module load cuda/12.1.1
if [ $? -ne 0 ]; then
    echo "Failed to load CUDA module"
    # Decide if you want to exit or try CPU-only
    # exit 1
fi

# --- Debugging: Check Environment and PyTorch ---
echo "--- Environment Info ---"
echo "Job running on node: $(hostname)"
echo "Current directory: $(pwd)"
echo "Using Python: $(which python)"
python --version

echo "--- PyTorch Info ---"
# Use python -c to avoid script path issues for this check
python -c "import torch; print(f'PyTorch Version: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version Used by PyTorch: {torch.version.cuda}')"
if [ $? -ne 0 ]; then
    echo "PyTorch import or check failed!"
    # Consider reinstalling PyTorch if this fails consistently
    # exit 1
fi

# --- Run Your Data Collection Script ---
echo "--- Running Data Collection ---"
# IMPORTANT: Define the correct path to your script
# Assuming you submit the job from the Masters-Thesis-Project directory:
SCRIPT_PATH="src/01_data_collection/get_sentiment_data.py"

# Check if the script exists before running
if [ -f "$SCRIPT_PATH" ]; then
    python "$SCRIPT_PATH"
    echo "--- Script Finished ---"
else
    echo "Error: Script not found at $SCRIPT_PATH"
    echo "Make sure you are submitting the job from the 'Masters-Thesis-Project' directory."
    exit 1
fi

# Deactivate environment (good practice)
# conda deactivate