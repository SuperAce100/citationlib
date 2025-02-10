"""
Example usage of the citations library demonstrating different citation styles and formats.
"""

import concurrent.futures
import time
from datetime import datetime
from urllib.parse import urlparse
from src import create_citation, Style, Format, Citation, Author

def create_url_citation(url: str, style: Style) -> str:
    """Create a citation from just the URL when metadata extraction fails."""
    # Parse URL to get domain and path
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Create a title from the path
    title = path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
    if not title:
        title = domain
    
    # Create citation with minimal information
    citation = Citation(
        authors=[],  # No authors available
        title=title,
        year=datetime.now().year,  # Current year as access year
        url=url,
        accessed_date=datetime.now(),
        publisher=domain.split('.')[0].title()  # Use domain as publisher
    )
    
    # Format based on style
    if style == Style.APA:
        return f"{title}. ({datetime.now().year}). Retrieved from {url}"
    elif style == Style.MLA:
        return f'"{title}". {domain}, {datetime.now().year}, {url}'
    else:  # Chicago
        return f'"{title}". {domain}. Accessed {datetime.now().strftime("%B %d, %Y")}. {url}'

def process_citation(url: str) -> tuple[str, str, str]:
    """Process a URL in all three citation styles."""
    try:
        apa = create_citation(url, style=Style.APA)
        time.sleep(1)  # Add delay between requests
        mla = create_citation(url, style=Style.MLA)
        time.sleep(1)  # Add delay between requests
        chicago = create_citation(url, style=Style.CHICAGO)
        return apa, mla, chicago
    except Exception as e:
        print(f"Warning: Using URL-based citation for {url}: {str(e)}")
        return (
            create_url_citation(url, Style.APA),
            create_url_citation(url, Style.MLA),
            create_url_citation(url, Style.CHICAGO)
        )

if __name__ == "__main__":
    # Example usage with a variety of common academic and web sources
    references = [
        # Academic journal articles (DOIs)
        "https://doi.org/10.1038/s41586-021-03819-2",  # Nature article
        "https://doi.org/10.1080/00461520.2012.722805",  # Science article
        
        # arXiv preprints
        "https://arxiv.org/abs/2401.03428",  # Recent AI paper
        "https://arxiv.org/abs/1706.03762",  # Attention Is All You Need
        "https://arxiv.org/abs/2303.08774",  # GPT-4 Technical Report
        
        # News and Media websites
        "https://www.nytimes.com/2025/02/09/world/europe/israel-gaza-netzarim.html",
        "https://www.theguardian.com/us-news/2025/feb/09/democrats-aggressive-stand-against-trump",
        "https://www.wired.com/story/elon-musk-doge-recruiting-palantir/",
        
        # Academic and Research websites
        "https://plato.stanford.edu/entries/artificial-intelligence/",
        "https://www.nih.gov/news-events/nih-research-matters/testing-transmission-infection-h5n1-cows",
        "https://pubmed.ncbi.nlm.nih.gov/38977017/",
        "https://www.sciencedirect.com/science/article/pii/S0004370221000862",
        
        # Technical websites and Blogs
        "https://openai.com/research/gpt-4",
        "https://research.google/pubs/fairness-and-optimality-in-routing/",
        "https://research.google/blog/chain-of-agents-large-language-models-collaborating-on-long-context-tasks/",
        "https://research.facebook.com/publications/fast-point-cloud-generation-with-straight-flows/",
        
        # Government and Organization websites
        "https://www.whitehouse.gov/presidential-actions/2025/02/gulf-of-america-day-2025//",
        "https://www.unesco.org/en/artificial-intelligence",
        "https://www.who.int/news-room/fact-sheets/detail/adolescents-health-risks-and-solutions"
    ]
    
    # Demonstrate different citation styles
    print("=== Citation Styles Demo ===\n")
    url = "https://doi.org/10.1038/s41586-021-03819-2"  # Nature article
    
    print("APA Style:")
    print(create_citation(url, style=Style.APA))
    print()
    
    print("MLA Style:")
    print(create_citation(url, style=Style.MLA))
    print()
    
    print("Chicago Style:")
    print(create_citation(url, style=Style.CHICAGO))
    print("\n")
    
    # Demonstrate different output formats
    print("=== Output Formats Demo ===\n")
    url = "https://arxiv.org/abs/1706.03762"  # Attention Is All You Need
    
    print("Plain Text:")
    print(create_citation(url, style=Style.APA, output_format=Format.PLAIN))
    print()
    
    print("HTML:")
    print(create_citation(url, style=Style.APA, output_format=Format.HTML))
    print()
    
    print("Markdown:")
    print(create_citation(url, style=Style.APA, output_format=Format.MARKDOWN))
    print()
    
    print("LaTeX:")
    print(create_citation(url, style=Style.APA, output_format=Format.LATEX))
    print()
    
    print("BibTeX:")
    print(create_citation(url, style=Style.APA, output_format=Format.BIBTEX))
    print("\n")
    
    # Batch process citations with different styles
    print("=== Batch Processing Demo ===\n")
    
    print("Processing citations in parallel...\n")
    # Use a smaller number of workers and process in batches
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_citation, references))
        
    for i, (apa, mla, chicago) in enumerate(results, 1):
        print(f"Reference {i}:")
        print(f"APA:     {apa}")
        print(f"MLA:     {mla}")
        print(f"Chicago: {chicago}")
        print()

    # print("Extracting authors from various sources...\n")
    # for i, ref in enumerate(references, 1):
    #     print(f"{i}. {ref}")
    #     authors = extract_authors(ref)
    #     if authors:
    #         for j, author in enumerate(authors, 1):
    #             print(f"   {j}. {author}")
    #     else:
    #         print("   No authors found")
    #     print()

    # # Test PubMed citation
    # pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/38977017/"
    # print("Testing PubMed citation extraction...\n")
    # print(f"URL: {pubmed_url}")
    # citation = create_citation(pubmed_url)
    # print(f"\nCitation:\n{citation}\n")

    # pcm_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3159421/"
    # print("Testing PMC citation extraction...\n")
    # print(f"URL: {pcm_url}")
    # citation = create_citation(pcm_url)
    # print(f"\nCitation:\n{citation}\n")
    
    