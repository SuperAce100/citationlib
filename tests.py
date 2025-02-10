"""
Example usage of the citations library demonstrating different citation styles and formats.
"""

from citationlib import create_citation, Style, Format

def test_citation_styles(url: str) -> None:
    """Test different citation styles for a given URL."""
    print("\n=== Citation Styles ===")
    
    print("\nAPA Style:")
    print(create_citation(url, style=Style.APA))
    
    print("\nMLA Style:")
    print(create_citation(url, style=Style.MLA))
    
    print("\nChicago Style:")
    print(create_citation(url, style=Style.CHICAGO))

def test_output_formats(url: str) -> None:
    """Test different output formats for a given URL."""
    print("\n=== Output Formats ===")
    
    print("\nPlain Text:")
    print(create_citation(url, style=Style.APA, output_format=Format.PLAIN))
    
    print("\nHTML:")
    print(create_citation(url, style=Style.APA, output_format=Format.HTML))
    
    print("\nMarkdown:")
    print(create_citation(url, style=Style.APA, output_format=Format.MARKDOWN))
    
    print("\nLaTeX:")
    print(create_citation(url, style=Style.APA, output_format=Format.LATEX))
    
    print("\nBibTeX:")
    print(create_citation(url, style=Style.APA, output_format=Format.BIBTEX))

if __name__ == "__main__":
    # Test URLs representing different types of sources
    urls = {
        "Academic Paper (Nature)": "https://doi.org/10.1038/s41586-021-03819-2",
        "ArXiv Preprint": "https://arxiv.org/abs/1706.03762",
        "News Article": "https://www.theguardian.com/us-news/2025/feb/09/democrats-aggressive-stand-against-trump",
        "Research Website": "https://research.google/pubs/fairness-and-optimality-in-routing/"
    }
    
    # Test each URL
    for source_type, url in urls.items():
        print(f"\n{'='*50}")
        print(f"Testing {source_type}: {url}")
        try:
            test_citation_styles(url)
            test_output_formats(url)
        except Exception as e:
            print(f"Error: {str(e)}")
    