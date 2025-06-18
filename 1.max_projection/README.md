# Generate max-projection image sets

In this module, we use python to perform max z projection and to get the middle most z-slice of the image sets for all patients.
It took approximately **five minutes** to generate the maximum projected image sets in one patient [parallel processing was used].
We are using a Linux-based machine running Pop_OS! LTS 22.04 with an AMD Ryzen 7 3700X 8-Core Processor. There is a total of 16 CPUs with 125 GB of MEM.

## Perform check and maximum projection

To perform max projection, use the below command:

```bash
# make sure you are in the 1.max_projection directory
source check_and_max_proj.sh
```
