# Download data

In this module, we will provide instructions for how to download the datasets once publicly available.

## Restructure images for preliminary data

For the pilot data, we use a notebook to reformat the file structure to work for CellProfiler processing.
Currently, images are nested deeply within multiple folders, which is not our standard for processing one plate of images.
We create a new folder in a parent directory (still slightly nested) that we copy the images to, called `NF0014`.
We copy the images using `shutil.copy2()` to preserve the metadata and keep the original data in tact.

It takes ~20 minutes to copy 20,421 images to the `NF0014` folder.

## Platemap visualization

For every plate of data, we create a platemap visualization that shows how the treatments or other relevant data are distributed across the plate.
We use R, specifically the `platetools` library to generate these plots and save as PNGs.

## Perform restructure and visualization

To perform both tasks as mentioned above, use the [update_and_visualize.sh script](./update_and_visualize.sh) using the command below:

_NOTE_: There could be issues with running the R script in terminal (like issues with saving with `ggsave`), so please be prepared for any troubleshooting or just use the jupyter notebook by itself with the R environment.

## For this use case we already have these image data processed. To process the data run the preprocessing from the 3D image based profiling module.


```bash
# make sure you are in the 0.download_data directory
source update_and_visualize.sh
```
