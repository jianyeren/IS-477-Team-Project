# Project Plan

## Overview
We will build an end‑to‑end, reproducible data workflow using two real datasets from Data.gov to examine whether limited access to healthy food retailers is associated with worse community health outcomes at the county level. The project demonstrates the IS477 lifecycle: discovery, acquisition, storage and organization, integration, quality and cleaning, documentation, and reproducibility, while following federal open‑data licensing.

The overall objective is to turn trusted public data into an analysis‑ready product that can be recomputed on demand. Our repository will contain clearly separated stages for raw, clean, and derived data, scripted transformations, and automation to run the pipeline from start to finish. By focusing on a single, policy‑relevant question and a small number of well‑documented indicators, we keep the scope realistic while still demonstrating the core skills required in this course. We will prioritize clarity and traceability over complex modeling so that another student, TA, or policymaker can inspect each step, understand our choices, and reproduce our results using their own machine.

The study is also designed to highlight responsible and ethical handling of public data. Both sources are federal open data, but we will still record citation requirements, access dates, dataset versions, and fixity information. Any limitations in geographic coverage, uncertainty in model‑based estimates, or assumptions introduced during aggregation will be written down in plain language. In short, the deliverable is not just an answer to a research question but a transparent, reusable workflow that can be adapted to other states, years, or related health outcomes.

## Research Questions
Primary: Do U.S. counties with more limited access to healthy food retailers show higher adult obesity and diagnosed diabetes prevalence?

Secondary: a) Does the association differ for urban versus rural counties? b) Which food‑access indicators (for example low‑income and low‑access flags, distance thresholds) best explain differences between counties?

The primary question is intentionally simple and measurable with the chosen data sources. We will operationalize food access using indicators from the Food Access Research Atlas aggregated to county, then compare those indicators to the CDC PLACES county outcomes. Because both datasets provide stable geographic identifiers, we can align records reliably with minimal preprocessing. The analysis will begin with descriptive comparisons, followed by correlation estimates and a small set of linear models designed to summarize association strength rather than imply causality. We will report effect sizes and uncertainty where appropriate, and we will verify that findings are not driven by a single extreme county or by an arbitrary data‑processing choice.

The secondary questions offer structure for sensitivity and subgroup analyses. Urban and rural counties can differ profoundly in retail patterns, transportation, and health services availability, all of which influence both food access and health outcomes. If possible within scope, we will attach an urbanicity classification to each county and compute stratified summaries so that results are not averaged in ways that obscure meaningful differences. To understand which specific food access signals carry the most information, we will compare distance‑based measures with composite low‑income and low‑access flags. This comparison can help a practitioner choose concise metrics for county‑level monitoring or for communicating risks to nontechnical audiences.

## Team
Jianye Ren – Data Engineering and Automation: programmatic acquisition; database and schema setup in DuckDB; workflow automation with a Run‑All script or Snakemake; GitHub repository structure, tags, and releases.

Zeyi Hua – Analysis and Documentation: data profiling and cleaning; county‑level aggregation and joins; exploratory analysis and figures; Markdown documentation for ProjectPlan, StatusReport, and README.

## Datasets (from Data.gov)
USDA Economic Research Service, Food Access Research Atlas (FARA). Catalog: https://catalog.data.gov/dataset/food-access-research-atlas. We will use tract‑level food‑access indicators (for example low‑income and low‑access flags, distance to supermarkets) and aggregate them to county FIPS to align with outcomes. Open federal data with citation to USDA ERS.

CDC PLACES, Local Data for Better Health — County Data (latest release). Catalog example 2023: https://catalog.data.gov/dataset/places-local-data-for-better-health-county-data-2023-release. We will use county‑level estimates for adult obesity and diagnosed diabetes with county FIPS identifiers. Open federal data with citation to CDC.

## Timeline
Week 6: finalize extraction and enrichment; map our workflow to the data lifecycle; confirm ethical, legal, and licensing notes; verify acquisition sources and access methods; decide storage layout and naming.

Week 7: begin integration; aggregate FARA to county, align with PLACES by FIPS; validate schemas and types; document storage and organization choices; record any format or API quirks discovered.

Week 8: complete integration; run sanity checks, coverage by state, quick descriptives; stabilize folder conventions; ensure lifecycle checkpoints are tracked; re-confirm licensing, attribution, and any redistribution limitations.

Week 9: conduct data quality assessment; profile completeness, ranges, and outliers; summarize issues by variable and geography; identify fields needing recode or imputation; note potential biases and risks.

Week 10: perform data cleaning; implement scripted fixes for types, units, syntactic and semantic issues; handle missing values and duplicates; rerun quality diagnostics; document decisions and impacts succinctly.

Week 11: automate the workflow end-to-end; create a parameterized Run-All or Snakemake pipeline covering download, checksums, load, transform, integrate, and figures; ensure deterministic outputs and logs.

Week 12: capture provenance; log source URLs, access dates, release identifiers, and SHA-256 checksums; record transformation lineage; verify intermediate artifacts are regenerable from raw inputs.

Week 13: strengthen reproducibility and transparency; draft clear environment setup and run instructions; provide command examples and expected outputs; state assumptions, limitations, and responsible-use guidance.

Week 14: rehearsal on a fresh clone; execute the pipeline on a clean machine or container; fix path, dependency, and ordering issues; tighten instructions; confirm one-command rebuild works.

Week 15: finalize metadata and documentation; complete data dictionary and codebook; add citations and license notices; supply concise descriptive metadata supporting discovery, understanding, and reuse.

Week 16: polish and release; freeze outputs, regenerate figures, and refine prose; summarize lifecycle alignment and ethics compliance; tag the final release; submit the release URL and commit hash.

## Constraints
Scale alignment because FARA is tract‑level and must be aggregated to counties; the choice of weights and thresholds affects indicators. Model‑based outcomes in PLACES require careful interpretation. Coverage and missingness may be an issue in rural areas. Nationwide aggregation can be large, so we will prototype on one state first.

There are also practical constraints related to computation and time. Although DuckDB is fast and works well on tabular data, tract‑to‑county aggregation across the entire country still involves millions of records. To keep runtimes acceptable on student hardware, we will stream reads where possible, prune columns early, and cache intermediate results. A small set of configuration variables will control geographic scope and year selection so that we can iterate quickly during development and expand to larger runs only when the pipeline is stable. Finally, because both datasets are periodically updated, we will record access dates and the exact release identifiers so that results remain comparable across runs.

## Gaps
Choose the pilot state, for example Illinois or California, to balance representativeness and runtime. Confirm year alignment across releases and run a short sensitivity check if years differ. If we stratify by urbanicity, select a coding source such as RUCA or Census urban classification.

Additional open questions include decisions about visualization standards and minimal modeling. For maps, we will select a consistent projection and a restrained color palette that preserves accessibility for readers with color‑vision deficiencies. For scatter or hexbin plots, we will annotate the number of counties and include simple reference lines to aid interpretation. With respect to modeling, the plan is to prefer summary statistics and transparent linear models over complex techniques. If time allows, we may add a small robustness check that includes a second health indicator or an alternative food access threshold to confirm that conclusions hold under modest variation.