# AstroAgent Skills Repository

Custom Hermes Agent skills developed by the AIP team for astronomy, data science, reproducible workflows, AI/ML, devops, and productivity.

Total: **118** custom skills across **17** categories.

## Repository layout

| Directory | Description | Skills |
|---|---|---|
| `agents/` | Agent concepts and configuration | 1 |
| `astronomy/` | Survey archives, ADQL/TAP queries, stellar catalogs, and astronomy-specific plots/animations | 21 |
| `creative/` | description: Creative content generation — ASCII art, hand-drawn style diagrams, and visual design tools. | 14 |
| `data-science/` | description: Skills for data science workflows — interactive exploration, Jupyter notebooks, data analysis, and visualization. | 1 |
| `devops/` | Operations, containers, deployment, service exposure, and runtime troubleshooting | 9 |
| `infrastructure/` | Hermes/OpenWebUI/API-server/MCP infrastructure and integration workflows | 7 |
| `leisure/` | Nearby places and leisure search workflows | 1 |
| `mcp/` | description: Skills for working with MCP (Model Context Protocol) servers, tools, and integrations. Includes the built-in native MCP client (configure servers in config.yaml for automatic tool discovery) and the mcporter CLI bridge for ad-hoc server interaction. | 1 |
| `media/` | description: Skills for working with media content — YouTube transcripts, GIF search, music generation, and audio visualization. | 2 |
| `mlops/` | description: Knowledge and Tools for Machine Learning Operations - tools and frameworks for training, fine-tuning, deploying, and optimizing ML/AI models | 9 |
| `productivity/` | Calendars, contacts, documents, OCR, PDFs, and image-description workflows | 4 |
| `python/` | Python data engineering, caching, plotting, and reusable scientific-programming workflows | 6 |
| `reana-workflows/` | REANA client configuration, templates, execution recipes, and workflow best practices | 17 |
| `research/` | Academic research, literature, LaTeX manuscripts, DRP, and paper improvement workflows | 13 |
| `science/` | dt4acc digital twin, accelerator-science runbooks, EPICS/Tango, and host smoke tests | 6 |
| `social-media/` | description: Skills for interacting with social platforms and social-media workflows — posting, reading, monitoring, and account operations. | 1 |
| `software-development/` | Coding workflows, docs-first development, and application-specific implementation guides | 5 |

## Categories overview

**Agents (1)** — Agent concepts and configuration

**Astronomy (21)** — Survey archives, ADQL/TAP queries, stellar catalogs, and astronomy-specific plots/animations

**Creative (14)** — description: Creative content generation — ASCII art, hand-drawn style diagrams, and visual design tools.

**Data Science (1)** — description: Skills for data science workflows — interactive exploration, Jupyter notebooks, data analysis, and visualization.

**Devops (9)** — Operations, containers, deployment, service exposure, and runtime troubleshooting

**Infrastructure (7)** — Hermes/OpenWebUI/API-server/MCP infrastructure and integration workflows

**Leisure (1)** — Nearby places and leisure search workflows

**Mcp (1)** — description: Skills for working with MCP (Model Context Protocol) servers, tools, and integrations. Includes the built-in native MCP client (configure servers in config.yaml for automatic tool discovery) and the mcporter CLI bridge for ad-hoc server interaction.

**Media (2)** — description: Skills for working with media content — YouTube transcripts, GIF search, music generation, and audio visualization.

**Mlops (9)** — description: Knowledge and Tools for Machine Learning Operations - tools and frameworks for training, fine-tuning, deploying, and optimizing ML/AI models

**Productivity (4)** — Calendars, contacts, documents, OCR, PDFs, and image-description workflows

**Python (6)** — Python data engineering, caching, plotting, and reusable scientific-programming workflows

**Reana Workflows (17)** — REANA client configuration, templates, execution recipes, and workflow best practices

**Research (13)** — Academic research, literature, LaTeX manuscripts, DRP, and paper improvement workflows

**Science (6)** — dt4acc digital twin, accelerator-science runbooks, EPICS/Tango, and host smoke tests

**Social Media (1)** — description: Skills for interacting with social platforms and social-media workflows — posting, reading, monitoring, and account operations.

**Software Development (5)** — Coding workflows, docs-first development, and application-specific implementation guides

## Skills inventory

| Skill | Description |
|---|---|
| `agents/astroagent-concept/` | Use the AstroAgent concept framing for architecture, positioning, and design discussions. |
| `astronomy/data-aip-de-s3/` | Work with data.aip.de and S3-backed datasets using reproducible local caching, Dask-first reads for huge data, and plotting workflows that scale to large astronomy catalogs. |
| `astronomy/gaia-aip-de-adql/` | Query gaia.aip.de using ADQL/TAP with reproducible query capture and astronomy-aware caveats. |
| `astronomy/gaia-dr3-plot-with-dust/` | Retrieve the 100 nearest Gaia DR3 stars (by parallax) and produce a two‑panel research‑paper‑style figure. The left panel shows RA vs Dec, the right panel shows a Galactic XY projection overlaid with an all‑sky dust‑e... |
| `astronomy/gaia-dr3-tap-query/` | Retrieve the nearest 100 stars from Gaia DR3 using the TAP service hosted at AIP (https://gaia.aip.de/tap/). Includes Parquet storage, preview CSV, and RA/Dec & Galactic XY plots. |
| `astronomy/gaiadr3-aip-de-adql/` | Query the Gaia DR3 PostgreSQL database at gaia.aip.de via its Daiquiri REST API. Includes CSRF handling, async job submission, queue names, and result fetching. Access 1.8 billion sources with ~153 columns. |
| `astronomy/gaiadr3-aip-query-api/` | Query the Gaia DR3 PostgreSQL database at gaia.aip.de via its Daiquiri REST API. Includes CSRF handling, queue names, and result fetching. |
| `astronomy/rave-dr6/` | Query the RAVE DR6 catalog at https://www.rave-survey.org/tap/ using pyvo (TAPService.run_sync). Access stellar parameters, Gaia cross-matches, distances, and Galactic coordinates (l, b). Includes galactic and equirec... |
| `astronomy/rave-dr6-3d-animation/` | Step‑by‑step workflow to query the RAVE DR6 catalog for the 100 nearest stars (by parallax), process the data, generate 2‑D visualisations and a public‑talk‑ready 3‑D rotating animation using Matplotlib. |
| `astronomy/rave-dr6-3d-public-animation/` | Generate a public‑talk‑ready 3‑D animation of the 100 nearest RAVE DR6 stars using matplotlib. |
| `astronomy/rave-dr6-nearest-100-plot/` | Query the 100 nearest RAVE DR6 stars and generate two clear PNG plots: Galactic projection and RA/Dec scatter, with reproducible local parquet output. |
| `astronomy/rave-dr6-public-talk-visualizations/` | Turn a nearest-100 RAVE DR6 query into dark-theme, public-talk-ready PNG visualizations with clear titles, readable scaling, and presentation-friendly styling. |
| `astronomy/rave-dr6-recent-observations-plot/` | Retrieve the most recent 100 entries from the RAVE DR6 `dr6_obsdata` table and generate a simple RA‑Dec scatter plot. Handles missing Python dependencies, installs them if necessary, and falls back to astropy for gala... |
| `astronomy/rave-dr6-tap-query/` | Query the RAVE DR6 catalog hosted at https://www.rave-survey.org/tap/ using pyvo (TAPService.run_sync). Useful for accessing stellar parameters, Gaia cross-matches, distances, and Galactic coordinates (l, b). Includes... |
| `astronomy/shboost-cmd-plot/` | Generates a colour‑magnitude diagram (CMD) for ~100 k stars from the public shboost2024 S3 bucket. The script caches the sampled data locally as a Parquet file for fast repeat runs and outputs a high‑resolution PNG (3... |
| `astronomy/shboost-cmd-visualization/` | Generate a high‑resolution density CMD (hexbin) from the ShBoost star dataset, cache locally as Parquet, add colour‑matched population annotations, a detailed legend, log‑scaled colour bar, and create a GIF animation... |
| `astronomy/shboost-plot-s3/` | Plot a sampled subset of the ShBoost 2024 star dataset stored on a public S3 bucket. |
| `astronomy/shboost-public-s3-cmd-plot/` | Plot a colour-magnitude diagram from the public SHBoost 2024 S3 parquet dataset using the notebook-backed access pattern and a REANA-friendly serial workflow. |
| `astronomy/shboost24-cmd/` | Generate colour-magnitude diagrams from SHboost24 data using local Parquet caching and agreed plotting conventions. |
| `astronomy/shboost_cmd_plot_and_animation/` | Cache selected columns from the ShBoost 2024 S3 dataset, create a hexbin CMD with log-scaled density, add optimized non‑overlapping stellar‑population annotations, and generate both a high‑resolution PNG and an MP4 an... |
| `astronomy/shboost_full_cmd_datashader/` | Generate a full‑dataset colour‑magnitude diagram (CMD) for the ShBoost 2024 star catalog using Dask and Datashader, optimized for minimal memory usage. |
| `astronomy/starhorse-access/` | Access and document StarHorse-related local datasets and usage conventions. |
| `creative/4most-spectrograph-animation/` | Manim CE animation explaining the 4MOST spectrograph for 11th-grade physics class. Full optical path from starlight through telescope, collimator, slit, dispersion element, fibre positioner, spectrographs, to CCD dete... |
| `creative/animate-sine-cosine-matplotlib/` | Generate an MP4 animation of sine (green) and cosine (red) curves using matplotlib for frame rendering and ffmpeg for encoding. The skill avoids privileged operations and destructive commands. |
| `creative/fourmost-educational-animation/` | Create a short Manim animation that explains the 4MOST spectrograph for 11th‑grade physics classes. Includes installation, script writing, rendering, common pitfalls, and fallback to external video. |
| `creative/fourmost-spectrograph-animation/` | Generates a 60-90s educational animation of the 4MOST spectrograph on the VISTA 4-m telescope using Manim Community Edition. Follows a schematic-first workflow: static matplotlib plot for review, then Manim animation.... |
| `creative/fourmost-spectrograph-schematic/` | Generate a static schematic illustration of the 4MOST spectrograph system as a precursor to a full Manim animation. |
| `creative/fractal-edm-showcase/` | Automated workflow to generate a short fractal showcase video with a synthetic fast‑paced EDM soundtrack, including Seahorse and Elephant valley visual elements. |
| `creative/fractal-showcase-animation/` | Generate a short Manim video showcasing famous fractals (Mandelbrot set, Sierpinski triangle, Barnsley fern, Barnsley elephant) and add a simple background music track. The process includes on‑the‑fly generation of fr... |
| `creative/fractals-edm-showcase/` | Create a high‑energy fractal showcase video with a synthetic EDM soundtrack, including custom Seahorse and Elephant‑jet visuals, a slow zoom, and final audio‑video merge. |
| `creative/galaxy-formation-animation/` | Create a concise Manim animation explaining galaxy formation for 11th‑grade students. Includes best‑practice steps, common pitfalls, and reusable code snippets. |
| `creative/manim-020-gotchas/` | Gotchas and API changes specific to Manim Community Edition 0.20.1. Includes ImageMobject, animation names, and font handling. |
| `creative/manim-educational-animation/` | Creating clean, non-overlapping Manim animations for educational explainers (Gymnasium/school level). Avoids text overlap bugs, guides pacing, and structures single-scene vs multi-scene approaches. |
| `creative/manim-tts-narration/` | Add German TTS narration to Manim educational videos using espeak-ng. Handles scene-by-scene audio generation, duration management, and merging with video. |
| `creative/plot-sine-cosine-matplotlib/` | Generate a PNG plot of sin(x) in red and cos(x) in green using matplotlib, handling missing dependencies in a managed Python environment. |
| `creative/sin-unit-circle-animation/` | Create animations showing the Unit Circle → Sine Wave connection. Uses ValueTracker + always_redraw for smooth rotating point that traces out the sine wave. Perfect for educational content (11th grade math, trigonomet... |
| `data-science/datashader-019-pipeline/` | Generate density plots (CMD, hexbin, 2D histograms) using datashader 0.19.0 with Dask for lazy data loading and matplotlib for final rendering. Handles the 0.19.0 API: no Canvas.hexbin(), no tf.to_rgba(), tf.shade() r... |
| `devops/api-server-local-image-support/` | Fix Open WebUI image display by extending api_server.py to convert standard markdown ![alt](/local/path) images into HTTP URLs via /media/<path> route. Handles the gap between agent-generated image paths and the API s... |
| `devops/docker-access/` | Verify Docker availability and run containers on this host. |
| `devops/docker-access-group-reload/` | Resolve Docker permission errors by ensuring the user is in the docker group and reloading group membership. |
| `devops/manim-headless-rendering/` | Guidelines for rendering Manim animations in a headless Linux environment (no GUI). Includes troubleshooting common errors, choosing correct renderer, managing long renders, and concatenating partial video files produ... |
| `devops/manim-telegram-animation/` | Guide to creating concise educational animations with Manim, handling common errors, rendering in low‑resolution, and delivering the final MP4 via Telegram (including ffmpeg concat handling). |
| `devops/manim-telegram-delivery/` | Generate a Manim animation, extract a short preview, concatenate full‑resolution fragments, and deliver the MP4 directly via Telegram. Handles common rendering pitfalls (partial movie files, missing renderer options)... |
| `devops/manim-video-audio/` | Add audio to Manim-rendered videos — background music, TTS narration, or SRT subtitles. Handles common pitfalls with MP3 decoding, volume mixing, and timing. |
| `devops/paperclip-oss120b-external/` | Step‑by‑step guide for turning a fresh Paperclip installation into a publicly reachable service that forwards LLM calls to a custom OSS‑120B model served via an OpenAI‑compatible endpoint. Handles deployment mode, bin... |
| `devops/telegram-auth-troubleshooting/` | Diagnose and fix cases where the Hermes Telegram bot silently ignores messages from group members (auth allowlist issues). |
| `infrastructure/api-server-media-display/` | Diagnose and fix images not displaying in Open WebUI / API server frontends. |
| `infrastructure/docs-mcp-at-aip/` | Access the AIP documentation MCP server at https://docs-mcp-server.kube.aip.de. Search, scrape, and fetch documentation for 15+ indexed libraries including reana, pandas, snakemake, dask, unsloth, and more. HTTP POST... |
| `infrastructure/hermes-api-server/` | Enable and expose the Hermes OpenAI-compatible API server safely for frontends and integrations. |
| `infrastructure/hermes-native-mcp/` | Configure and use Hermes Agent's built-in MCP client for stdio and HTTP MCP servers, including testing, troubleshooting, and TLS trust fixes for internal HTTPS endpoints. |
| `infrastructure/mcporter-cli/` | Use the mcporter CLI for ad-hoc MCP server discovery, testing, schema inspection, and tool calls without changing Hermes configuration. |
| `infrastructure/openwebui-hermes/` | Connect Hermes Agent to Open WebUI using the OpenAI-compatible API server and document image/file-delivery caveats. |
| `infrastructure/openwebui-media-via-s3/` | Serve images, videos, and audio to Open WebUI by uploading media to the public S3 bucket (scr4agent), then embedding pure markdown URLs. |
| `leisure/find-nearby/` | Find nearby places (restaurants, cafes, bars, pharmacies, etc.) using OpenStreetMap. Works with coordinates, addresses, cities, zip codes, or Telegram location pins. No API keys needed. |
| `mcp/mcporter/` | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation. |
| `media/ffmpeg-ambient-audio/` | Create layered ambient pad music using FFmpeg's aevalsrc filter. Generates loopable 15-second clips with slow vibrato, shimmer, and exponential decay, then loops to target duration. Mixes into video at low volume for... |
| `media/fractal-preference-mandelbrot-elephant/` | When the user asks for a fractal showcase, they want a video that shows ONLY a Mandelbrot zoom transitioning to the Elephant's Valley image. The transition should use a very small scaling factor (~1e-7). No other frac... |
| `mlops/cloud/modal/` | Serverless GPU cloud platform for running ML workloads. Use when you need on-demand GPU access without infrastructure management, deploying ML models as APIs, or running batch jobs with automatic scaling. |
| `mlops/inference/gguf/` | GGUF format and llama.cpp quantization for efficient CPU/GPU inference. Use when deploying models on consumer hardware, Apple Silicon, or when needing flexible quantization from 2-8 bit without GPU requirements. |
| `mlops/inference/guidance/` | Control LLM output with regex and grammars, guarantee valid JSON/XML/code generation, enforce structured formats, and build multi-step workflows with Guidance - Microsoft Research's constrained generation framework |
| `mlops/models/clip/` | OpenAI's model connecting vision and language. Enables zero-shot image classification, image-text matching, and cross-modal retrieval. Trained on 400M image-text pairs. Use for image search, content moderation, or vis... |
| `mlops/models/stable-diffusion/` | State-of-the-art text-to-image generation with Stable Diffusion models via HuggingFace Diffusers. Use when generating images from text prompts, performing image-to-image translation, inpainting, or building custom dif... |
| `mlops/models/whisper/` | OpenAI's general-purpose speech recognition model. Supports 99 languages, transcription, translation to English, and language identification. Six model sizes from tiny (39M params) to large (1550M params). Use for spe... |
| `mlops/training/grpo-rl-training/` | Expert guidance for GRPO/RL fine-tuning with TRL for reasoning and task-specific model training |
| `mlops/training/peft/` | Parameter-efficient fine-tuning for LLMs using LoRA, QLoRA, and 25+ methods. Use when fine-tuning large models (7B-70B) with limited GPU memory, when you need to train <1% of parameters with minimal accuracy loss, or... |
| `mlops/training/pytorch-fsdp/` | Expert guidance for Fully Sharded Data Parallel training with PyTorch FSDP - parameter sharding, mixed precision, CPU offloading, FSDP2 |
| `productivity/aip-member-contact-retrieval/` | Retrieve phone number (and email) for a staff member of the Leibniz Institute for Astrophysics Potsdam (AIP) from the public website. |
| `productivity/image-description-workflow/` | Workflow for handling user‑submitted images, generating a description via vision_analyze, and responding. |
| `productivity/nextcloud-caldav/` | Access and manage calendars on cloud.aip.de Nextcloud via CalDAV. List, create, edit, and delete events in personal and shared calendars. Credentials are passed via environment variables — never hardcode them. |
| `productivity/nextcloud-caldav-calendar-management/` | Create, read, update, and delete calendar events via Nextcloud CalDAV API. Includes auth patterns, calendar paths, and quirks for Nextcloud v29+. |
| `python/cmd-plotting/` | Generate astronomy colour-magnitude diagrams in Python with reproducible plotting choices. |
| `python/dask-hvplot-datashader-scientific-plots/` | Build scalable scientific plots from large tabular datasets using Dask for processing, hvPlot for plotting, and Datashader for dense large-data rendering. |
| `python/hdf5-on-s3-cached/` | Access HDF5 files stored on S3 by creating a reliable local cache first, extracting reusable subsets, and converting repeated tabular work products to local Parquet. |
| `python/s3-parquet-sampling/` | Sample or reduce massive Parquet datasets on S3 using local Parquet caching, Dask-first processing for large inputs, and hvPlot/Datashader for scalable scientific visualization. |
| `python/s3-parquet-sampling-plot-cached/` | Efficiently sample a subset of a massive Parquet dataset stored on an S3‑compatible bucket, cache the sampled rows locally as a Parquet file for fast reuse, and produce high‑resolution PNG plots suitable for analysis... |
| `python/seaborn-paper-plots/` | Create clean seaborn/matplotlib plots suitable for papers, notes, and reproducible reports. |
| `reana-workflows/reana-aip/` | Create REANA workflows using AIP conventions, approved environments, and reproducible workflow structure. |
| `reana-workflows/reana-client-config/` | Configure REANA client authentication with multi-profile `.reana/config.yaml` or `~/.reana/config.yaml`, store tokens safely, and select dev/prod back-ends reproducibly. |
| `reana-workflows/reana-client-docker/` | Use the Dockerized REANA client to ping a REANA server, list workflows, and format output with jq. |
| `reana-workflows/reana-client-multi-backend/` | Reusable instructions to set up a .reana/config.yaml with dev and prod profiles and run reana‑client via Docker using REANA_PROFILE. |
| `reana-workflows/reana-cmd-plot-workflow/` | REANA workflow that caches a large S3 Parquet dataset and plots bprp0 vs mg0 as a hex‑bin PNG. |
| `reana-workflows/reana-cmd-plot-workflow-external-script/` | Create a REANA workflow that runs a large S3 Parquet data plot using an external Python script. The script is stored as a separate file and referenced in the workflow inputs. This avoids inline script blocks that caus... |
| `reana-workflows/reana-dev-workflow-setup/` | Set up a REANA development workflow in its own directory, place a minimal reana.yaml, and run it using the Dockerized REANA client. |
| `reana-workflows/reana-run-script-with-workspace/` | Run a Python (or other) script in a REANA workflow ensuring the script is found via $REANA_WORKSPACE. |
| `reana-workflows/reana-selflearn-workflows/` | Self‑learn REANA by listing finished workflows on the development backend, downloading their `reana.yaml` files, and providing guidelines for writing correct REANA workflows. |
| `reana-workflows/reana-serial-python/` | Reusable template for REANA serial workflows that run a Python analysis script on remote data, cache processed results locally as Parquet, and produce PNG outputs. Designed for SHBoost-like analyses where only the scr... |
| `reana-workflows/reana-serial-python-analysis-template/` | Reusable template for REANA serial workflows that run a Python analysis script on remote data, cache processed results locally as Parquet, and produce PNG outputs. Designed for SHBoost-like analyses where only the scr... |
| `reana-workflows/reana-shboost24/` | Run SHboost24 plotting and sampling workflows on REANA with cached parquet inputs and explicit script packaging. |
| `reana-workflows/reana-sin-plot-workflow/` | Minimal REANA workflow that plots a sine curve in green using pandas and matplotlib. Includes `reana.yaml`, `plot_sin.py` (and optional `requirements.txt`). |
| `reana-workflows/reana-version-info/` | Quick reference for REANA client and server versions for dev and production backends used by the user. |
| `reana-workflows/reana-workflow-best-practices/` | How to write a correct REANA workflow YAML that complies with the organization’s policies. |
| `reana-workflows/reana-workflow-sin-plot/` | Automates creation, submission, monitoring, and retrieval of a REANA workflow that plots a green sine curve using pandas and matplotlib. |
| `reana-workflows/reana-workflow-with-env/` | Create a REANA workflow respecting the organization’s environment repository and default memory limit. |
| `research/2026-agentic-astronomy-literature/` | Summarize and apply the key 2026 literature on agentic systems in astronomy and scientific analysis. |
| `research/arxiv/` | Search and retrieve academic papers from arXiv using the free REST API. Query by keyword, author, category, or paper ID. Fetch abstracts, full PDFs, generate BibTeX, and explore citations via Semantic Scholar. |
| `research/astroagent-github-skills-repo-bootstrap/` | Scaffold a shareable GitHub repository for Hermes skills focused on AstroAgent, astronomy workflows, REANA, Open WebUI integration, and local dataset operations. |
| `research/cold-streams-monitoring/` | Automated arXiv monitoring for cold gas filament accretion in galaxy formation. Discovers new papers on cold mode accretion, cold flows, cosmological filaments, and related topics. Runs as a scheduled cron job. |
| `research/drp-paper/` | Create and maintain the DRP white paper project with REANA integration |
| `research/iterative-paper-improvement/` | Structured multi-round improvement workflow for LaTeX academic papers — each round targets specific improvements (structure, prose, figures, compilation). Also covers merging multiple papers and multi-phase iterations... |
| `research/latex-journal-submission-package/` | Convert a working LaTeX manuscript into a journal-style submission package with separate BibTeX, build helper, manifest, and zip archive; useful when TeX is unavailable locally. |
| `research/latex-paper-iteration/` | Iteratively improve LaTeX research papers — structural fixes, prose polishing, figure integration, compilation cycles. Also covers merging multiple papers into a unified manuscript. |
| `research/latex-research-paper/` | Generate complete, compilable LaTeX research papers in formal academic style with full section structure, BibTeX references, and figure support. |
| `research/mnras-latex-compile-portability-fixes/` | Fix common MNRAS LaTeX portability issues on Ubuntu/Debian TeX Live installs, compile successfully, and package submission artifacts. |
| `research/mnras-latex-portable/` | Build and package an MNRAS LaTeX manuscript portably on Ubuntu, avoiding missing-font-package failures and fixing common two-column table issues. |
| `research/mnras-latex-portable-build-and-package/` | Build and package an MNRAS LaTeX manuscript portably on Ubuntu, avoiding missing-font-package failures and fixing common two-column table issues. |
| `research/multi-section-latex-whitepaper/` | Generate comprehensive LaTeX white papers from multiple sources — Markdown sections, existing papers, or user ideas. Converts and assembles into a single compiled PDF. |
| `science/dt4acc-container-troubleshooting/` | Debugging dt4acc digital twin containers — the twin requires accelerator lattice data in MongoDB to initialize, or use HIFIS pre-built images with BESSY II data pre-loaded. |
| `science/dtwin-burnin-tests/` | Run comprehensive burn-in tests on the dt4acc Digital Twin IOC to verify EPICS PV stability, throughput, and read/write resilience |
| `science/dtwin-epics-runbook/` | EPICS-first runbook for dt4acc using the current local-repo workflow, with host-side smoke test first and direct EPICS startup for the faster path. |
| `science/dtwin-host-smoke-test/` | Reproducible host-side smoke test for the dt4acc digital twin stack using local dt4acc, dt4acc-lib, and lat2db repos without MongoDB, TANGO, or Apptainer. |
| `science/dtwin-setup/` | Build and run the dt4acc Digital Twin for particle accelerators using Apptainer |
| `science/dtwin-tango-runbook/` | SOLEIL-oriented TANGO runbook for dt4acc, including Tango DB container startup, private data prerequisites, and the recommended debug order after the public host smoke test. |
| `social-media/xitter/` | Interact with X/Twitter via the x-cli terminal client using official X API credentials. Use for posting, reading timelines, searching tweets, liking, retweeting, bookmarks, mentions, and user lookups. |
| `software-development/dask-mcp-docs-first/` | Generate or review Dask Python code only after consulting indexed MCP documentation, using strict version lookup and focused query templates for current APIs and best practices. |
| `software-development/pandas-datashader-mcp-docs-first/` | Write or review pandas and Datashader plotting code only after consulting indexed MCP documentation, using focused query templates for current IO, dtype, aggregation, and rendering APIs. |
| `software-development/paperclip-enable-llm-api/` | Configure the top-level LLM provider block in Paperclip so the instance recognizes the OpenAI backend in current Paperclip versions. |
| `software-development/paperclip-ensure-oss-120b-assistant/` | Verify and, if needed, create the oss-120b-assistant agent in Paperclip after server startup, ensuring it is visible in the agents dashboard. |
| `software-development/python-mcp-docs-first/` | When writing or revising Python code, consult the docs MCP server first for indexed libraries and base API usage on the latest available indexed documentation. |

## Using this repository with Hermes

Add the repository as a tap:

```bash
hermes skills tap add arm2arm/AstroAgentAssistant
```

Then search and install skills from it.

### Browse and search

```bash
hermes skills browse
hermes skills search shboost
hermes skills search reana
hermes skills search gaia
hermes skills search manim
```

### Install example skills

```bash
# Astronomy
hermes skills install arm2arm/AstroAgentAssistant/astronomy/rave-dr6-public-talk-visualizations
hermes skills install arm2arm/AstroAgentAssistant/astronomy/gaia-aip-de-adql

# Creative
hermes skills install arm2arm/AstroAgentAssistant/creative/manim-educational-animation
hermes skills install arm2arm/AstroAgentAssistant/creative/fractal-showcase-animation

# Data science / Python
hermes skills install arm2arm/AstroAgentAssistant/data-science/datashader-019-pipeline
hermes skills install arm2arm/AstroAgentAssistant/python/dask-hvplot-datashader-scientific-plots

# Infrastructure / DevOps
hermes skills install arm2arm/AstroAgentAssistant/infrastructure/docs-mcp-at-aip
hermes skills install arm2arm/AstroAgentAssistant/devops/paperclip-oss120b-external

# REANA
hermes skills install arm2arm/AstroAgentAssistant/reana-workflows/reana-client-config
hermes skills install arm2arm/AstroAgentAssistant/reana-workflows/reana-serial-python

# Research
hermes skills install arm2arm/AstroAgentAssistant/research/drp-paper
hermes skills install arm2arm/AstroAgentAssistant/research/latex-research-paper

# Science
hermes skills install arm2arm/AstroAgentAssistant/science/dtwin-epics-runbook

# Productivity
hermes skills install arm2arm/AstroAgentAssistant/productivity/nextcloud-caldav-calendar-management

# Software development
hermes skills install arm2arm/AstroAgentAssistant/software-development/python-mcp-docs-first
```

### Load a skill in a session

```bash
hermes -s shboost-cmd-plot
hermes -s reana-serial-python-analysis-template -s docs-mcp-at-aip
```

Or simply ask Hermes in chat to use a named skill — it will auto-load the relevant one.

## Security scanning

This repository includes a GitHub Actions workflow at:

- `.github/workflows/secret-scan.yml`

It runs `gitleaks` on pushes to `main`, pull requests, and manual workflow dispatch. This helps catch accidentally committed API keys, tokens, passwords, and private keys.

## Authoring rules

Every skill should contain:
- `SKILL.md`
- clear trigger conditions under `## When to Use`
- numbered `## Procedure` or an actionable workflow section
- `## Pitfalls`
- `## Verification`

Optional support files:
- `references/`
- `templates/`
- `scripts/`
- `assets/`

## AIP-specific operational defaults

- SHBoost public S3 endpoint: `https://s3.data.aip.de:9000`
- SHBoost parquet glob: `s3://shboost2024/shboost_08july2024_pub.parq/*.parquet`
- REANA environment source repo: `https://gitlab-p4n.aip.de/punch_public/reana/environments`
- Common observed REANA environments:
  - `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro.9845`
  - `gitlab-p4n.aip.de:5005/p4nreana/reana-env:py311-astro-ml.2891a60c`
- REANA convention: default memory `32GB`
- Plotting convention for SHBoost CMDs:
  - local Parquet cache
  - PNG only
  - original axes
  - y-axis inverted only
  - `hexbin` density with `512x512` grid
