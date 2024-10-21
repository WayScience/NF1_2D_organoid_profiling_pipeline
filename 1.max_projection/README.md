# Generate max-projection image sets

In this module, we use CellProfiler to group the z-slices together per well and site and use maximum projection (taking the highest intensity per pixel) for each channel to create one representative image set.

There are 104 unique wells and sites (1 removed due to incomplete number of channels) with 5 channels each, so we took >20,000 images and reduced it down to 520 images (104 image sets * 5 channels).
It took approximately **one hour** to generate the maximum projected image sets.
We are using a Linux-based machine running Pop_OS! LTS 22.04 with an AMD Ryzen 7 3700X 8-Core Processor. There is a total of 16 CPUs with 125 GB of MEM.

## Perform check and maximum projection

To check/correct for any incomplete image sets per z-slice (missing channels) and perform max projection, use the below command:

```bash
# make sure you are in the 1.max_projection directory
source check_and_max_proj.sh
```
