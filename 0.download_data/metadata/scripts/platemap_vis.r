suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(platetools))

platemap_files <- list.files(pattern = "_platemap\\.csv$", full.names = TRUE)
print(platemap_files)

output_fig_dir <- file.path("platemap_figures")
if (!dir.exists(output_fig_dir)) {
    dir.create(output_fig_dir, recursive = TRUE)
}
platemap_suffix <- "_platemap_figure.png"

# Define output figure paths
output_platemap_files <- list()
for (platemap_file in platemap_files) {
    # Extract plate name and remove suffix 
    plate <- basename(platemap_file)
    plate <- stringr::str_remove(plate, "_platemap.csv") 
    
    output_platemap_files[[plate]] <- file.path(output_fig_dir, paste0(plate, platemap_suffix))
}

print(output_platemap_files)

# Load in all platemap CSV files
platemap_dfs <- list()
for (plate in names(output_platemap_files)) {
    # Find the platemap file associated with the plate
    platemap_file <- platemap_files[stringr::str_detect(platemap_files, plate)]
    
    # Load in the platemap data
    df <- readr::read_csv(
        platemap_file,
        col_types = readr::cols(.default = "c")
    )
    
    # Update 'Dose' column
    df <- df %>%
        mutate(
            dose = case_when(
                treatment == "DMSO" ~ paste0(dose, "%"),
                TRUE ~ paste0(dose, " uM")
            )
        )
    
    # Store the updated data frame
    platemap_dfs[[plate]] <- df 
}

# Print the head of each data frame in the list
for (plate in names(platemap_dfs)) {
    cat("\nHead of plate:", plate, "\n")
    print(head(platemap_dfs[[plate]]))
}

for (plate in names(platemap_dfs)) {
    # Output for each plate
    output_file <- output_platemap_files[[plate]]
    
    # Create the platemap plot
    platemap <-
        platetools::raw_map(
            data = platemap_dfs[[plate]]$treatment,
            well = platemap_dfs[[plate]]$well_position,
            plate = 96,
            size = 10 # Shape size in the plot
        ) +
        ggtitle(paste("Platemap layout for plate", plate)) +
        theme(
            plot.title = element_text(size = 10, face = "bold"),
            legend.position = "right",          # Position legends on the right
            legend.box = "vertical",             # Align legends vertically
            legend.spacing.y = unit(0.5, "cm"),  # Space between legend items vertically
            legend.margin = margin(t = 0, b = 5, unit = "pt"),  # Adjust margins
            legend.text = element_text(size = 8),  # Decrease font size for legend text
            legend.title = element_text(size = 9)  # Decrease font size for legend title
        ) +
        geom_point(
            aes(shape = platemap_dfs[[plate]]$dose)  # Keep only the dose shape
        ) +
        scale_shape_discrete(name = "Dose") +
        scale_fill_discrete(name = "Treatment") +  # Manual color scale for treatment
        guides(
            shape = guide_legend(order = 2, nrow = 1, override.aes = list(size = 3)),  # Horizontal dose legend
            fill = guide_legend(order = 1, ncol = 2, override.aes = list(size = 3))   # Treatment legend with 2 columns
        )

    # Save the plot with adjusted dimensions
    ggsave(
        output_file,
        platemap,
        device = 'png',
        dpi = 500,
        height = 4,  # Adjusted height
        width = 8   # Adjusted width
    )
}
