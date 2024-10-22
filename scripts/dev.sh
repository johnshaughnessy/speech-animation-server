PROJECT_DIR=$(realpath $0 | xargs dirname | xargs dirname)
source $PROJECT_DIR/scripts/log.sh

export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 # Otherwise, conda commands fail.

# Check if the current conda environment is the correct one
# The current conda environment can be checked by running `conda env list`
current_env=$(conda env list | grep -oP '(?<=\* ).*')
# We only want the environment name, which is after the last slash
current_env=${current_env##*/}

# The two previous commands can be combined into one:
current_env=$(conda env list | grep -oP '(?<=\* ).*' | grep -oP '[^/]*$')

# It should begin with "speech-animation-server" (but might be "speech-animation-server-rocm" or "speech-animation-server-cuda").
# If it doesn't, warn the user and exit
if [[ ! $current_env =~ ^speech-animation-server.* ]]; then
    log "info" "Current conda environment: $current_env"
    log "error" "A conda environment for speech-animation-server must be active:"
    log "warn" "    conda activate speech-animation-server-rocm"
    log "warn" "    conda activate speech-animation-server-cuda"
    exit 1
fi

pkill -f "python -m speech.app" -9
sleep 1.5

if [ -d "/opt/rocm" ]; then
    log "info" "ROCM is installed, setting up environment variables for ROCm"
    export PYTORCH_ROCM_ARCH="gfx1030"
    export HSA_OVERRIDE_GFX_VERSION=10.3.0
    export HIP_VISIBLE_DEVICES=0
    export ROCM_PATH=/opt/rocm
    log "info"  "PYTORCH_ROCM_ARCH: $PYTORCH_ROCM_ARCH"
    log "info" "HSA_OVERRIDE_GFX_VERSION: $HSA_OVERRIDE_GFX_VERSION"
    log "info" "HIP_VISIBLE_DEVICES: $HIP_VISIBLE_DEVICES"
    log "info" "ROCM_PATH: $ROCM_PATH"
fi

SPEECH_ENV=development python -m speech.app "$@"
