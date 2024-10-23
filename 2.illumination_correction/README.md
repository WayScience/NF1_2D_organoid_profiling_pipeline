# Generate and save illumination correction images

In this module, we use CellProfiler to calculate an illumination correction (IC) function per channel that is based on each image.
We then save the corrected images as 16-bit integer TIFF files.

There are 520 images from one plate to process, which is actually only 104 image sets in total (because of multiple z stacks per organoid).
It took approximately **~5 minutes** to generate IC functions and save corrected images.
We are using a Linux-based machine running Pop_OS! LTS 22.04 with an AMD Ryzen 7 3700X 8-Core Processor with 16 CPUs and 125 GB of MEM.

## Perform illumination correction

To perform illumination correction, use the below command:

```bash
# make sure you are in the 2.illumination_correction directory
source run_IC.sh
```
