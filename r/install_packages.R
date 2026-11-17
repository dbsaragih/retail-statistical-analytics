# install_packages.R
# R packages used by the retail-statistical-analytics R notebooks (R 4.6).
# Run once:  Rscript r/install_packages.R
# Then register the Jupyter kernel:  Rscript -e 'IRkernel::installspec(name = "ir", displayname = "R (WSL)")'

pkgs <- c(
  # data and plotting (all notebooks)
  "arrow", "dplyr", "tidyr", "ggplot2", "lubridate", "scales",
  # regression inference: robust and HAC standard errors (BQ1, BQ3)
  "sandwich", "lmtest",
  # classification and ROC (BQ3, BQ6)
  "rpart", "rpart.plot", "pROC",
  # clustering (BQ4)
  "cluster",
  # association rules (BQ5)
  "arules",
  # forecasting and gradient boosting (BQ6)
  "prophet", "xgboost",
  # anomaly detection (BQ7)
  "isotree",
  # Jupyter kernel
  "IRkernel"
)

# Use the repository set in .Rprofile if there is one (e.g. pre-built Linux binaries from Posit Package Manager);
# otherwise fall back to the main CRAN server
repos <- getOption("repos")
if (is.null(repos) || repos[["CRAN"]] %in% c("@CRAN@", "")) repos <- "https://cloud.r-project.org"
options(timeout = max(900, getOption("timeout")))   # prophet and xgboost are large downloads

missing <- setdiff(pkgs, rownames(installed.packages()))
if (length(missing) > 0) {
  install.packages(missing, repos = repos)
}
ok <- vapply(pkgs, function(p) suppressWarnings(requireNamespace(p, quietly = TRUE)), logical(1))
cat("Installed:", sum(ok), "of", length(pkgs), "packages\n")
if (any(!ok)) cat("Missing:", names(ok)[!ok], "\n")
