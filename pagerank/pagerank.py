import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
 
    corpus = crawl(sys.argv[1])

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            # print(contents)
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            # print(links)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    trans = dict()
    
    for filename in corpus:
        trans[filename] = 0.0
        if filename in corpus[page]:
            trans[filename] = damping_factor / len(corpus[page])
        trans[filename] += round((1 - damping_factor) / len(corpus), 4)
    return trans


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize the ranks dictionary with zero for all the pages
    ranks = dict()
    for page in corpus:
        ranks[page] = 0
    
    # Generate samples and keep track of how many times each page has shown up
    for x in range(n):
        # Random start page
        if x == 0:
            current_page = random.choice(list(corpus))
        # Chose a page pseudorandomly based on the transition distribution
        else:
            trans = transition_model(corpus, current_page, DAMPING)
            current_page = random.choices(list(trans.keys()), weights=trans.values(), k=1)[0]
        ranks[current_page] += 1
    
    # normalize the probabilities
    for page in ranks:
        ranks[page] /= n

    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize the dictionary to keep track of current ranks
    # Begin by assigning each page a rank of 1 / N
    curr_ranks = dict()
    for page in corpus:
        curr_ranks[page] = 1 / len(corpus)

    # Initialize the dictionary to calculate new ranks
    new_ranks = dict()

    # The 1 - d probability of choosing a page at random is split evenly among all N possible pages
    split_prob = round((1 - damping_factor) / len(corpus), 4)
    
    # Calculate a new set of PageRank values for each page until convergence
    while True:
        for ranked in curr_ranks:
            links_prob = 0
            # The d probability of choosing a page based on the PageRanks of all pages that link to it
            for page in corpus:
                if ranked in corpus[page]:
                    links_prob += curr_ranks[page] / len(corpus[page])
                # A page that has no links is interpreted as having links for every page including itself
                elif len(corpus[page]) == 0:
                    links_prob += curr_ranks[page] / len(corpus)
            links_prob *= damping_factor
            # Adding up the two probabilities
            new_ranks[ranked] = split_prob + links_prob
        # Compare current rank values and the new rank values
        if convergence(curr_ranks, new_ranks):
            break
        # Update rank values
        for ranked in curr_ranks:
            curr_ranks[ranked] = new_ranks[ranked]
    
    return curr_ranks

# Convergence occurs when no PageRank value changes by more than 0.001 between iterations
def convergence(curr_ranks, new_ranks):
    for ranked in curr_ranks:
        if curr_ranks[ranked] - new_ranks[ranked] > 0.001:
            return False 
        elif curr_ranks[ranked] - new_ranks[ranked] < -0.001:
            return False 
    return True


if __name__ == "__main__":
    main()