# Food Access and County Health – IS477 Final Project

## Title

Food Access and County Health: A Small Reproducible Workflow

## Contributors

- **Jianye Ren** – data engineering, programming, documentation  
- **Zeyi Hua** – analysis design, interpretation, writing  

---

## Summary

This project examines how food access and chronic disease outcomes line up across U.S. counties. The basic idea is that counties where more people live far from supermarkets might also be places with higher adult obesity and diabetes. The project is not only about that question, but also about walking through the full IS477 data lifecycle with a single, reproducible workflow.

Our **primary research question** is:

> Do U.S. counties with more limited access to healthy food retailers show higher adult obesity and diagnosed diabetes prevalence?

We also track two **secondary questions**:

> (a) Does the association differ for mostly urban versus mostly rural counties?  
> (b) Which food-access indicators (for example low-access and low-income/low-access counts) seem most informative for explaining differences between counties?

To study this, we combine two public data sources:

1. **USDA Food Access Research Atlas (FARA)** – tract-level measures of supermarket access and basic demographics.  
2. **CDC PLACES “Local Data for Better Health” – County Data** – county-level estimates of health outcomes, including adult obesity and diagnosed diabetes.

Both datasets are treated as **acquired secondary data**. We do not scrape any websites or collect any human-subjects data. We download the official CSV files once and keep them under `data/raw/`.

All code lives in a single notebook called **`Workprocess.ipynb`**. The notebook is organized by lifecycle stage:

1. Data collection  
2. Storage and organization  
3. Integration  
4. Data quality assessment  
5. Data cleaning  
6. Analysis and visualization  

Each section builds on the previous one. The same notebook can be re-run from top to bottom to regenerate all outputs.

For **data collection**, we use `pandas` plus small pieces of Python from class. The notebook reads the two raw CSV files (`Food Access Research Atlas.csv` and `PLACES_Better_Health_County_Data.csv`), checks that they exist, and prints shapes and `head()` so we can see a small “pilot slice.” We also compute SHA-256 checksums with `hashlib` and write a collection log to `metadata/data_collection_log.csv`. This log records file paths, sizes, last modified times, and checksums. If someone accidentally changes a raw file later, the hash will no longer match.

In **storage and organization**, we separate raw and derived data into folders: `data/raw/`, `data/interim/`, `data/processed/`, and `metadata/`. From FARA we keep the columns we actually need: `CensusTract`, `Urban`, `Pop2010`, `LAPOP1_10`, `LALOWI1_10`, plus a few others. We create tract GEOIDs and then derive a 5-digit `county_fips` by taking the first five digits. From PLACES we keep the basic identifiers (`LocationID`, `StateAbbr`, `StateDesc`, `LocationName`), `MeasureId`, `Data_Value`, and `Year`. We standardize `LocationID` to a 5-digit `county_fips` so the two sources can talk to each other.

**Integration** happens in the same notebook. FARA is tract-level, so we aggregate it to the county level by summing up `Pop2010`, `LAPOP1_10`, and `LALOWI1_10` within each `county_fips`. We then compute simple rates:

- `LAPOP1_10_rate = LAPOP1_10 / Pop2010` – share of people living in low-access tracts  
- `LALOWI1_10_rate = LALOWI1_10 / Pop2010` – share of people who are both low income and low access  

On the PLACES side, we keep only the latest year of data and filter to `MeasureId` equal to `OBESITY` or `DIABETES`. We pivot to wide format so each county has one row with columns `OBESITY` and `DIABETES`. Finally, we join the county-level FARA and PLACES tables on `county_fips` using an inner join, with `validate="one_to_one"` so we catch any unexpected duplicates.

After integration, the notebook runs a **data quality assessment**. We look at dtypes, summary statistics, and missingness for each column. Range checks enforce the basic rules that population and count variables must be non-negative and that prevalence variables (obesity and diabetes) must fall between 0 and 100 percent. We also check that `county_fips` is unique, confirming that the table really is at “one row per county.” Any values that violate the simple rules are printed out for inspection.

In the **cleaning** section, we apply a small set of scripted fixes. We drop territories so we focus on the 50 states plus DC. Negative counts and out-of-range prevalence values are turned into missing values rather than silently truncated. Rate variables are recomputed more carefully, with population clipped at a minimum of 1 and the resulting rates clipped to the [0, 1] interval. Rows missing any of the key analysis variables (`Pop2010`, `LAPOP1_10_rate`, `OBESITY`, `DIABETES`) are dropped to form a clean analytic sample. We also standardize `county_fips` to a zero-padded string and keep only the columns relevant for the research questions. The cleaned table is written to `data/processed/county_food_access_health_clean.csv` (and also as a Parquet file for convenience).

The final part of the notebook does **analysis and visualization**. We divide counties into quartiles based on `LAPOP1_10_rate` to compare obesity and diabetes across “better access” versus “worse access” counties. We compute simple correlations between access measures and outcomes and draw scatterplots. We also construct an “urban share” for each county using the FARA `Urban` field and examine how the relationships differ for mostly rural, mixed, and mostly urban counties.

Overall, the project gives us a small but complete workflow: from downloaded CSVs to a cleaned county-level dataset and some first answers to the research questions, all backed by code that can be re-run by someone else.

---

## Data profile

### USDA Food Access Research Atlas (FARA)

The Food Access Research Atlas is published by USDA’s Economic Research Service. It describes how far people live from supermarkets and large grocery stores, and whether they are low income. The unit of analysis is the **census tract**. Each row has a FIPS code, basic population counts, and several indicators at different distance thresholds.

For this project we use only a subset of columns:

- `CensusTract` – numeric FIPS code for the tract, which we convert to an 11-digit GEOID.  
- `Urban` – 1 for urban tracts, 0 for rural tracts.  
- `Pop2010` – total population in 2010.  
- `LAPOP1_10` – number of people in low-access tracts using the 1 mile / 10 miles rule.  
- `LALOWI1_10` – number of people who are both low income and low access under the same rule.

All of these are aggregated counts, so there is no individual-level information. The Atlas is released as open data intended for research and policy analysis. We still treat it cautiously: the raw CSV is kept under `data/raw/` and we do not try to link it to any microdata. In the notebook we compute `county_fips` by taking the first five digits of the tract GEOID so that we can match to county-level outcomes later.

From a data-profile point of view, FARA is the main source for our **explanatory variables**. It gives us a way to talk about “food deserts” or low-access areas in a simple quantitative way. It also gives us a clean `Urban` flag that we later use to classify counties as mostly rural or mostly urban.

### CDC PLACES – County Data

PLACES is a CDC project that provides model-based small-area estimates for health measures such such as obesity, diabetes, smoking, and more. We work with the **county-level CSV** that has one row per measure per county and year.

The key columns we rely on are:

- `LocationID` – county FIPS code, later turned into `county_fips`.  
- `StateAbbr` and `StateDesc` – state abbreviation and full state name.  
- `LocationName` – county name.  
- `MeasureId` – short code for the measure (we use `OBESITY` and `DIABETES`).  
- `Measure` – plain-language label.  
- `Data_Value` – prevalence estimate (percentage).  
- `Year` – reference year.

PLACES is also aggregated and does not contain individual-level records. It is built from BRFSS and other inputs using small-area modeling, so the values should be read as estimates, not exact measurements. Licensing allows research and public use.

In our project we filter the PLACES data down to a single year (the most recent year present in the file) and keep only the rows where `MeasureId` is `OBESITY` or `DIABETES`. We then pivot so that each county has one row and two outcome columns (`OBESITY`, `DIABETES`). This curated table feeds into the integration step.

### Integrated county-level dataset

After aggregation and joining, we end up with a county-level table that combines FARA access indicators and PLACES outcomes. The cleaned version keeps:

- `county_fips` – 5-digit county code.  
- `state_abbr`, `state_name`, `county_name` – context.  
- `Pop2010` – county population in 2010 (sum of tract populations).  
- `LAPOP1_10` and `LALOWI1_10` – sums of tract-level counts.  
- `LAPOP1_10_rate` and `LALOWI1_10_rate` – the same counts divided by population.  
- `OBESITY` and `DIABETES` – adult prevalence estimates in percent.

Privacy risk here is low because everything is aggregated to county level and comes from official public releases. The more important issues are interpretive: understanding that “low access” is defined in a particular technical way, and that health measures are model-based estimates subject to sampling and modeling error.

---

## Data quality

We follow the four main quality dimensions from class: **accuracy**, **completeness**, **consistency**, and **timeliness**. All checks are scripted inside `Workprocess.ipynb`, and the notebook keeps the raw diagnostics (tables and plots) alongside the code.

### Accuracy and plausibility

For accuracy, we mainly focus on obvious numeric problems. The notebook prints `describe()` summaries for all numeric columns and then performs value-range checks:

- Count variables (`Pop2010`, `LAPOP1_10`, `LALOWI1_10`) must be greater than or equal to zero.  
- Prevalence variables (`OBESITY`, `DIABETES`) must lie between 0 and 100 percent.

If any value violates these constraints, it is reported. In practice we did not see extreme or impossible values from the official releases, but the checks are important as guardrails, especially if the pipeline is reused with different versions of the data.

When computing rates such as `LAPOP1_10_rate`, we also watch for divide-by-zero issues. To avoid infinite or undefined values, we clip `Pop2010` at a minimum of 1 before dividing. The resulting rates are then clipped to the \[0, 1] range. Histograms of the rates show reasonable distributions: most counties have fairly low low-access shares, but there is a tail of counties where a large fraction of residents live far from supermarkets.

### Completeness

Completeness is assessed by computing percent missing for each column. The core columns that define the analysis (`county_fips`, `Pop2010`, `LAPOP1_10`, `LALOWI1_10`, `OBESITY`, `DIABETES`) show very low missingness. A small number of counties have missing access counts, which likely comes from issues at the tract level. Instead of trying to impute these values, we simply exclude those rows from the main analysis once we reach the cleaning stage.

For derived variables like `urban_share`, missingness can appear if a county’s tracts do not have valid `Urban` flags. These cases are rare, and we exclude them only from the urban/rural comparison while keeping them in the primary dataset.

### Consistency

Consistency is about making sure the dataset obeys its own rules. The main rule here is the grain: **one row per county**. After we aggregate FARA to `county_fips` and pivot PLACES to wide format, we use `validate="one_to_one"` in the merge to guarantee that there is at most one row per county on each side. The notebook also explicitly checks that `county_fips` is unique in the integrated table. If duplicates ever show up, the merge fails and forces us to debug rather than silently producing a messy result.

We also clean up column names and types for consistency. For instance, we rename `StateAbbr` to `state_abbr` and ensure that all FIPS fields are stored as 5-character strings with leading zeros. Rates are stored as floats. These small steps keep the table easier to work with and reduce subtle bugs from type mismatches.

### Timeliness

Timeliness in this project has two levels. First, within PLACES we make sure we use a single, clearly identified year. The notebook picks the maximum `Year` present in the file and filters to that year before pivoting. This avoids mixing different PLACES vintages in one table.

Second, the FARA indicators are tied to 2010, while the PLACES data are more recent. This means that we are relating past access conditions to more recent health outcomes. For this course project we accept that limitation and document it. In future work, a better solution would be to either obtain food access measures for multiple years or restrict PLACES to a year closer to 2010. The key point is that the notebook makes the vintages explicit so that anyone reusing the data understands the timing.

### Summary of quality findings

Putting it together, the data are in good enough shape for a cross-sectional, county-level analysis. Counts and prevalence values are within reasonable ranges, missingness on key variables is low, and the grain is consistent. The main caveats are the temporal mismatch between FARA and PLACES and the fact that PLACES outcomes are model-based. We handle these by being cautious in how we interpret correlations and by clearly stating the limitations in the findings and future-work sections.

---

## Findings

### Overview

All findings are based on the cleaned county-level dataset (`county_food_access_health_clean`) produced in the workflow.  
After removing counties with missing key variables, the primary analytic sample contains **3,074 counties**.

---

### Primary Research Question  
**Do counties with worse food access show higher obesity and diabetes?**

The main exposure is `LAPOP1_10_rate`, the share of residents living in low-food-access census tracts.  
Counties are split into quartiles of this rate:

| access_quartile   | LAPOP1_10_rate | OBESITY (%) | DIABETES (%) |
|-------------------|---------------:|------------:|-------------:|
| Q1_best_access    | 0.0589         | 37.60       | 12.04        |
| Q2                | 0.1673         | 37.32       | 11.61        |
| Q3                | 0.2652         | 37.28       | 11.53        |
| Q4_worst_access   | 0.4808         | 37.13       | 11.66        |

Key points:

- Mean obesity and diabetes are **very similar across quartiles**.  
  The obesity mean changes by less than one percentage point from Q1 to Q4; diabetes varies by about half a point.
- Pearson correlations are:

  - `corr(LAPOP1_10_rate, OBESITY) ≈ -0.036`
  - `corr(LAPOP1_10_rate, DIABETES) ≈ -0.040`
  - `corr(OBESITY, DIABETES) ≈ 0.699`

- Scatterplots of `LAPOP1_10_rate` against both outcomes show dense clouds with **no strong upward trend**.

**Conclusion:** at the county level, a higher share of residents in low-access tracts is **not strongly associated** with higher obesity or diabetes; the simple low-access rate is almost uncorrelated with these outcomes.

---

### Secondary Research Question (a)  
**Does the association differ for urban vs rural counties?**

An `urban_share` is computed from tract-level FARA data, and counties are grouped as:

- **mostly_rural** – `urban_share < 0.25` (1,416 counties)  
- **mixed** – `0.25 ≤ urban_share ≤ 0.75` (1,244 counties)  
- **mostly_urban** – `urban_share > 0.75` (414 counties)

Mean values by urban category:

| urban_category | LAPOP1_10_rate | OBESITY (%) | DIABETES (%) |
|----------------|---------------:|------------:|-------------:|
| mostly_rural   | 0.2233         | 38.06       | 12.21        |
| mixed          | 0.2560         | 37.57       | 11.49        |
| mostly_urban   | 0.2721         | 34.15       | 10.67        |

Findings:

- **Rural counties have clearly worse outcomes**: higher obesity and diabetes than mixed and urban counties.
- At the same time, their average `LAPOP1_10_rate` is only slightly lower than urban counties.
- Scatterplots of `LAPOP1_10_rate` vs obesity drawn separately for each group show:
  - Similar “cloud” shape everywhere.
  - A **vertical shift**: the rural cloud sits higher on the y-axis, the mixed cloud is in the middle, and the urban cloud is lowest.

**Conclusion:** urban–rural context itself is strongly related to obesity and diabetes levels. Within each context, the low-access rate remains a weak predictor, but rural counties tend to have higher chronic disease burden overall.

---

### Secondary Research Question (b)  
**Which food-access indicators best explain differences between counties?**

Interpretation:

- `LALOWI1_10_rate` shows **small but clearly positive** correlations with both obesity and diabetes.
- `LAPOP1_10_rate` alone has correlations close to zero and slightly negative.
- This suggests that **combining low income and low access** captures vulnerability better than distance-based access alone.

**Overall conclusion:**  
The county-level data do not support a strong direct link between simple low-access rates and obesity/diabetes, but they do show that:
1. Counties with more rural character have substantially higher obesity and diabetes levels, and  
2. Access indicators that focus on **low-income, low-access** populations are more informative about health differences than access measures by themselves.

---

## Future work

There are several natural extensions, both on the analysis side and on the workflow side.

### Analysis

1. **Control for confounders.** A logical next step is to add covariates such as median income, educational attainment, age structure, and racial composition, and fit multivariable models. Many of these variables are available from the American Community Survey and could be merged in using FIPS codes. This would help separate the effect of food access from other structural disadvantages.

2. **Look at more outcomes.** PLACES includes many other measures (physical inactivity, hypertension, preventive screenings, etc.). Extending the analysis to those outcomes would give a broader view of how food environments relate to health.

3. **Move beyond simple correlations.** With enough covariates, we could fit regression models or use causal diagrams to reason more formally about pathways from access to health. That is outside the scope of this course project but would be a natural follow-up.

4. **Consider time and space.** If we had multiple years of food-access and health data, we could run panel analyses or look for spatial clusters of high-risk counties. Spatial autocorrelation tools (Moran’s I, local indicators) would be useful here.

### Workflow

1. **Stronger automation.** Right now, running “Run All” in `Workprocess.ipynb` is enough to regenerate the results, but we could further wrap the notebook in a small command-line script or use a workflow tool to create an explicit dependency graph. That would help if we add more inputs or analysis steps.

2. **Better environment capture.** Adding a `requirements.txt` or `environment.yml` file would fix the exact versions of `pandas`, `matplotlib`, and other libraries. For a fully portable setup, we could add a Dockerfile so the whole environment can be rebuilt easily.

3. **Richer metadata.** Beyond the current collection log, a small YAML or JSON file listing each dataset, where it came from, and which notebook sections produced each derived table would push the project closer to FAIR principles.

4. **Formal data dictionary.** Creating a separate markdown or CSV file with variable names, types, units, and descriptions for the cleaned dataset would make reuse easier for outside users (and for us in the future).

These changes would not fundamentally alter the main findings, but they would make the project more robust, reusable, and aligned with open-science practices.

---
## Reproducing: 

This project is packaged so that the full workflow—from acquisition of the public datasets to the final analysis and visualizations—can be reproduced and inspected.

All code for the workflow is contained in a single notebook, **`Workprocess.ipynb`**. The notebook is organized by lifecycle stage (data collection, storage and organization, integration, quality assessment, cleaning, analysis/visualization), and each stage is fully scripted. Running the notebook from top to bottom regenerates every intermediate table, quality diagnostic, and final plot. The README and “Reproducing” section describe the expected directory layout and the exact file names and locations for the raw USDA FARA and CDC PLACES CSV files.

To make the data component reproducible, the project includes both documentation and concrete artifacts. The "county_food_access_health_clean.csv" file records, for each input file, the source name, local path, file size, last-modified time, and SHA-256 checksum, so that the exact release used can be verified. The final integrated and cleaned county-level datasets (`data/processed/county_food_access_health.parquet` and `data/processed/county_food_access_health_clean.csv/.parquet`) are kept under version control and mirrored in a shared **Box folder**
Box Folder Link: https://uofi.box.com/s/l40t6irnoxjfnpojitgx1xmtb5eouvcz



## References

U.S. Department of Agriculture, Economic Research Service. (2025). *Food Access Research Atlas* [data set]. Washington, DC. Retrieved from https://catalog.data.gov/dataset/food-access-research-atlas   

Centers for Disease Control and Prevention. (2023). *PLACES: Local Data for Better Health, County Data, 2023 release* [data set]. Division of Population Health, Epidemiology and Surveillance Branch. Retrieved from https://catalog.data.gov/dataset/places-local-data-for-better-health-county-data-2023-release   

Greenlund, K. J., Lu, H., Counts, N. Z., et al. (2022). PLACES: Local data for better health. *Preventing Chronic Disease, 19*, E46. https://doi.org/10.5888/pcd19.210315   

pandas Development Team. (2025). *pandas: Python data analysis library* (Version 2.x) [Computer software]. Retrieved from https://pandas.pydata.org   

DuckDB Development Team. (2025). *DuckDB* (Version 1.x) [Computer software]. DuckDB Project. Retrieved from https://duckdb.org   

Hunter, J. D., Droettboom, M., Caswell, T. A., et al. (2025). *Matplotlib: Visualization with Python* (Version 3.x) [Computer software]. Matplotlib Development Team. Retrieved from https://matplotlib.org   

Python Software Foundation. (2025). *Python 3 Standard Library Documentation* [Computer software documentation]. Retrieved from https://docs.python.org/3/library/   
