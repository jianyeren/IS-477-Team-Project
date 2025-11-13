# StatusReport.md — Interim Status Report (Milestone 3)

> Project: **Food Access vs. County Health**  
> Research goal: Test whether poorer food access is associated with higher adult obesity/diabetes at the **county** level in the U.S. We follow the IS477 lifecycle: *collection → storage/organization → integration → data quality → cleaning → automation/provenance → reproducibility*.  
> Milestone scope: work completed through **end of Week 11**.


## 1) Task updates (with repository artifacts)

### A. Data collection (✅ done)
The workflow begins by fetching a tiny, representative slice from each public source: FARA (tract-level food access indicators) and PLACES (county-level obesity and diabetes). We show how the data are programmatically retrieved, record essential provenance (catalog URL, access date, and release label), and compute a simple checksum to illustrate fixity. This mirrors the course emphasis on automating acquisition and capturing enough context to make the data re-obtainable later.

### B. Storage & organization (90%)
Right after download, the workflow standardizes basic types (strings for FIPS, numeric for percentages) and writes a small, tidy table for each dataset. Instead of spreading files across many directories, we keep outputs from this milestone embedded in the workflow’s state and export only the final pilot tables for inspection. The narrative explains our naming, the choice to keep FIPS as a zero-padded string, and how these decisions support downstream joins—directly reflecting the “good-enough practices” we discussed in class.

### C. Integration (~75%)
FARA is tract-level, so we aggregate to county using population-weighted logic inside the same file. We then align with PLACES by 5-digit county FIPS and run simple schema/type checks before joining. The workflow shows the conceptual model (county as the grain; FIPS as the key; years/vintages made explicit) and performs a guarded join that halts if keys or types drift. This follows the module on heterogeneity: handle structure (columns, types), semantics (FIPS definitions), and timeliness (vintage notes) before merging.

### D. Data quality assessment (~65%)
After integration, we compute quick profiles that are light enough for the pilot: row counts by state, missingness rates for key fields, and simple range sanity checks. We summarize the four quality dimensions from class—Accuracy, Completeness, Consistency, Timeliness—and log issues we observed (e.g., rural counties more likely to have missing values; potential year misalignment). These diagnostics are written as small text summaries produced by the workflow so they travel with the analysis.

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
