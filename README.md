<a href="https://paul-lai.vercel.app"><img src="assets/plant.svg" width="100%" alt="Paul Lai, M.S. Data Science at UC San Diego. An animated data factory: fab sensor, hydrophone, Statcast and pottery data ride conveyor belts into one machine and come out validated."></a>

<p align="center">
  <a href="https://paul-lai.vercel.app/assets/Paul_Lai_Resume.pdf"><img src="assets/buttons/resume.svg" height="40" alt="Resume (PDF)"></a>&nbsp;
  <a href="https://paul-lai.vercel.app"><img src="assets/buttons/portfolio.svg" height="40" alt="Portfolio"></a>&nbsp;
  <a href="https://www.linkedin.com/in/paullai0111/"><img src="assets/buttons/linkedin.svg" height="40" alt="LinkedIn"></a>&nbsp;
  <a href="mailto:holai@ucsd.edu"><img src="assets/buttons/email.svg" height="40" alt="holai@ucsd.edu"></a>
</p>

I'm Paul, an M.S. Data Science student at UC San Diego. I like data that arrives large and messy, from sensors, archives and streams, and results that still hold when checked against the world outside the model. That points me toward **AI data solutions, smart manufacturing and big data processing**. Below are the lines I've built so far; open any of them for screenshots and details. My work history lives on my [portfolio](https://paul-lai.vercel.app) and [resume](https://paul-lai.vercel.app/assets/Paul_Lai_Resume.pdf).

<img src="assets/panel.svg" width="100%" alt="Instrument panel: 590 sensors per run, 4 GB of audio per day, 2.14 million pitches processed, clustering silhouette 0.64.">

## Production lines

<a href="https://github.com/Paul-Lai0111/semiconductor-yield-anomaly-detection"><img src="assets/monitors/yield.svg" width="100%" alt="Semiconductor Yield: which wafer runs to inspect first when only 20% can be reviewed; 5 of 17 later failures caught with 62 reviews."></a>

<details>
<summary><b>Open the line:</b> Semiconductor Yield · results, method, repo</summary>
<br>

<img src="https://raw.githubusercontent.com/Paul-Lai0111/semiconductor-yield-anomaly-detection/main/manufacturing_results/figures/outcome_summary.png" width="100%" alt="Same-budget outcomes for the selected method, previous recipe and random review">

- **Data:** UCI SECOM, 1,567 production runs × 590 anonymized sensors, 104 failures (6.6%). Predicting "pass" everywhere scores 93% accuracy and catches nothing, so every method is judged by failures caught per review.
- **Search:** 50 fixed configurations (forests, boosting, SVMs, linear, nearest neighbors, novelty detectors) over three expanding forward blocks, 150 fits, plus one predeclared rank blend.
- **Discipline:** the protocol and source hashes were saved before the search, and the recipe was frozen before the latest 20% of runs were scored.
- **Result:** 5 of 17 later failures with 62 reviews, the same as the previous recipe. Reported as it came out, not as the best of many tries.

[Repository](https://github.com/Paul-Lai0111/semiconductor-yield-anomaly-detection) · [Executed notebook](https://github.com/Paul-Lai0111/semiconductor-yield-anomaly-detection/blob/main/manufacturing_notebook.ipynb) · [Full results](https://github.com/Paul-Lai0111/semiconductor-yield-anomaly-detection/blob/main/manufacturing_results/RESULTS.md)
</details>

<a href="https://github.com/Paul-Lai0111/ocean-soundscape-ml"><img src="assets/monitors/ocean.svg" width="100%" alt="Ocean Soundscape: a year of deep-ocean audio sorted without labels; monthly agreement r = 0.99 with MBARI's fin whale index."></a>

<details>
<summary><b>Open the line:</b> Ocean Soundscape · findings, live dashboard, repo</summary>
<br>

<img src="https://raw.githubusercontent.com/Paul-Lai0111/ocean-soundscape-ml/main/docs/img/year_ltsa.png" width="100%" alt="One year of the deep-ocean soundscape: fin whale chorus at 20 Hz from September to January">

- **Pipeline:** 8 commands stream minutes from MBARI's 4 GB-per-day public archive, extract 16 calibrated acoustic features and cluster them.
- **Weather first:** 1–8 kHz noise tracks NOAA buoy wind (r = 0.86 for the year); relative features cut the clusters' wind dependence from η² 0.49 to 0.020 and lift silhouette from 0.27 to 0.51.
- **Outside check:** agrees with MBARI's published call indices month by month (r = 0.99 fin, 0.91 blue); the comparison exposed a flaw whose fix raised per-minute agreement from 0.81 to 0.93.
- **Surprise:** the loudest minute of the first week is an M3.3 earthquake 78 km away, found as an outlier.

[Live dashboard](https://ocean-soundscape-ml-paullai.streamlit.app) · [Repository](https://github.com/Paul-Lai0111/ocean-soundscape-ml) · [Full report](https://github.com/Paul-Lai0111/ocean-soundscape-ml/blob/main/docs/analysis.md)
</details>

<a href="https://github.com/Paul-Lai0111/MLB_DeepPitch_Dashboard"><img src="assets/monitors/deeppitch.svg" width="100%" alt="DeepPitch: 2.14 million MLB pitches rebuilt as physics with an out-of-sample Stuff+ model."></a>

<details>
<summary><b>Open the line:</b> DeepPitch · screenshots, findings, live app</summary>
<br>

<img src="https://raw.githubusercontent.com/Paul-Lai0111/MLB_DeepPitch_Dashboard/main/docs/img/home.png" width="49%" alt="DeepPitch home: animated flight canvas"> <img src="https://raw.githubusercontent.com/Paul-Lai0111/MLB_DeepPitch_Dashboard/main/docs/img/pitcher.png" width="49%" alt="Pitcher scorecard with percentile diamonds">

- **Pipeline:** 2.14M Statcast pitches (2024–26) fetched in 6-day chunks, rebuilt by a unit-tested physics engine and served from about 17 MB of Parquet.
- **Model:** LightGBM Stuff+ scored leave-one-season-out, so every grade is out-of-sample; it correlates 0.45 with next season's run value, against 0.19 for this season's results.
- **Finding:** across 1,082 pitcher-season four-seamers, vertical approach angle relates to whiffs (r = +0.47) while "rise" barely does (r = −0.02).
- **App:** eight pages in English and Traditional Chinese, from flight replay to a physics lab.

[Live app](https://paul-2024mlb-deeppitch-analytics.streamlit.app/) · [Repository](https://github.com/Paul-Lai0111/MLB_DeepPitch_Dashboard)
</details>

<a href="https://github.com/Paul-Lai0111/sinica-ceramic-clustering"><img src="assets/monitors/ceramics.svg" width="100%" alt="Archaeological Ceramics: 257 pottery sherds grouped by mineral composition; silhouette rose from 0.50 to 0.64."></a>

<details>
<summary><b>Open the line:</b> Archaeological Ceramics · method, figures, repo</summary>
<br>

<img src="https://raw.githubusercontent.com/Paul-Lai0111/sinica-ceramic-clustering/main/results/figures/pca_pruning_nanke.png" width="100%" alt="Nanke sherds in PCA space, before and after feature pruning">

- **Data:** 257 sherds from 28 excavation sites in Penghu and Nanke, 11 compositional variables (the data belongs to the institutes and stays private).
- **Leak-proofing:** the site code handed the model the answer, so it was removed along with a texture-only field, 13 → 11 variables.
- **Result:** K-Means beat DBSCAN on every dataset; silhouette rose from 0.50 to 0.64 on Nanke, while DBSCAN flagged isolated sherds for re-examination.

[Repository](https://github.com/Paul-Lai0111/sinica-ceramic-clustering) · [Case study](https://paul-lai.vercel.app/projects/ceramic-clustering/)
</details>

<a href="https://github.com/Paul-Lai0111/streamlit-wake"><img src="assets/monitors/wake.svg" width="100%" alt="streamlit-wake: a GitHub Action that presses the Streamlit wake button every 6 hours."></a>

<details>
<summary><b>Open the line:</b> streamlit-wake · how it works</summary>
<br>

- A plain ping can't wake a sleeping Streamlit app, because the sleep page loads fine; only pressing the button in a browser does.
- So a scheduled workflow opens each app in headless Chromium with Playwright, presses the button if it's there and waits for the app to render. If an app doesn't come back within 4 minutes, the run fails and GitHub emails you.
- Use it as a template repository or as a one-step composite action. MIT licensed. It keeps the two live demos above awake.

[Repository](https://github.com/Paul-Lai0111/streamlit-wake)
</details>

## Telemetry

<img src="assets/telemetry/languages.svg" width="49%" alt="Languages across public repositories"> <img src="assets/telemetry/hours.svg" width="49%" alt="Commit clock in Pacific time">

<sub>Redrawn every day by a GitHub Action from the public GitHub API ([build_stats.py](scripts/build_stats.py)).</sub>

## Toolbox

| Equipment | What it does on these lines | Lines |
|---|---|---|
| Python, pandas, NumPy | ingest, cleaning, time ordering, feature tables | all |
| scikit-learn | preprocessing, PCA, clustering, model search, validation | Yield · Ocean · Ceramics |
| XGBoost, LightGBM | gradient boosting for failure ranking and Stuff+ | Yield · DeepPitch |
| SciPy, soundfile | calibrated spectra and acoustic features from raw audio | Ocean |
| Parquet (pyarrow), AWS S3 | columnar storage, streaming from public archives | DeepPitch · Ocean |
| Streamlit, Plotly, matplotlib | live dashboards and figures | Ocean · DeepPitch · Ceramics |
| pytest, GitHub Actions, Playwright | tests, CI, scheduled browser automation | Yield · DeepPitch · Wake |

<p align="center"><sub>All artwork is drawn in code (<a href="scripts">scripts/</a>), lettered in Barlow under the SIL Open Font License.</sub></p>
