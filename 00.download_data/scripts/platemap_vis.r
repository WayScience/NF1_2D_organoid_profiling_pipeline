suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(platetools))
suppressPackageStartupMessages(library(RColorBrewer))


patients <- read.csv(file.path("../../data/patient_IDs.txt"), header = FALSE, col.names = "PatientID")
list_of_platemaps <- c()
for (i in 1:nrow(patients)) {
  patient_id <- patients$PatientID[i]
  platemap_file <- file.path(paste0("../../data/",patient_id),"platemap","platemap.csv")
  if (file.exists(platemap_file)) {
    platemap <- read.csv(platemap_file)
    platemap <- platemap %>%
      mutate(PatientID = patient_id)
    list_of_platemaps[[i]] <- platemap
  } else {
    warning(paste("Platemap file for patient", patient_id, "not found. Skipping."))
  }
}

output_fig_dir <- file.path("platemap_figures")
if (!dir.exists(output_fig_dir)) {
    dir.create(output_fig_dir, recursive = TRUE)
}
platemap_suffix <- "_platemap_figure.png"

# Define output figure paths
output_platemap_files <- list()
for (df in list_of_platemaps) {
    patient_id <- df$PatientID[1]

    output_platemap_files[[patient_id]] <- file.path(output_fig_dir, paste0(patient_id, platemap_suffix))
}

# Load in all platemap CSV files
platemap_dfs <- list()
for (plate in list_of_platemaps) {
    # Update 'Dose' column
    plate <- plate %>%
        mutate(
            dose = case_when(
                treatment == "DMSO" ~ paste0(dose, "%"),
                TRUE ~ paste0(dose, " uM")
            )
        )

    # Store the updated data frame directly (not as a list)
    platemap_dfs[[plate$PatientID[1]]] <- plate  # Remove the list() wrapper
}

for (plate in names(platemap_dfs)) {
    output_file <- output_platemap_files[[plate]]

    # Access the dataframe directly
    current_platemap <- platemap_dfs[[plate]]

    platemap <- platetools::raw_map(
        data = current_platemap$treatment,
        well = current_platemap$well_position,
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
        geom_point(aes(shape = current_platemap$dose)) +
        scale_shape_discrete(name = "Dose") +
        # scale_fill_manual(values = okabe_ito, name = "Treatment") +
        guides(
            shape = guide_legend(order = 2, nrow = 1, override.aes = list(size = 3)),
            fill = guide_legend(order = 1, ncol = 2, override.aes = list(size = 3))
        )

    ggsave(output_file, platemap, device = 'png', dpi = 600, height = 4, width = 8)
}
