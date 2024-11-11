# Perform segmentation and extract morphology features

In this module, we use CellProfiler to segment nuclei, cells, cytoplasm (also known as compartments) and whole organoids.
We then extract morphology features (e.g., texture, granularity, area, etc.) using the compartments as masks across all channels.
We also extract some whole image features, but these are not included in downstream analysis.
We are focused on extracting `single-cell` (nuclei, cells, and cytoplasm) and `whole organoid` (organoids) features.

It took approximately **~3 to 4 hours** to segment and extract features into an SQLite database from 104 image sets (520 images total)
We are using a Linux-based machine running Pop_OS! LTS 22.04 with an AMD Ryzen 7 3700X 8-Core Processor with 16 CPUs and 125 GB of MEM.

## Perform CellProfiler analysis (segmentation and feature extraction)

To perform CellProfiler analysis, use the below command:

```bash
# make sure you are in the 3.feature_extraction directory
source run_analysis.sh
```
