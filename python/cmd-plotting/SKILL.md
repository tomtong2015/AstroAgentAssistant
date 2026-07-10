---
name: cmd-plotting
description: Generate astronomy colour-magnitude diagrams in Python with reproducible plotting choices.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [python, astronomy, plotting, cmd, visualization]
    category: python
    related_skills: [shboost24-cmd, seaborn-paper-plots]
---

# CMD Plotting

## When to Use
Use this skill for colour-magnitude diagrams or related astronomy plots in Python.

## Procedure
1. Keep only required columns.
2. Use consistent axis labeling and explicit units when available.
3. Prefer density representations for large samples.
4. Save publication-ready PNG outputs by default.

## Pitfalls
- Avoid scatter plots for very large datasets when density plots are more appropriate.
- Avoid undocumented axis transformations.
- **For a known cluster, anchor member selection to literature values.** Set the parallax / proper-motion cuts from the cluster's published distance and mean proper motion — not from whatever maximizes the member count. A count-maximizing selection pulls in field stars, smears the main sequence, and makes the turn-off (and any age read-off) wrong.

## Verification
- Plot labels and file outputs match the stated convention.
