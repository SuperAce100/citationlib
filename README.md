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
from citations import create_citation, Style, Format

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
from citations import Style

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
from citations import Format

# Plain text
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

### Extracting Authors

You can extract author information separately:

```python
from citations import extract_authors

authors = extract_authors("https://doi.org/10.1038/s41586-021-03819-2")
for author in authors:
    print(f"{author.last_name}, {author.first_name}")
```

## Error Handling

The library uses custom exceptions for better error handling:

```python
from citations import create_citation, CitationError

try:
    citation = create_citation("https://example.com/invalid-paper")
except CitationError as e:
    print(f"Failed to create citation: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 