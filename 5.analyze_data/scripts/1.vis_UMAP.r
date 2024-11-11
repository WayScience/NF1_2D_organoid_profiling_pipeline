suppressPackageStartupMessages(library(ggplot2)) #plotting
suppressPackageStartupMessages(library(dplyr)) #work with data frames
suppressPackageStartupMessages(library(RColorBrewer)) # colors for plotting

# Set directory and file structure
umap_dir <- "results"
output_fig_dir <- "figures"
# Create the figures directory if it does not exist
if (!dir.exists(output_fig_dir)) {
  dir.create(output_fig_dir, recursive = TRUE)
}
umap_files <- list.files(umap_dir, pattern = "\\.tsv$", full.names = TRUE)

# Define prefix for constructing paths
umap_prefix <- "UMAP_"

# Build dictionary of output paths
output_umap_files <- setNames(
    lapply(umap_files, function(file) {
        plate <- sub("^.*UMAP_(.*)\\.tsv$", "\\1", file)
        file.path(output_fig_dir, paste0(umap_prefix, plate))
    }),
    sapply(umap_files, function(file) {
        sub("^.*UMAP_(.*)\\.tsv$", "\\1", file)
    })
)

print(output_umap_files)

# Load data
umap_cp_df <- list()
for (plate in names(output_umap_files)) {
    # Find the umap file associated with the plate
    umap_file <- umap_files[stringr::str_detect(umap_files, plate)]
    
    # Load in the umap data
    df <- readr::read_tsv(
        umap_file,
        col_types = readr::cols(
            .default = "d",
            "Metadata_Plate" = "c",
            "Metadata_Well" = "c",
            "Metadata_Site" = "c",
            "Metadata_treatment" = "c",
            "Metadata_dose" = "c",
            "Metadata_ZSlice" = "c",
        )
    )
    
    # Create the Metadata_treatment_dose column and ZSlice_Number column
    df <- df %>%
        mutate(
            Metadata_treatment_dose = paste(Metadata_treatment, Metadata_dose, sep = "_"),
            ZSlice_Number = substr(Metadata_ZSlice, nchar(Metadata_ZSlice) - 1, nchar(Metadata_ZSlice))
        )

    # Count cells per well
    well_counts <- df %>%
        group_by(Metadata_Well) %>%
        summarise(well_cell_count = n(), .groups = 'drop')

    # Join the counts back to the original dataframe
    df <- df %>%
        left_join(well_counts, by = "Metadata_Well")

    # Append the data frame to the list
    umap_cp_df[[plate]] <- df 
}

# Define a custom color palette
color_palette <- c(
  "Mirdametinib_1" = "#1f77b4",       # Light blue
  "Mirdametinib_10" = "#1f47b4",      # Darker blue
  "Everolimus_1" = "#ff7f0e",         # Bright orange
  "Imatinib_1" = "#bcbd22",           # Olive green (light)
  "Linsitinib_1" = "#2ca02c",         # Light green
  "DMSO_1" = "#9467bd",               # Light purple
  "Cabozantinib_1" = "#5b3e2f",       # Darker brown
  "Onalespib_1" = "#9edae5",          # Softer cyan
  "Fimepinostat_1" = "#7f7f7f",       # Gray
  "Trametinib_1" = "#17becf",         # Cyan
  "Trametinib_10" = "#0091b0",        # Darker cyan for 10
  "Selumetinib_1" = "#e377c2",        # Light pink
  "Selumetinib_10" = "#d5006d",       # Dark pink for 10
  "Rapamycin_1" = "#ff6f61",          # Coral pink
  "Copanlisib_1" = "#ffbb78",         # Light orange for 1
  "Binimetinib_1" = "#ff9896",        # Light red
  "Binimetinib_10" = "#d62728",       # Dark red for 10
  "Ketotifen_1" = "#98df8a",          # Light green
  "Nilotinib_1" = "#c5b0d5",          # Lavender
  "Digoxin_1" = "#ffb3e6",            # Light lavender pink
  "STAURO_10" = "#b46a61"             # Darker brown for 10
)

# Define the Viridis colors manually
viridis_colors <- c(
    "#440154", "#482878", "#3e4a8a", "#31688e", 
    "#26828e", "#1f9e89", "#5ec962", "#b3d86e", 
    "#fde724"
)

for (plate in names(umap_cp_df)) {
    # Genotype UMAP file path
    treatment_output_file <- paste0(output_umap_files[[plate]], "_treatment.png")

    # UMAP labeled with treatment and dose
    treatment_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = Metadata_treatment_dose), size = 2, alpha = 0.6, show.legend = TRUE
        )
        + scale_color_manual(values = color_palette)  # Use custom color palette
        + theme_bw()
        + labs(color = "Treatment and Dose")  # Change legend title
        + theme(
            legend.position = "left"
        )
    )
    
    ggsave(treatment_output_file, treatment_gg, dpi = 500, height = 6, width = 10)

    # UMAP for well cell count
    well_cell_count_output_file <- paste0(output_umap_files[[plate]], "_well_cell_count.png")

    well_cell_count_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = well_cell_count), size = 2, alpha = 0.6, show.legend = TRUE
        )
        + scale_color_gradientn(colors = viridis_colors, name = "Cell Count")  # Use manually defined colors
        + theme_bw()
        + theme(
            legend.position = "left"
        )
    )

    ggsave(well_cell_count_output_file, well_cell_count_gg, dpi = 500, height = 6, width = 10)
    
    # UMAP for ZSlice_Number in green gradient
    zslice_output_file <- paste0(output_umap_files[[plate]], "_zslice.png")

    zslice_gg <- (
        ggplot(umap_cp_df[[plate]], aes(x = UMAP0, y = UMAP1))
        + geom_point(
            aes(color = as.numeric(ZSlice_Number)), size = 2, alpha = 0.6, show.legend = TRUE
        )
        + scale_color_gradient(low = "lightgreen", high = "darkgreen", name = "ZSlice Number")  # Green gradient
        + theme_bw()
        + theme(
            legend.position = "left"
        )
    )

    ggsave(zslice_output_file, zslice_gg, dpi = 500, height = 6, width = 10)
}
