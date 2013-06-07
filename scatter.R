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
    inputfile = paste0('/Users/alan/github/mapgardening/outputv4_', place, '_raster_', scale, '.tsv')

    # If filename doesn't exist, skip it
    if (!file.exists(inputfile)) {
      cat("skipping", inputfile, "\n")
      next
    }

    cat("reading", place, "from file", inputfile, "\n")

    classes <- c("numeric", "character", "numeric", "numeric", "numeric", "Date", "Date", "Date", "numeric", "Date", "Date")

    # specify quote and comment.char to avoid catching "#" or "'"
    frame <- read.table(inputfile, sep="\t", quote="", comment.char="", header=TRUE, na.strings = "NULL", colClasses=classes) 
    
    names(frame) = c("uid", "username", "edits", "blankedits", "v1edits", "firstedit", "firsteditv1", "firsteditblank", "days_active", "mean_date", "mean_date_weighted")
  
    attach(frame)
  
    outputfile = paste0('/Users/alan/github/mapgardening/outscattersingle4_total-v-blank_', place, '_', scale, '.png')
  
    #pdf(outputfile, 7, 7) # Create a PDF of 7 by 7 inches
    png(outputfile, 600, 600)
  
    # Add 0.1 to x and y to avoid problems with the log scale
    a <- ggplot(data = frame, aes(x = jitter(edits+0.1, 0.01), y = jitter(blankedits+0.1, 0.01), col=days_active)) +
      #stat_smooth(formula="y ~ x", na.rm=TRUE, method="lm") +
      #stat_smooth(formula="y ~ poly(x,2)", na.rm=TRUE, method="lm") +
      #stat_smooth(formula="y ~ a * log(x+0.1) + b", na.rm=TRUE, method="lm") +
      #stat_smooth(formula="y ~ a * exp(b *x)", na.rm=TRUE, method="lm") +
      geom_point(aes(size = days_active)) +
      scale_x_log10("Log total edits") + scale_y_log10("Log blankspot edits") +
      ggtitle(paste0(place, '_', scale)) + scale_color_continuous(name = "days active")
    print(a)
    dev.off()

    outputfile = paste0('/Users/alan/github/mapgardening/output_meaneditdate_', place, '_', scale, '.png')
    png(outputfile, 600, 600)

    # Add 0.1 to x and y to avoid problems with the log scale
    a <- ggplot(data = frame, aes(x = mean_date_weighted, y = jitter(blankedits+0.1, 0.01), col=days_active)) +
      geom_point(aes(size = days_active)) +
      scale_x_date("Mean edit date weighted") + scale_y_log10("Log blankspot edits") +
      ggtitle(paste0(place, '_', scale)) + scale_color_continuous(name = "days active")
    print(a)
    dev.off()

    detach(frame)

}
