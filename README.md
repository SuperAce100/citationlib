# CitationLib

A powerful Python library for generating academic citations from various sources including DOIs, arXiv papers, PubMed articles, and web pages. The library supports multiple citation styles and output formats.

## Features

- **Multiple Citation Styles**
  - APA (7th edition)
  - MLA (9th edition)
  - Chicago (17th edition)

- **Various Output Formats**
  - Plain text
  - HTML
  - Markdown
  - LaTeX
  - BibTeX

- **Source Support**
  - DOI (Digital Object Identifier)
  - arXiv papers
  - PubMed articles
  - PMC articles
  - General web pages
  - News articles

## Installation

```bash
pip install citationlib
```

## Quick Start

```python
from citationlib import create_citation, Style, Format

# Basic usage - defaults to APA style and plain text format
citation = create_citation("https://doi.org/10.1038/s41586-021-03819-2")
print(citation)

# Using different citation styles
mla_citation = create_citation(
    "https://arxiv.org/abs/2303.08774",
    style=Style.MLA
)
print(mla_citation)

# Different output formats
latex_citation = create_citation(
    "https://www.nature.com/articles/s41586-021-03819-2",
    style=Style.CHICAGO,
    output_format=Format.LATEX
)
print(latex_citation)

# BibTeX output
bibtex_entry = create_citation(
    "https://arxiv.org/abs/1706.03762",
    output_format=Format.BIBTEX
)
print(bibtex_entry)
```

## Detailed Usage

### Citation Styles

The library supports three major citation styles:

```python
from citationlib import create_citation, Style

# APA (7th edition)
apa_citation = create_citation(url, style=Style.APA)

# MLA (9th edition)
mla_citation = create_citation(url, style=Style.MLA)

# Chicago (17th edition)
chicago_citation = create_citation(url, style=Style.CHICAGO)
```

### Output Formats

Choose from five different output formats:

```python
from citationlib import create_citation, Format

# Plain text (default)
text_citation = create_citation(url, output_format=Format.PLAIN)

# HTML
html_citation = create_citation(url, output_format=Format.HTML)

# Markdown
md_citation = create_citation(url, output_format=Format.MARKDOWN)

# LaTeX
latex_citation = create_citation(url, output_format=Format.LATEX)

# BibTeX
bibtex_citation = create_citation(url, output_format=Format.BIBTEX)
```

### Example with Different Sources

The library supports various types of academic sources:

```python
# Academic paper from Nature
doi_citation = create_citation("https://doi.org/10.1038/s41586-021-03819-2")

# ArXiv preprint
arxiv_citation = create_citation("https://arxiv.org/abs/1706.03762")

# News article
news_citation = create_citation("https://www.theguardian.com/us-news/2025/feb/09/democrats-aggressive-stand-against-trump")

# Research website
website_citation = create_citation("https://research.google/pubs/fairness-and-optimality-in-routing/")
```

## Error Handling

The library provides proper error handling for various scenarios:

```python
from citationlib import create_citation

try:
    citation = create_citation("https://example.com/invalid-paper")
except Exception as e:
    print(f"Failed to create citation: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 