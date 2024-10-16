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

# Color-blind friendly and most distinct color palette
okabe_ito <- c(
    "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#8DA0CB", 
    "#D55E00", "#CC79A7", "#999999", "#A6CEE3", "#1F78B4", 
    "#B2DF8A", "#33A02C", "#FB9A99", "#E31A1C", "#FDBF6F", 
    "#FF7F00", "#CAB2D6"
)

for (plate in names(platemap_dfs)) {
    output_file <- output_platemap_files[[plate]]
    platemap <- platetools::raw_map(
        data = platemap_dfs[[plate]]$treatment,
        well = platemap_dfs[[plate]]$well_position,
        plate = 96,
        size = 10
    ) +
        ggtitle(paste("Platemap layout for plate", plate)) +
        theme(
            plot.title = element_text(size = 10, face = "bold"),
            legend.position = "right",
            legend.box = "vertical",
            legend.spacing.y = unit(0.5, "cm"),
            legend.margin = margin(t = 0, b = 5, unit = "pt"),
            legend.text = element_text(size = 8),
            legend.title = element_text(size = 9)
        ) +
        geom_point(aes(shape = platemap_dfs[[plate]]$dose)) +
        scale_shape_discrete(name = "Dose") +
        scale_fill_manual(values = okabe_ito, name = "Treatment") +  # Use Okabe-Ito palette
        guides(
            shape = guide_legend(order = 2, nrow = 1, override.aes = list(size = 3)),
            fill = guide_legend(order = 1, ncol = 2, override.aes = list(size = 3))
        )

    ggsave(output_file, platemap, device = 'png', dpi = 500, height = 4, width = 8)
}



