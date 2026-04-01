#!/bin/bash
# from Dave Bunten
# build and run cellprofiler from a docker container
CPDOCKER_RUNDIR=$PWD
CPDOCKER_IMAGE_NAME=cp-docker

# build image
docker build --platform linux/amd64 -t "$CPDOCKER_IMAGE_NAME" -f "$CPDOCKER_RUNDIR/Dockerfile" .

# show the CellProfiler version and use run as a quick test
echo "CellProfiler version:"
docker run --rm --platform linux/amd64 -w /app \
    -v "$CPDOCKER_RUNDIR:/app" \
    "$CPDOCKER_IMAGE_NAME" \
    --version

apptainer build cellprofiler.sif docker-daemon://cp-docker:latest
image_path="$(pwd)/cellprofiler.sif"
alias cellprofiler="apptainer exec '$image_path' cellprofiler"

# write the alias to bashrc and zshrc for future use
echo "alias cellprofiler='apptainer exec '$image_path' cellprofiler'" >> ~/.bashrc
echo "alias cellprofiler='apptainer exec '$image_path' cellprofiler'" >> ~/.zshrc
