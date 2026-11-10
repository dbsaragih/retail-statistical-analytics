# install_packages.R
# R packages used by the retail-statistical-analytics notebooks.
# Run once:  Rscript r/install_packages.R

pkgs <- c(
  # data and plotting
  "arrow", "dplyr", "tidyr", "ggplot2", "lubridate", "scales", "broom",
  # regression inference (HAC / Newey-West)
  "sandwich", "lmtest",
  # time series and forecasting (BQ2, BQ6)
  "tsibble", "feasts", "fable", "fabletools",
  # clustering (BQ4)
  "cluster", "factoextra",
  # association rules (BQ5)
  "arules", "arulesViz",
  # classification (BQ3, BQ6)
  "rpart", "rpart.plot", "ranger", "pROC",
  # anomaly detection (BQ7)
  "isotree", "qcc"
)

# Use the repository set in .Rprofile if there is one (e.g. pre-built Linux packages);
# otherwise fall back to the main CRAN server
repos <- getOption("repos")
if (is.null(repos) || repos[["CRAN"]] %in% c("@CRAN@", "")) repos <- "https://cloud.r-project.org"

missing <- setdiff(pkgs, rownames(installed.packages()))
if (length(missing) > 0) {
  install.packages(missing, repos = repos)
}
cat("Installed:", length(pkgs) - length(setdiff(pkgs, rownames(installed.packages()))),
    "of", length(pkgs), "packages\n")