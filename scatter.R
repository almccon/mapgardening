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
  "tirana",
  "cairo"
)

scales = c(
  "250m",
  "500m",
  "1000m"
)

# Loop over each possible tsv filename exported from Python script:

for (place in places) {
  for (scale in scales) {
    inputfile = paste0('/Users/alan/github/mapgardening/outputv3_', place, '_', scale, '.tsv')

    # If filename doesn't exist, skip it
    if (!file.exists(inputfile)) {
      cat("skipping", inputfile, "\n")
      next
    }

    cat("reading", place, "from file", inputfile, "\n")

    frame <- read.table(inputfile, sep="\t", quote="", comment.char="", header=TRUE) # avoid catching "#" or "'"
    
    names(frame) = c("uid", "username", "edits", "blankedits", "v1edits", "firstedit", "firsteditv1", "firsteditblank", "days_active")
  
    attach(frame)
  
    #outputfile = paste0('/Users/alan/github/mapgardening/outscattersingle3_', place, '_', scale, '.pdf')
    outputfile = paste0('/Users/alan/github/mapgardening/outscattersingle3_', place, '_', scale, '.png')
  
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
    detach(frame)
  }
}
