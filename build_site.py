#!/usr/bin/env python3
"""
build_site.py — Build the Biblical Sanctuary Series website.

Scans D:/bible/bible-studies/sanc-* for all 30 studies,
copies files into docs/studies/, generates mkdocs.yml and index.md,
and copies shared assets from etc-website.
"""

import os
import re
import shutil
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
STUDIES_SRC = Path("D:/bible/bible-studies")
ETC_WEBSITE = Path("D:/bible/etc-website")
DOCS = PROJECT_ROOT / "docs"
DOCS_STUDIES = DOCS / "studies"

# ── Study metadata ─────────────────────────────────────────────────
SHORT_TITLES = {
    "sanc-01": "Why a Sanctuary?",
    "sanc-02": "Tabernacle Architecture",
    "sanc-03": "Sanctuary Furniture",
    "sanc-04": "The Daily Service (Tamid)",
    "sanc-05": "Sacrifice Types",
    "sanc-06": "How Sin Enters the Sanctuary",
    "sanc-07": "The Priesthood",
    "sanc-08": "The Veil",
    "sanc-09": "Day of Atonement Ritual",
    "sanc-10": "Day of Atonement Chiasm",
    "sanc-11": "The Two Goats",
    "sanc-12": "Seven Feasts",
    "sanc-13": "Spring Feasts Fulfilled",
    "sanc-14": "Feast of Trumpets",
    "sanc-15": "Jubilee and Day of Atonement",
    "sanc-16": "Feast of Tabernacles",
    "sanc-17": "Atonement Vocabulary",
    "sanc-18": "Blood Ministry",
    "sanc-19": "Vindication and the Courtroom",
    "sanc-20": "Sanctuary as Salvation Model",
    "sanc-21": "Hebrews: Christ's Heavenly Ministry",
    "sanc-22": "Heavenly Things Purified",
    "sanc-23": "Three Phases of Ministry",
    "sanc-24": "Daniel 7: The Heavenly Court",
    "sanc-25": "Daniel 8:14: Sanctuary Vindicated",
    "sanc-26": "Daniel 9:24: Atonement & Vindication",
    "sanc-27": "Ezekiel & Zechariah: Sanctuary Theology",
    "sanc-28": "Sanctuary Vocabulary in Revelation",
    "sanc-29": "Sanctuary Progression in Revelation",
    "sanc-30": "Grand Synthesis",
}

FULL_TITLES = {
    "sanc-01": "Why did God command the building of a sanctuary, and what purpose does it serve in Scripture?",
    "sanc-02": "What does the tabernacle's three-part architecture reveal about access to God?",
    "sanc-03": "What do the sanctuary furnishings teach about worship, intercession, and the presence of God?",
    "sanc-04": "What does the daily tamid service teach about continual intercession and atonement?",
    "sanc-05": "What are the distinct sacrifice types and what does each accomplish for the worshipper?",
    "sanc-06": "How does confessed sin transfer into the sanctuary, and what problem does this create?",
    "sanc-07": "What does the Levitical priesthood reveal about mediation between God and humanity?",
    "sanc-08": "What does the veil teach about access, separation, and the progressive opening of the way to God?",
    "sanc-09": "What happens on the Day of Atonement and why is it the climax of the ritual year?",
    "sanc-10": "Does the Leviticus 16 ritual follow a chiastic literary structure with theological implications?",
    "sanc-11": "What do the two goats of Yom Kippur represent and how are their roles distinguished?",
    "sanc-12": "What are the seven Leviticus 23 festivals and how do they form a prophetic calendar?",
    "sanc-13": "How were the spring feasts fulfilled in the events of Christ's first coming?",
    "sanc-14": "What does the Feast of Trumpets signify and how does it bridge spring and fall fulfillments?",
    "sanc-15": "How do Jubilee and Day of Atonement connect liberation, restoration, and final judgment?",
    "sanc-16": "What does the Feast of Tabernacles teach about God dwelling with His people?",
    "sanc-17": "What do the Hebrew terms kipper, kapporet, nasa, and salach reveal about atonement theology?",
    "sanc-18": "What role does blood play in the sanctuary system and why is it essential to atonement?",
    "sanc-19": "How does the sanctuary frame judgment as vindication rather than merely punishment?",
    "sanc-20": "Does the sanctuary provide a comprehensive model for the plan of salvation?",
    "sanc-21": "What does Hebrews teach about Christ's current ministry in the heavenly sanctuary?",
    "sanc-22": "Why do the heavenly things need purification and what does this mean for Christ's ministry?",
    "sanc-23": "Does Christ's heavenly ministry involve distinct phases corresponding to daily and yearly services?",
    "sanc-24": "How does Daniel 7's judgment scene reflect sanctuary Day of Atonement imagery?",
    "sanc-25": "What does Daniel 8:14 mean by the sanctuary being vindicated, and when does this occur?",
    "sanc-26": "How does Daniel 9:24 use sanctuary atonement vocabulary to define the Messiah's work?",
    "sanc-27": "How do Ezekiel and Zechariah use sanctuary theology to frame restoration and cleansing?",
    "sanc-28": "How saturated is Revelation with sanctuary vocabulary and imagery?",
    "sanc-29": "Does Revelation follow a sanctuary progression from lampstand through Most Holy Place?",
    "sanc-30": "The Biblical Sanctuary: Grand Synthesis of Studies 1-29",
}

# Cluster groupings
CLUSTERS = [
    {
        "name": "Part 1 -- The Earthly Sanctuary",
        "desc": "What is the sanctuary, why did God command it, and what does every component teach?",
        "studies": ["sanc-01", "sanc-02", "sanc-03"],
    },
    {
        "name": "Part 2 -- The Ritual System",
        "desc": "The sanctuary is a living system of rituals that teach how sin is dealt with, how intercession works, and how final judgment operates.",
        "studies": ["sanc-04", "sanc-05", "sanc-06", "sanc-07", "sanc-08", "sanc-09", "sanc-10", "sanc-11"],
    },
    {
        "name": "Part 3 -- The Festival Calendar",
        "desc": "The Leviticus 23 festivals as a prophetic calendar demonstrating spring feast fulfillment as the pattern for fall feast fulfillment.",
        "studies": ["sanc-12", "sanc-13", "sanc-14", "sanc-15", "sanc-16"],
    },
    {
        "name": "Part 4 -- Atonement & Salvation Theology",
        "desc": "The sanctuary teaches salvation. These studies extract the theological principles embedded in the rituals.",
        "studies": ["sanc-17", "sanc-18", "sanc-19", "sanc-20"],
    },
    {
        "name": "Part 5 -- The Heavenly Sanctuary",
        "desc": "From earthly copy to heavenly reality. What Hebrews teaches about Christ's current ministry.",
        "studies": ["sanc-21", "sanc-22", "sanc-23"],
    },
    {
        "name": "Part 6 -- Sanctuary in Prophecy",
        "desc": "How Daniel and the prophets use sanctuary imagery to frame prophetic events.",
        "studies": ["sanc-24", "sanc-25", "sanc-26", "sanc-27"],
    },
    {
        "name": "Part 7 -- Sanctuary in Revelation",
        "desc": "How Revelation is saturated with sanctuary imagery from chapter 1 to chapter 22.",
        "studies": ["sanc-28", "sanc-29"],
    },
    {
        "name": "Part 8 -- Synthesis",
        "desc": "Complete synthesis of all 29 studies with evidence assessment and final conclusions.",
        "studies": ["sanc-30"],
    },
]

# Standard study files (in display order for nav)
STUDY_FILES = [
    ("CONCLUSION.md", None),           # Landing page (no label = index page)
    ("03-analysis.md", "Analysis"),
    ("02-verses.md", "Verses"),
    ("04-word-studies.md", "Word Studies"),
    ("01-topics.md", "Topics"),
    ("PROMPT.md", "Research Scope"),
]

# Raw data file display names
RAW_DATA_NAMES = {
    "concept-context": "Concept Context",
    "existing-studies": "Existing Studies",
    "greek-parsing": "Greek Parsing",
    "hebrew-parsing": "Hebrew Parsing",
    "naves-topics": "Nave's Topics",
    "parallels": "Cross-Testament Parallels",
    "strongs-lookups": "Strong's Lookups",
    "strongs": "Strong's Lookups",
    "web-research": "Web Research",
    "grammar-references": "Grammar References",
    "evidence-tally": "Evidence Tally",
    "study-db-queries": "Study DB Queries",
    "sanctuary-evidence": "Sanctuary Evidence",
    "per-study-breakdown": "Per-Study Breakdown",
}


def get_raw_data_name(filename: str) -> str:
    """Get a display name for a raw-data file."""
    stem = Path(filename).stem
    if stem in RAW_DATA_NAMES:
        return RAW_DATA_NAMES[stem]
    return stem.replace("-", " ").title()


def find_study_folders() -> list[tuple[str, Path]]:
    """Find all sanc-NN-* folders in the studies source directory."""
    folders = []
    for d in sorted(STUDIES_SRC.iterdir()):
        if d.is_dir() and re.match(r"sanc-\d{2}-", d.name):
            slug = d.name
            num = slug.split("-")[1]
            key = f"sanc-{num}"
            folders.append((key, d))
    return folders


def copy_study(key: str, src: Path, preserved_simples: dict):
    """Copy a study folder into docs/studies/."""
    dest = DOCS_STUDIES / src.name
    dest.mkdir(parents=True, exist_ok=True)

    # Copy standard files
    for fname, _ in STUDY_FILES:
        src_file = src / fname
        if src_file.exists():
            shutil.copy2(src_file, dest / fname)

    # Restore preserved conclusion-simple.md, or copy from source
    simple_path = dest / "conclusion-simple.md"
    if src.name in preserved_simples:
        simple_path.write_text(preserved_simples[src.name], encoding="utf-8")
    else:
        simple_src = src / "conclusion-simple.md"
        if simple_src.exists():
            shutil.copy2(simple_src, dest / "conclusion-simple.md")

    # Copy METADATA.yaml if present
    meta = src / "METADATA.yaml"
    if meta.exists():
        shutil.copy2(meta, dest / "METADATA.yaml")

    # Copy raw-data/ (both .md and .txt files)
    raw_src = src / "raw-data"
    if raw_src.exists() and raw_src.is_dir():
        raw_dest = dest / "raw-data"
        raw_dest.mkdir(parents=True, exist_ok=True)
        for f in raw_src.iterdir():
            if f.is_file():
                # Convert .txt to .md for MkDocs rendering
                if f.suffix == ".txt":
                    dest_file = raw_dest / (f.stem + ".md")
                    content = f.read_text(encoding="utf-8", errors="replace")
                    # Wrap in code block if it looks like raw data
                    dest_file.write_text(f"# {get_raw_data_name(f.name)}\n\n```\n{content}\n```\n", encoding="utf-8")
                else:
                    shutil.copy2(f, raw_dest / f.name)

    return dest


def build_nav_entry(key: str, slug: str) -> dict:
    """Build a nav entry for one study."""
    num = key.split("-")[1]
    short_title = SHORT_TITLES.get(key, slug)
    nav_title = f"{num} -- {short_title}"

    dest = DOCS_STUDIES / slug
    items = []

    # Landing page: conclusion-simple.md if it exists, else CONCLUSION.md
    simple = dest / "conclusion-simple.md"
    conclusion = dest / "CONCLUSION.md"
    if simple.exists():
        items.append(f"studies/{slug}/conclusion-simple.md")
        if conclusion.exists():
            items.append({"Conclusion": f"studies/{slug}/CONCLUSION.md"})
    elif conclusion.exists():
        items.append(f"studies/{slug}/CONCLUSION.md")

    # Other standard files
    for fname, label in STUDY_FILES:
        if label is None:
            continue
        fpath = dest / fname
        if fpath.exists():
            items.append({label: f"studies/{slug}/{fname}"})

    # Raw data files
    raw_dir = dest / "raw-data"
    if raw_dir.exists() and raw_dir.is_dir():
        raw_items = []
        for f in sorted(raw_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                display = get_raw_data_name(f.name)
                raw_items.append({display: f"studies/{slug}/raw-data/{f.name}"})
        if raw_items:
            items.append({"Raw Data": raw_items})

    return {nav_title: items}


def generate_mkdocs_yml(study_folders: list[tuple[str, Path]]):
    """Generate mkdocs.yml."""
    slug_map = {key: src.name for key, src in study_folders}

    lines = []
    lines.append('site_name: "The Biblical Sanctuary"')
    lines.append("site_description: A 30-study comprehensive investigation of the biblical sanctuary from its physical architecture through its theological implications for salvation, prophecy, and Revelation.")
    lines.append("")
    lines.append("theme:")
    lines.append("  name: material")
    lines.append("  palette:")
    lines.append("    - scheme: default")
    lines.append("      primary: indigo")
    lines.append("      accent: amber")
    lines.append("      toggle:")
    lines.append("        icon: material/brightness-7")
    lines.append("        name: Switch to dark mode")
    lines.append("    - scheme: slate")
    lines.append("      primary: indigo")
    lines.append("      accent: amber")
    lines.append("      toggle:")
    lines.append("        icon: material/brightness-4")
    lines.append("        name: Switch to light mode")
    lines.append("  features:")
    lines.append("    - navigation.instant")
    lines.append("    - navigation.tracking")
    lines.append("    - navigation.tabs")
    lines.append("    - navigation.sections")
    lines.append("    - navigation.top")
    lines.append("    - navigation.indexes")
    lines.append("    - search.suggest")
    lines.append("    - search.highlight")
    lines.append("    - content.tabs.link")
    lines.append("    - toc.follow")
    lines.append("  font:")
    lines.append("    text: Roboto")
    lines.append("    code: Roboto Mono")
    lines.append("  custom_dir: overrides")
    lines.append("")
    lines.append("plugins:")
    lines.append("  - search")
    lines.append("")
    lines.append("markdown_extensions:")
    lines.append("  - abbr")
    lines.append("  - admonition")
    lines.append("  - attr_list")
    lines.append("  - def_list")
    lines.append("  - footnotes")
    lines.append("  - md_in_html")
    lines.append("  - tables")
    lines.append("  - toc:")
    lines.append("      permalink: true")
    lines.append("  - pymdownx.details")
    lines.append("  - pymdownx.superfences")
    lines.append("  - pymdownx.highlight:")
    lines.append("      anchor_linenums: true")
    lines.append("  - pymdownx.inlinehilite")
    lines.append("  - pymdownx.tabbed:")
    lines.append("      alternate_style: true")
    lines.append("  - pymdownx.tasklist:")
    lines.append("      custom_checkbox: true")
    lines.append("")
    lines.append("extra:")
    lines.append("  social:")
    lines.append("    - icon: fontawesome/solid/book-bible")
    lines.append("      link: /")
    lines.append("")
    lines.append("extra_javascript:")
    lines.append("  - javascripts/verse-popup.js")
    lines.append("  - javascripts/study-breadcrumbs.js")
    lines.append("  - javascripts/external-links.js")
    lines.append("")
    lines.append("extra_css:")
    lines.append("  - stylesheets/extra.css")
    lines.append("")
    lines.append("nav:")
    lines.append("  - Home: index.md")
    lines.append("  - Studies:")
    lines.append("")

    for cluster in CLUSTERS:
        lines.append(f"    # ── {cluster['name']} ──")
        lines.append(f'    - "{cluster["name"]}":')
        lines.append("")
        for key in cluster["studies"]:
            slug = slug_map.get(key)
            if not slug:
                continue
            nav_entry = build_nav_entry(key, slug)
            for title, items in nav_entry.items():
                lines.append(f'      - "{title}":')
                for item in items:
                    if isinstance(item, str):
                        lines.append(f"        - {item}")
                    elif isinstance(item, dict):
                        for label, val in item.items():
                            if isinstance(val, list):
                                lines.append(f"        - {label}:")
                                for sub in val:
                                    if isinstance(sub, dict):
                                        for slabel, spath in sub.items():
                                            lines.append(f'          - "{slabel}": {spath}')
                                    else:
                                        lines.append(f"          - {sub}")
                            else:
                                lines.append(f"        - {label}: {val}")
        lines.append("")

    lines.append("  - Methodology: methodology.md")
    lines.append('  - "Tools & Process": tools.md')

    yml_path = PROJECT_ROOT / "mkdocs.yml"
    yml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Generated {yml_path}")


def generate_index_md():
    """Generate docs/index.md."""
    content = []

    content.append("# The Biblical Sanctuary: God's Master Illustration")
    content.append("")
    content.append("*A 30-study comprehensive investigation of the biblical sanctuary from its physical architecture through its theological implications for salvation, prophecy, and Revelation. 284 evidence items classified.*")
    content.append("")
    content.append("---")
    content.append("")
    content.append("## The Question")
    content.append("")
    content.append("The sanctuary is the Bible's most detailed visual curriculum. God did not merely describe salvation in words -- He built a physical model of it and prescribed rituals that enact every stage of the plan of redemption. From the courtyard altar to the Most Holy Place, from the daily tamid to the annual Day of Atonement, each element teaches something specific about how God deals with sin, intercedes for sinners, and brings the great controversy to its close.")
    content.append("")
    content.append("This series investigates the sanctuary system from the ground up: What does the Bible actually teach through this institution? How do the earthly rituals connect to Christ's heavenly ministry? And how does sanctuary theology illuminate Daniel, Hebrews, and Revelation?")
    content.append("")
    content.append("## The Approach")
    content.append("")
    content.append("Each study is a genuine investigation. The agents gathered ALL relevant evidence, presented what the biblical text teaches, and classified findings using a rigorous evidence hierarchy:")
    content.append("")
    content.append("- **Explicit (E):** What the text directly says -- a quote or close paraphrase")
    content.append("- **Necessary Implication (N):** What unavoidably follows from explicit statements")
    content.append("- **Inference (I):** What positions claim the text implies, requiring something beyond the text itself")
    content.append("")
    content.append("**Hierarchy:** E > N > I (inferences cannot override explicit statements)")
    content.append("")
    content.append("[**Read the Methodology**](methodology.md){ .md-button }")
    synth_simple = DOCS_STUDIES / "sanc-30-grand-synthesis" / "conclusion-simple.md"
    if synth_simple.exists():
        content.append("[**Skip to the Grand Synthesis**](studies/sanc-30-grand-synthesis/conclusion-simple.md){ .md-button .md-button--primary }")
    else:
        content.append("[**Skip to the Grand Synthesis**](studies/sanc-30-grand-synthesis/CONCLUSION.md){ .md-button .md-button--primary }")
    content.append("")
    content.append("---")
    content.append("")
    content.append("## The 30 Studies")
    content.append("")

    for cluster in CLUSTERS:
        content.append(f"### {cluster['name']}")
        content.append("")
        content.append(cluster["desc"])
        content.append("")
        content.append("| # | Study | Question |")
        content.append("|---|-------|----------|")
        for key in cluster["studies"]:
            num = key.split("-")[1]
            short = SHORT_TITLES.get(key, key)
            full = FULL_TITLES.get(key, short)
            slug = None
            for d in sorted(STUDIES_SRC.iterdir()):
                if d.is_dir() and d.name.startswith(f"{key}-"):
                    slug = d.name
                    break
            if slug:
                simple_path = DOCS_STUDIES / slug / "conclusion-simple.md"
                if simple_path.exists():
                    link = f"studies/{slug}/conclusion-simple.md"
                else:
                    link = f"studies/{slug}/CONCLUSION.md"
                content.append(f"| {num} | [{short}]({link}) | {full} |")
            else:
                content.append(f"| {num} | {short} | {full} |")
        content.append("")

    content.append("---")
    content.append("")
    content.append("## What Each Study Contains")
    content.append("")
    content.append("Every study includes multiple layers of research, all accessible through the navigation:")
    content.append("")
    content.append("| File | Contents |")
    content.append("|------|----------|")
    content.append("| **Simple Conclusion** | A plain-language summary of the study's findings -- no technical jargon or evidence tables |")
    content.append("| **Conclusion** | The final evidence classification with Explicit/Necessary Implication/Inference tables, tally, and assessment |")
    content.append("| **Analysis** | Verse-by-verse analysis, identified patterns, connections between passages |")
    content.append("| **Verses** | Full KJV text for every passage examined, organized thematically |")
    content.append("| **Word Studies** | Hebrew and Greek word studies with Strong's numbers, semantic ranges, and parsing |")
    content.append("| **Topics** | Nave's Topical Bible entries and key research findings |")
    content.append("| **Research Scope** | The original research question and scope that guided the investigation |")
    content.append("| **Raw Data** | Nave's topic output, Strong's lookups, Greek/Hebrew parsing, cross-testament parallels |")
    content.append("")
    content.append("---")
    content.append("")
    content.append("## Evidence Summary (from Study 30)")
    content.append("")
    content.append("Study 30 synthesized the evidence from Studies 1-29 on the sanctuary system. The synthesis classified **284 unique evidence items** across those studies.")
    content.append("")
    content.append("### Evidence by Confidence Tier")
    content.append("")
    content.append("| Tier | Count | Description |")
    content.append("|------|-------|-------------|")
    content.append("| **E (Explicit)** | 185 | Direct textual statements -- what the Bible says about the sanctuary |")
    content.append("| **N (Necessary Implication)** | 80 | What unavoidably follows from combining explicit statements |")
    content.append("| **I (Inference)** | 19 | Conclusions requiring reasoning beyond explicit text |")
    content.append("| **Total** | **284** | |")
    content.append("")
    content.append("### Evidence by Classification")
    content.append("")
    content.append("| Classification | Count | Description |")
    content.append("|---------------|-------|-------------|")
    content.append("| Textual | 129 | Direct statements about sanctuary elements, rituals, and meanings |")
    content.append("| Structural | 58 | Architectural patterns, literary structures, and organizational design |")
    content.append("| Typological | 58 | Type-antitype correspondences between earthly and heavenly realities |")
    content.append("| Neutral | 29 | Background observations supporting multiple conclusions |")
    content.append("| Prophetic | 8 | Sanctuary imagery in prophetic contexts |")
    content.append("| Grammatical | 1 | Evidence from original-language grammar |")
    content.append("| Historicist | 1 | Evidence bearing on historicist interpretation |")
    content.append("")
    content.append("### Confidence Assessment")
    content.append("")
    content.append("The sanctuary evidence base is overwhelmingly grounded in explicit text:")
    content.append("")
    content.append("- **HIGH confidence (E+N):** 265 items (93%) -- direct textual statements and their necessary implications")
    content.append("- **MODERATE confidence (I):** 19 items (7%) -- inferences that extend beyond explicit text")
    content.append("")
    content.append("The sanctuary system is one of the most explicitly documented theological subjects in Scripture. Nearly all findings rest on direct textual evidence rather than inference.")
    content.append("")
    synth_simple2 = DOCS_STUDIES / "sanc-30-grand-synthesis" / "conclusion-simple.md"
    if synth_simple2.exists():
        content.append("[**Read the Grand Synthesis**](studies/sanc-30-grand-synthesis/conclusion-simple.md){ .md-button .md-button--primary }")
    else:
        content.append("[**Read the Grand Synthesis**](studies/sanc-30-grand-synthesis/CONCLUSION.md){ .md-button .md-button--primary }")
    content.append("")
    content.append("---")
    content.append("")
    content.append("## Source Restrictions")
    content.append("")
    content.append("This series uses **no denominational or extra-biblical sources** as authoritative evidence. Permitted sources are:")
    content.append("")
    content.append("- Scripture (KJV text with Hebrew/Greek analysis)")
    content.append("- Secular and church historians (for verifying prophetic claims against historical events)")
    content.append("- Scholarly commentators from all traditions")
    content.append("- Hebrew and Greek lexicons, grammars, and concordances")
    content.append("")
    content.append("The question is always: **What does the Bible say?**")
    content.append("")
    # Hub banner is injected by hub-website/inject_links.py after build

    index_path = DOCS / "index.md"
    index_path.write_text("\n".join(content) + "\n", encoding="utf-8")
    print(f"  Generated {index_path}")


def generate_tools_md():
    """Generate docs/tools.md."""
    content = """# Research Tools & Process

*This page describes the automated research system and investigative methodology that produced the 30 studies in this series.*

---

## Investigative Stance

Each study is produced by an agent that functions as an **investigator, not an advocate.** This distinction governs every step of the process:

- **Gather evidence from all sides.** If a passage is cited by one tradition, examine it honestly. If another tradition reads it differently, examine that reading honestly.
- **Do not assume a conclusion before examining the evidence.** The conclusion emerges FROM the evidence, not the reverse.
- **State what the text says, not opinions about it.** The agent does not use editorial characterizations like "genuine tension," "strongest argument," or "non-intuitive reading." It states what each passage says and what each interpretive position infers from it.
- **Never use language like "irrefutable," "obviously," or "clearly proves."** Use "the text states," "this is consistent with."

---

## How the Studies Were Produced

Each study was generated by a multi-agent pipeline, a Claude Code skill that answers Bible questions through tool-driven research. The pipeline ensures that:

- **Scope comes from tools, not training knowledge.** The AI does not decide which verses are relevant based on what it was trained on. Instead, tools search topical dictionaries, concordances, and semantic indexes to discover what Scripture says about the topic.
- **Research and analysis are separated.** The agent that gathers data is not the same agent that draws conclusions. This prevents confirmation bias.
- **Every claim is traceable.** Raw tool output is preserved in each study's `raw-data/` folder, so every finding can be verified against its source.

### The Three-Agent Pipeline

```
Phase 1: Scoping Agent
   | Discovers topics, verses, Strong's numbers, related studies
   | Writes PROMPT.md (the research brief)

Phase 2: Research Agent
   | Reads PROMPT.md
   | Retrieves all verse text, runs parallels, word studies, parsing
   | Writes 01-topics.md, 02-verses.md, 04-word-studies.md
   | Saves raw tool output to raw-data/

Phase 3: Analysis Agent
   | Reads clean research files
   | Applies the evidence classification methodology
   | Writes 03-analysis.md and CONCLUSION.md
```

**Why three agents instead of one?**

- The **scoping agent** prevents training-knowledge bias. Scope comes from tool discovery, not from what the AI "knows" about theology.
- The **research agent** gets a fresh context window dedicated to data gathering. This maximizes the amount of data it can collect without running out of context.
- The **analysis agent** gets a fresh context window loaded with clean, organized research. This maximizes its capacity for synthesis and careful reasoning.

---

## The Study Files

Each study directory contains these files, produced by the pipeline:

| File | Produced By | Contents |
|------|-------------|----------|
| `PROMPT.md` | Scoping Agent | The research brief: tool-discovered topics, verses, Strong's numbers, related studies, and focus areas |
| `01-topics.md` | Research Agent | Nave's Topical Bible entries with all verse references for each topic |
| `02-verses.md` | Research Agent | Full KJV text for every verse examined, organized thematically |
| `04-word-studies.md` | Research Agent | Strong's concordance data: Hebrew/Greek words, definitions, translation statistics, verse occurrences |
| `raw-data/` | Research Agent | Raw tool output archived by category (Strong's lookups, parsing, parallels, etc.) |
| `03-analysis.md` | Analysis Agent | Verse-by-verse analysis with full evidence classification applied |
| `CONCLUSION.md` | Analysis Agent | Evidence tables (E/N/I), tally, and final assessment |

---

## Data Sources

The tools draw from these primary data sources:

| Source | Description | Size |
|--------|-------------|------|
| **KJV Bible** | Complete King James Version text | 31,102 verses |
| **Nave's Topical Bible** | Orville J. Nave's topical dictionary | 5,319 topics |
| **Strong's Concordance** | James Strong's exhaustive concordance with Hebrew/Greek lexicon | Every word in the KJV mapped to original language |
| **BHSA** (Biblia Hebraica Stuttgartensia Amstelodamensis) | Hebrew Bible linguistic database via Text-Fabric | Full morphological parsing of every Hebrew word |
| **N1904** (Nestle 1904) | Greek New Testament linguistic database via Text-Fabric | Full morphological parsing of every Greek word |
| **Textus Receptus** | Byzantine Greek text tradition | For textual variant comparison |
| **LXX Mapping** | Septuagint translation correspondences | Hebrew-to-Greek word mappings |
| **Sentence embeddings** | Pre-computed semantic vectors | For semantic search across all sources |

---

## Evidence Classification Methodology

The core of the methodology is a three-tier evidence classification system that distinguishes between what Scripture directly states, what necessarily follows from it, and what positions claim it implies.

### The Three Tiers

**E -- Explicit.** "The Bible says X." You can point to a verse that says X. A close paraphrase of the actual words of a specific verse, with no concept, framework, or interpretation added beyond what the words themselves require.

**N -- Necessary Implication.** "The Bible implies X." You can point to verses that, when combined, force X with no alternative. Every reader from any theological position must agree this follows -- no additional reasoning is required.

**I -- Inference.** "A position claims the Bible teaches X." No verse explicitly states X, and no combination of verses necessarily implies X. Something must be added beyond what the text contains.

**Critical rule:** Inferences cannot block explicit statements or necessary implications. If E and N items establish X, the existence of passages that *could be inferred* to teach not-X does not prevent X from being established.

---

### Evidence Classifications

Evidence items in the sanctuary series are classified by the type of biblical data they represent:

- **Textual:** Direct statements about sanctuary elements, rituals, and their stated purposes
- **Structural:** Architectural patterns, literary structures, and organizational design within the sanctuary system
- **Typological:** Type-antitype correspondences between earthly sanctuary services and heavenly realities
- **Prophetic:** Sanctuary imagery used in prophetic contexts (Daniel, Revelation)
- **Grammatical:** Evidence derived from original-language grammar and syntax
- **Neutral:** Background observations that support or inform multiple conclusions

[**Read the Full Methodology**](methodology.md){ .md-button }
"""
    tools_path = DOCS / "tools.md"
    tools_path.write_text(content, encoding="utf-8")
    print(f"  Generated {tools_path}")


def copy_assets():
    """Copy shared assets from etc-website."""
    js_src = ETC_WEBSITE / "docs" / "javascripts"
    js_dest = DOCS / "javascripts"
    js_dest.mkdir(parents=True, exist_ok=True)
    for fname in ["verse-popup.js", "study-breadcrumbs.js", "external-links.js",
                   "verses.json", "strongs.json"]:
        src = js_src / fname
        if src.exists():
            shutil.copy2(src, js_dest / fname)
            print(f"  Copied {fname}")
        else:
            print(f"  WARNING: {src} not found")

    css_src = ETC_WEBSITE / "docs" / "stylesheets" / "extra.css"
    css_dest = DOCS / "stylesheets"
    css_dest.mkdir(parents=True, exist_ok=True)
    if css_src.exists():
        shutil.copy2(css_src, css_dest / "extra.css")
        print(f"  Copied extra.css")


def copy_methodology():
    """Copy sanctuary methodology or fall back to a general methodology."""
    # Try sanctuary-specific methodology first
    src = STUDIES_SRC / "sanc-series-methodology.md"
    if not src.exists():
        # Fall back to the hist-series methodology as a base
        src = STUDIES_SRC / "hist-series-methodology.md"
    dest = DOCS / "methodology.md"
    if src.exists():
        shutil.copy2(src, dest)
        print(f"  Copied methodology.md from {src.name}")
    else:
        print(f"  WARNING: No methodology file found")


def copy_overrides():
    """Copy overrides from hist-website."""
    src = Path("D:/bible/hist-website/overrides/main.html")
    dest = PROJECT_ROOT / "overrides"
    dest.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dest / "main.html")
        print(f"  Copied overrides/main.html")
    else:
        print(f"  WARNING: {src} not found")


def generate_deploy_yml():
    """Generate .github/workflows/deploy.yml."""
    deploy_dir = PROJECT_ROOT / ".github" / "workflows"
    deploy_dir.mkdir(parents=True, exist_ok=True)
    content = """name: Deploy MkDocs to GitHub Pages

on:
  push:
    branches:
      - master

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure Git credentials
        run: |
          git config user.email "action@github.com"
          git config user.name "GitHub Actions"

      - uses: actions/setup-python@v5
        with:
          python-version: 3.x

      - name: Cache MkDocs dependencies
        uses: actions/cache@v4
        with:
          key: mkdocs-material-${{ hashFiles('**/requirements.txt') }}
          path: .cache
          restore-keys: mkdocs-material-

      - name: Install MkDocs Material
        run: pip install mkdocs-material

      - name: Deploy to GitHub Pages
        run: mkdocs gh-deploy --force
"""
    (deploy_dir / "deploy.yml").write_text(content, encoding="utf-8")
    print(f"  Generated deploy.yml")


def generate_gitignore():
    """Generate .gitignore."""
    content = """site/
.venv/
__pycache__/
node_modules/
"""
    (PROJECT_ROOT / ".gitignore").write_text(content, encoding="utf-8")
    print(f"  Generated .gitignore")


def generate_readme(study_folders: list[tuple[str, Path]]):
    """Generate README.md."""
    lines = []
    lines.append("# The Biblical Sanctuary: God's Master Illustration")
    lines.append("")
    lines.append("A 30-study comprehensive investigation of the biblical sanctuary from its physical architecture through its theological implications for salvation, prophecy, and Revelation. 284 evidence items classified.")
    lines.append("")
    lines.append("## Studies")
    lines.append("")
    lines.append("| # | Study | Question |")
    lines.append("|---|-------|----------|")
    for key, src in study_folders:
        num = key.split("-")[1]
        short = SHORT_TITLES.get(key, key)
        full = FULL_TITLES.get(key, short)
        lines.append(f"| {num} | {short} | {full} |")
    lines.append("")
    lines.append("## Built With")
    lines.append("")
    lines.append("- [MkDocs](https://www.mkdocs.org/) with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)")
    lines.append("- Interactive Bible verse and Strong's number popups")
    lines.append("- Full KJV text and Strong's Concordance data")

    (PROJECT_ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Generated README.md")


def main():
    print("=" * 60)
    print("Building Biblical Sanctuary Series website")
    print("=" * 60)

    # Preserve any existing conclusion-simple.md files before cleaning
    preserved_simples = {}
    if DOCS_STUDIES.exists():
        for d in DOCS_STUDIES.iterdir():
            if d.is_dir():
                simple = d / "conclusion-simple.md"
                if simple.exists():
                    preserved_simples[d.name] = simple.read_text(encoding="utf-8")
        shutil.rmtree(DOCS_STUDIES)
    DOCS_STUDIES.mkdir(parents=True)
    print(f"  Preserved {len(preserved_simples)} conclusion-simple.md files")

    # Find all study folders
    print("\n[1/8] Finding study folders...")
    study_folders = find_study_folders()
    print(f"  Found {len(study_folders)} studies")

    # Copy studies
    print("\n[2/8] Copying study files...")
    for key, src in study_folders:
        dest = copy_study(key, src, preserved_simples)
        print(f"  {key}: {src.name} -> {dest.relative_to(PROJECT_ROOT)}")

    # Copy methodology
    print("\n[3/8] Copying methodology...")
    copy_methodology()

    # Copy shared assets
    print("\n[4/8] Copying shared assets from etc-website...")
    copy_assets()

    # Copy overrides
    print("\n[5/8] Copying overrides...")
    copy_overrides()

    # Generate mkdocs.yml
    print("\n[6/8] Generating mkdocs.yml...")
    generate_mkdocs_yml(study_folders)

    # Generate index.md and tools.md
    print("\n[7/8] Generating index.md and tools.md...")
    generate_index_md()
    generate_tools_md()

    # Generate supporting files
    print("\n[8/8] Generating supporting files...")
    generate_deploy_yml()
    generate_gitignore()
    generate_readme(study_folders)

    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"  Studies: {len(study_folders)}")
    print(f"  Output: {DOCS}")
    print("\nNext steps:")
    print("  1. mkdocs serve")
    print("=" * 60)


if __name__ == "__main__":
    main()
