# StatusReport.md — Interim Status Report (Milestone 3)

> Project: **Food Access vs. County Health**  
> Research goal: Test whether poorer food access is associated with higher adult obesity/diabetes at the **county** level in the U.S. We follow the IS477 lifecycle: *collection → storage/organization → integration → data quality → cleaning → automation/provenance → reproducibility*.  
> Milestone scope: work completed through **end of Week 11**.


## 1) Task updates

### A. Data collection 
For this milestone the data collection step is scripted with and basic Python utilities to keep it reproducible. We treat both inputs as acquired secondary data from public agencies: the USDA Food Access Research Atlas (tract-level food access and demographics) and the CDC PLACES “Better Health” county dataset (county-level health outcomes and risk factors). The notebook loads the two local raw files— and —into DataFrames ( and ) using , with file locations handled via so the workflow can be re-run on different machines.pandasFood Access Research Atlas.csvPLACES_Better_Health_County_Data.csvdf_FAdf_Placeread_csvpathlib.Path

To capture provenance and fixity, a helper function gathers basic file metadata (name, absolute path, size, last-modified time) and computes a SHA-256 checksum using . These records are stored in , which acts as a simple collection register and lets us detect if a raw file changes in the future. As a final sanity check, the script prints dataset shapes and shows the first few rows of each table so we can verify that encodings, delimiters, and key variables look correct before moving on to storage and organization.describe_file()hashlibmetadata/data_collection_log.csv

### B. Storage & organization 
The storage layer starts from the imported df_FA and df_Place DataFrames and turns them into a small, well-structured schema for later integration and analysis. Using pandas, we select a focused set of variables from each source (geographic identifiers, population denominators, food-access indicators, and the health outcomes for obesity and diabetes) and standardize column names to a consistent, snake-case convention. Because the two sources use different geographic keys, we normalize all identifiers to string-typed FIPS codes: in FARA we derive a tract-level geoid and a 5-digit county_fips field from CensusTract, and in PLACES we coerce the county FIPS column to the same zero-padded string format. Numeric variables are cast to floats, and flag variables are stored as categorical fields to avoid accidental type mixing.

To separate raw data from derived tables, the script never overwrites the original CSV files. Instead, it writes cleaned, analysis-ready copies to a data/interim/ directory as column-pruned Parquet files (e.g., fara_tract.parquet, places_county.parquet). We also mirror these tables into a DuckDB database file (data/interim/pipeline.duckdb) so later stages can use SQL for joins and aggregation without repeatedly re-parsing CSV. The remaining work in this stage is mostly documentation and small refinements (finalizing primary-key definitions and adding comments in the DuckDB schema), so the core storage and organization tasks are effectively complete.

### C. Integration
Because FARA is tract-level, we first aggregate it to the county level using a consistent 5-digit county_fips key. Population totals and low-income/low-access indicators are summed, and population-normalized rates are derived when possible. PLACES is then reshaped from long format to wide format so that each county has a single row with separate columns for key health measures (e.g., OBESITY and DIABETES). Before merging, the workflow performs basic schema checks—verifying that county_fips exists in both sources, inspecting column types, and ensuring that the PLACES vintage (year) is explicit. After these checks, we run a guarded inner join on the standardized county_fips key to produce one integrated county-level table combining food-access characteristics and health outcomes. This follows the course module on managing heterogeneity by reconciling structure (columns and shapes), semantics (FIPS definitions), and timeliness (explicit year selection) before attempting integration.

### D. Data quality assessment
After integration, we profile the county-level analysis table built from FARA and PLACES rather than cleaning it. Using describe() and data-type listings, we confirm the basic structure (one row per county FIPS, with population counts, food-access indicators, and OBESITY/DIABETES prevalence). We then compute per-column missingness and sort by percent missing to assess completeness, paying particular attention to the LAPOP1_10 and LALOWI1_10 variables and the two health outcomes. For accuracy / plausibility, the workflow applies range checks: OBESITY and DIABETES must lie between 0 and 100 percent, and the tract-level counts aggregated to the county (Pop2010, LAPOP1_10, LALOWI1_10) are required to be non-negative. Any violations are flagged and displayed but not modified. To check consistency, we verify that county_fips is unique in the integrated table and that the ratios we derive—LAPOP1_10_rate and LALOWI1_10_rate—fall mostly in the expected 0–1 interval. Timeliness is handled by explicitly restricting PLACES to the latest available year and recording that vintage in the notebook.

As part of this assessment, we also look at whether the data can speak to our research question at all. By constructing simple quartiles of LAPOP1_10_rate and comparing average OBESITY and DIABETES across those bins, as well as computing basic correlations and urban/rural summaries, we see a preliminary pattern in which counties with higher low-access shares tend to report higher obesity and diabetes. These results are treated as diagnostic signal that motivates more careful modeling after the subsequent data-cleaning step.

### E. Data cleaning (~50%)
Guided by course practice, we first fix surface-level problems (trim whitespace, harmonize NA codes, ensure FIPS is 5 characters). Then we apply semantic assertions: FIPS must be valid, county population must be non-negative, and indicators must lie in reasonable ranges. The workflow uses a “document before repair” approach—flag everything, then apply minimal, scripted fixes only when required, and annotate every decision in the output notes.

### F. Preliminary analysis/visualization. 
To bridge plan and implementation, the workflow generates a single pilot graphic—food‑access indicator vs. adult obesity for a handful of counties—and a compact table of descriptives. This makes joins and unit assumptions visible and lets us spot obvious inconsistencies early.

### G. Automation & reproducibility
Within the same file, we fix random seeds where sampling occurs, emit a lightweight run log, and write a provenance line (source URL, access date, release label, SHA‑256) for each acquisition step. The top of the file includes two example commands so a grader can execute the pilot end‑to‑end in one shot. Outputs are deterministic for the same inputs, and all decisions (e.g., vintage notes, imputation choices) are copied into short text notes alongside the results. This sets up Weeks 12–13, when we will parameterize states/vintages and promote the same steps into a tiny pipeline without changing semantics.


## 2) Updated timeline (with status at end of Week 11)

- **Week 6** — finalize extraction/enrichment; lifecycle mapping; ethics/licensing ✅ *Completed.*  
- **Week 7** — begin integration; aggregate FARA; align FIPS; document storage choices ✅ *Completed (pilot scale).*  
- **Week 8** — complete integration; sanity checks; coverage by state; stabilize folders ✅ *Completed (pilot); national pending cleaning rule freeze.*  
- **Week 9** — data quality assessment; profiles; summarize issues ✅ *First pass complete; living document continues in W12.*  
- **Week 10** — data cleaning; scripted fixes; rerun diagnostics ✅ *Syntactic pass done; semantic checks ~50%.*  
- **Week 11** — automate end-to-end; parameterized Run-All/Snakemake; deterministic outputs and logs ✅ *Initial pipeline in place; logs & parameters to be extended in W12–13.*  
- **Week 12** — **provenance**: URLs, access dates, releases, SHA-256; transformation lineage; regenerability  *Planned.*  
- **Week 13** — **reproducibility & transparency**: environment & run docs; expected outputs; assumptions/limitations  *Planned.*  
- **Week 14** — **fresh-clone rehearsal**; fix paths/deps/order; one-command rebuild  *Planned.*  
- **Week 15** — finalize metadata & documentation; data dictionary/codebook; citations & licenses  *Planned.*  
- **Week 16** — polish & release; freeze outputs; regenerate figures; tag final release; submit URL & commit hash  *Planned.*


## 3) Changes to the project plan (and rationale)

1) **Dataset sample (tiny, representative subset).**  
We now enforce a pilot sequence (IL + 2 contrast states) before nationwide execution. This stabilizes cleaning/integration rules, exposes rural coverage edge cases early, and controls runtime.

2) **Data-access script (minimal, reproducible).**  
Offer a lightweight script that retrieves one example file per source, records basic provenance (source, access date, release), and demonstrates the intended acquisition flow end-to-end.

3) **Quick visualization (pilot check).”**  
Produce a single, simple graphic—e.g., food-access indicator vs. adult obesity for a handful of counties—to verify joins and reveal obvious inconsistencies, creating a visible bridge from plan to analysis.



## 4) Team member contribution summaries (this milestone)

**Jianye Ren — Engineering and Workflow**  
I focused on engineering and workflow from Week 6 through Week 11. In Week 6 I set up small data access runs and recorded source and release information while choosing FIPS as the primary key with clear type handling. In Week 7 I finalized extraction details and storage conventions and aligned the workflow with the data lifecycle. In Week 8 I aggregated FARA to the county level using population weights and aligned the result with PLACES using county FIPS. In Week 9 I produced light profiles and checks and summarized findings across accuracy completeness consistency and timeliness. In Week 10 I completed syntactic cleaning including NA normalization type unification and zero padded FIPS and drafted the initial semantic checks. In Week 11 I consolidated all steps into a single executable workflow fixed random seeds and wrote short run notes to prepare for parameterization and provenance.

**Zeyi Hua — Analysis & Documentation**  
I led analysis and documentation across Week 6 to Week 11. In Week 6 I completed dataset descriptions and linked them to the data lifecycle with citation and licensing notes. In Week 7 I documented storage layout and variable naming and confirmed the handling of FIPS and units. In Week 8 I reviewed the aggregated and joined fields for coherence and wrote the first rule for year and vintage alignment. In Week 9 I authored the data quality summary and highlighted rural missingness and potential vintage drift. In Week 10 I proposed minimal fixes recorded a document before repair guideline and checked how cleaning choices affect analysis. In Week 11 I wrote the task updates narrative prepared pilot descriptives and produced a simple visualization to show progress from plan to implementation.
