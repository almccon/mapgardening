#!/usr/bin/env Rscript

library(ggplot2)

places = c(
  "bayarea",
  "manchester",
  "seattle",
  "vancouver",
  "haiti",
  "london",
  "amsterdam",
  "cairo",
  "tirana"
)

scales = c(
  "250m",
  "500m",
  "1000m"
)

# Loop over each possible tsv filename exported from Python script:

for (place in places) {
  for (scale in scales) {

    inputfile = paste0('/Users/alan/github/mapgardening/output_totals_', place, '_raster_', scale, '.tsv')

    # If filename doesn't exist, skip it
    if (!file.exists(inputfile)) {
      cat("skipping", inputfile, "\n")
      next
    }

    classes <- c("Date","numeric","numeric","numeric")

    frame2 <- read.table(inputfile, header=TRUE, colClasses=classes)

    names(frame2) = c("date","edits","v1edits","blankedits")

    attach(frame2)

    outputfile = paste0('/Users/alan/github/mapgardening/output_history_', place, '_', scale, '.png')
    png(outputfile, 600, 600)

    a <- ggplot(data = frame2, aes(x = date, y = cumsum(blankedits))) +
      geom_line() +
      scale_x_date("Date") + scale_y_continuous("Cumulative blankspot edits") +
      ggtitle(paste0(place, '_', scale))
    print(a)
    dev.off()


    detach(frame2)
  }
}
