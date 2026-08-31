import os
import re
import sys
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

DEFAULT_PER_PROVIDER = 5
REQUEST_TIMEOUT = 15

USER_AGENT = (
    "IP-SAKTI-Sahayak/1.0 "
    "(Indian intellectual-property legal-research project)"
)


def normalize_query(query):
    if not query:
        return ""

    query = str(query).strip()

    # Remove excessive whitespace.
    query = re.sub(r"\s+", " ", query)

    return query


def tokenize(text):
    if not text:
        return set()

    text = str(text).lower()

    # Keep words, numbers and useful IP phrases.
    words = re.findall(r"[a-z0-9]+", text)

    return {
        word
        for word in words
        if len(word) >= 2
    }

def detect_ip_topic(query):
    text = normalize_query(query).lower()

    if any(
        phrase in text
        for phrase in [
            "patent",
            "patents",
            "invention",
            "inventor",
            "patented",
        ]
    ):
        return "patent"


    if any(
        phrase in text
        for phrase in [
            "trademark",
            "trade mark",
            "brand mark",
            "brand logo",
            "logo example",
            "logo examples",
        ]
    ):
        return "trademark"

    # Copyright
    if any(
        phrase in text
        for phrase in [
            "copyright",
            "copyrighted",
            "literary work",
            "artistic work",
            "creative work",
        ]
    ):
        return "copyright"

    # Geographical Indication
    if any(
        phrase in text
        for phrase in [
            "geographical indication",
            "geographical indications",
            "gi tag",
            "gi tagged",
            "gi product",
            "gi products",
            "gi tag product",
            "gi tag products",
        ]
    ):
        return "gi"

    # Industrial design
    if any(
        phrase in text
        for phrase in [
            "industrial design",
            "design registration",
            "registered design",
            "product design",
        ]
    ):
        return "design"

    # Plant varieties
    if any(
        phrase in text
        for phrase in [
            "plant variety",
            "plant varieties",
            "farmers variety",
            "seed variety",
        ]
    ):
        return "plant"

    return "general_ip"


# ============================================================
# QUERY EXPANSION
# ============================================================

def build_search_queries(query):
    """
    Build better provider-specific search queries.

    The goal is NOT to blindly add keywords.

    We create a small number of targeted queries depending
    on the detected IP topic.
    """

    query = normalize_query(query)

    if not query:
        return []

    topic = detect_ip_topic(query)

    queries = []

    # --------------------------------------------------------
    # PATENT
    # --------------------------------------------------------

    if topic == "patent":

        queries.extend(
            [
                f"{query} patent document",
                f"Indian patent document",
                f"patent application India",
                f"patent certificate India",
            ]
        )

    # --------------------------------------------------------
    # TRADEMARK
    # --------------------------------------------------------

    elif topic == "trademark":

        queries.extend(
            [
                f"{query} trademark",
                f"Indian trademark registration",
                f"Indian trademark logo",
                f"trademark registration certificate India",
            ]
        )



    elif topic == "gi":

        queries.extend(
            [
                f"{query} India GI product",
                f"Indian geographical indication product",
                f"India GI tagged product",
                f"Indian GI handicraft food product",
            ]
        )


    elif topic == "copyright":

        queries.extend(
            [
                f"{query} copyright India",
                f"Indian copyright registration",
                f"copyright certificate India",
                f"copyright law India",
            ]
        )


    elif topic == "design":

        queries.extend(
            [
                f"{query} industrial design India",
                f"registered design India",
                f"industrial design registration India",
            ]
        )


    elif topic == "plant":

        queries.extend(
            [
                f"{query} India plant variety",
                f"Indian plant variety",
                f"plant variety protection India",
            ]
        )


    else:

        queries.extend(
            [
                query,
                f"{query} India",
                f"{query} intellectual property India",
            ]
        )

    
    unique_queries = []

    seen = set()

    for item in queries:

        item = normalize_query(item)

        key = item.lower()

        if not item or key in seen:
            continue

        seen.add(key)
        unique_queries.append(item)

    return unique_queries


def search_pexels(query, per_page=5):

    if not PEXELS_API_KEY:
        print("Pexels API key not configured.")
        return []

    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": PEXELS_API_KEY,
    }

    params = {
        "query": query,
        "per_page": per_page,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for photo in data.get("photos", []):

        src = photo.get("src", {})

        image_url = src.get("large")

        if not image_url:
            continue

        results.append(
            {
                "url": image_url,
                "thumbnail": src.get("medium"),
                "title": photo.get("alt") or query,
                "source": "pexels",
                "author": photo.get("photographer"),
                "source_url": photo.get("url"),
                "provider_id": photo.get("id"),
                "width": photo.get("width"),
                "height": photo.get("height"),
                "search_query": query,
            }
        )

    return results


def search_unsplash(query, per_page=5):

    if not UNSPLASH_ACCESS_KEY:
        print("Unsplash access key not configured.")
        return []

    url = "https://api.unsplash.com/search/photos"

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}",
    }

    params = {
        "query": query,
        "per_page": per_page,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    for photo in data.get("results", []):

        user = photo.get("user", {})

        title = (
            photo.get("alt_description")
            or photo.get("description")
            or query
        )

        urls = photo.get("urls", {})

        image_url = urls.get("regular")

        if not image_url:
            continue

        results.append(
            {
                "url": image_url,
                "thumbnail": urls.get("small"),
                "title": title,
                "source": "unsplash",
                "author": user.get("name"),
                "source_url": photo.get("links", {}).get("html"),
                "provider_id": photo.get("id"),
                "width": photo.get("width"),
                "height": photo.get("height"),
                "search_query": query,
            }
        )

    return results


def search_wikimedia(query, per_page=5):

    url = "https://commons.wikimedia.org/w/api.php"

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": per_page,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1200,
        "format": "json",
    }

    headers = {
        "User-Agent": USER_AGENT,
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    results = []

    pages = data.get("query", {}).get("pages", {})

    for page in pages.values():

        image_info = page.get("imageinfo", [])

        if not image_info:
            continue

        info = image_info[0]

        image_url = (
            info.get("thumburl")
            or info.get("url")
        )

        if not image_url:
            continue

        results.append(
            {
                "url": image_url,
                "thumbnail": (
                    info.get("thumburl")
                    or info.get("url")
                ),
                "title": page.get("title"),
                "source": "wikimedia",
                "author": None,
                "source_url": info.get("descriptionurl"),
                "provider_id": page.get("pageid"),
                "width": None,
                "height": None,
                "search_query": query,
            }
        )

    return results

def remove_duplicates(results):

    seen = set()

    unique_results = []

    for result in results:

        url = result.get("url")

        if not url:
            continue

        # Normalize URL slightly.
        normalized_url = url.split("?")[0].rstrip("/")

        if normalized_url in seen:
            continue

        seen.add(normalized_url)

        unique_results.append(result)

    return unique_results

def clean_title(title):

    if not title:
        return ""

    title = str(title).lower()
    title = re.sub(r"^file:\s*", "", title)
    title = re.sub(r"[_\-]+", " ", title)

    title = re.sub(
        r"\.(jpg|jpeg|png|gif|svg|webp|pdf|djvu)$",
        "",
        title,
        flags=re.IGNORECASE,
    )

    title = re.sub(r"\s+", " ", title)

    return title.strip()

def get_result_text(result):

    title = result.get("title", "")
    search_query = result.get("search_query", "")

    return clean_title(
        f"{title} {search_query}"
    )


GENERIC_NEGATIVE_TERMS = {
    "graduation",
    "graduate",
    "university",
    "college",
    "diploma",
    "degree",
    "school",
    "classroom",
    "student",
    "teacher",
    "exam",
    "military",
    "air force",
    "navy",
    "army",
    "warship",
    "soldier",
    "battle",
    "weapon",
    "gun",
    "helicopter",
    "aircraft",
    "motorcycle",
    "motorbike",
    "car",
    "automobile",
    "racing",
    "football",
    "cricket",
    "basketball",
    "concert",
    "music",
    "wedding",
    "portrait",
    "selfie",
    "travel",
    "tourism",
    "landscape",
    "sunset",
    "nature",
    "beach",
    "ocean",
}

TOPIC_KEYWORDS = {

    "patent": {
        "patent": 12,
        "patents": 12,
        "invention": 8,
        "inventor": 7,
        "patented": 9,
        "patent application": 12,
        "patent document": 15,
        "patent certificate": 15,
        "patent drawing": 13,
        "patent illustration": 10,
        "intellectual property": 8,
        "india": 3,
        "indian": 3,
    },

    "trademark": {
        "trademark": 15,
        "trade mark": 15,
        "trademarks": 15,
        "brand": 5,
        "brand mark": 12,
        "logo": 7,
        "registration": 5,
        "registered": 5,
        "certificate": 7,
        "intellectual property": 7,
        "india": 3,
        "indian": 3,
    },

    "copyright": {
        "copyright": 15,
        "copyrighted": 13,
        "creative work": 8,
        "literary": 8,
        "artistic": 8,
        "author": 5,
        "creator": 5,
        "book": 3,
        "music": 3,
        "india": 3,
        "indian": 3,
    },

    "gi": {
        "geographical indication": 18,
        "geographical indications": 18,
        "gi tag": 18,
        "gi tagged": 18,
        "gi product": 16,
        "gi products": 16,
        "gi registration": 12,
        "geographical": 7,
        "indication": 6,
        "india": 5,
        "indian": 5,
        "handicraft": 7,
        "handicrafts": 7,
        "artisan": 5,
        "food": 4,
        "textile": 4,
        "product": 4,
    },

    "design": {
        "industrial design": 16,
        "registered design": 15,
        "design registration": 15,
        "product design": 10,
        "industrial": 7,
        "design": 8,
        "registration": 5,
        "india": 3,
        "indian": 3,
    },

    "plant": {
        "plant variety": 17,
        "plant varieties": 17,
        "seed variety": 12,
        "crop variety": 12,
        "plant": 5,
        "agriculture": 5,
        "farmer": 5,
        "india": 3,
        "indian": 3,
    },

    "general_ip": {
        "intellectual property": 15,
        "intellectual": 8,
        "property": 4,
        "law": 3,
        "legal": 3,
        "india": 3,
        "indian": 3,
    },
}

def score_image_relevance(query, result):
    query_text = query.lower().strip()

    title = str(result.get("title", "")).lower()
    source = str(result.get("source", "")).lower()

    # Normalize text
    query_text = re.sub(r"[^a-z0-9\s]", " ", query_text)
    title = re.sub(r"[^a-z0-9\s]", " ", title)

    query_words = {
        word
        for word in query_text.split()
        if len(word) >= 3
    }

    title_words = set(title.split())
    score = 0
    if query_text in title:
        score += 15


    for word in query_words:
        if word in title_words:
            score += 4



    keyword_groups = {
        "trademark": {
            "trademark": 15,
            "logo": 8,
            "brand": 6,
            "registration": 6,
            "registered": 6,
        },

        "patent": {
            "patent": 15,
            "invention": 8,
            "inventor": 6,
            "registration": 5,
        },

        "copyright": {
            "copyright": 15,
            "creative": 5,
            "author": 5,
            "work": 3,
        },

        "geographical indication": {
            "geographical": 15,
            "indication": 10,
            "gi": 8,
            "product": 4,
        },

        "design": {
            "design": 12,
            "industrial": 6,
            "registration": 5,
        },
    }

    # Detect requested topic
    detected_group = None

    for group_name in keyword_groups:
        if group_name in query_text:
            detected_group = group_name
            break

    if detected_group:
        keywords = keyword_groups[detected_group]

        for keyword, points in keywords.items():
            if keyword in title:
                score += points


    india_terms = {
        "india",
        "indian",
        "bharat",
    }

    if query_words.intersection(india_terms):
        if any(term in title for term in india_terms):
            score += 10

    negative_keywords = {
        "graduation": -15,
        "graduate": -15,
        "university": -12,
        "diploma": -12,
        "degree": -12,
        "academic": -10,
        "school": -10,
        "college": -10,
        "citizenship": -15,
        "passport": -12,
        "banknote": -12,
        "currency": -12,
        "money": -10,
        "rupee": -10,
        "air force": -15,
        "journalism": -10,
    }

    for keyword, points in negative_keywords.items():
        if keyword in title:
            score += points

    matched_words = query_words.intersection(title_words)

    if query_words and not matched_words:
        score -= 5

    if source == "wikimedia":
        score += 2

    return score



def is_reasonably_relevant(query, result, score):

    title = clean_title(result.get("title", ""))
    topic = detect_ip_topic(query)
    hard_negative_terms = {
        "motorcycle",
        "motorbike",
        "helicopter",
        "air force",
        "navy",
        "army",
        "graduation",
        "university",
        "college",
        "football",
        "cricket",
        "wedding",
    }

    if any(
        term in title
        for term in hard_negative_terms
    ):

        topic_present = any(
            keyword in title
            for keyword in TOPIC_KEYWORDS.get(
                topic,
                {},
            )
        )

        if not topic_present:
            return False
        
    if score < -5:
        return False

    return True


def search_provider_queries(
    query,
    per_provider=DEFAULT_PER_PROVIDER,
):
    queries = build_search_queries(query)
    fetch_per_query = max(3, per_provider)
    all_results = []


    if PEXELS_API_KEY:

        for search_query in queries[:3]:

            try:

                results = search_pexels(
                    search_query,
                    fetch_per_query,
                )

                all_results.extend(results)

            except Exception as error:

                print(
                    f"Pexels search failed "
                    f"for '{search_query}': {error}"
                )



    if UNSPLASH_ACCESS_KEY:
        for search_query in queries[:3]:
            try:
                results = search_unsplash(
                    search_query,
                    fetch_per_query,
                )

                all_results.extend(results)

            except Exception as error:

                print(
                    f"Unsplash search failed "
                    f"for '{search_query}': {error}"
                )

    for search_query in queries[:4]:

        try:

            results = search_wikimedia(
                search_query,
                fetch_per_query,
            )

            all_results.extend(results)

        except Exception as error:

            print(
                f"Wikimedia search failed "
                f"for '{search_query}': {error}"
            )

    return all_results

def diversify_results(results, per_provider):
    grouped = {}
    for result in results:
        source = result.get("source", "unknown")
        grouped.setdefault(source, []).append(result)

    final_results = []

    max_from_provider = max(
        per_provider,
        1,
    )

    provider_names = list(grouped.keys())

    index = 0

    while len(final_results) < per_provider * 3:

        added_this_round = False

        for provider in provider_names:

            provider_results = grouped.get(
                provider,
                [],
            )

            if index >= len(provider_results):
                continue

            result = provider_results[index]

            if provider_results:

                final_results.append(result)

                added_this_round = True

                if len(final_results) >= per_provider * 3:
                    break

        if not added_this_round:
            break

        index += 1

    return final_results


def search_images(
    query,
    per_provider=DEFAULT_PER_PROVIDER,
):

    query = normalize_query(query)

    if not query:
        return []
    
    all_results = search_provider_queries(
        query,
        per_provider=per_provider,
    )

    all_results = remove_duplicates(
        all_results
    )

    scored_results = []

    for result in all_results:

        score = score_image_relevance(
            query,
            result,
        )

        result["relevance_score"] = score
        if is_reasonably_relevant(
            query,
            result,
            score,
        ):
            scored_results.append(result)

    scored_results.sort(
        key=lambda result: (
            result.get("relevance_score", 0),
            result.get("source", ""),
        ),
        reverse=True,
    )

    final_results = diversify_results(
        scored_results,
        per_provider,
    )

    final_results.sort(
        key=lambda result: result.get(
            "relevance_score",
            0,
        ),
        reverse=True,
    )
    max_results = per_provider * 3

    return final_results[:max_results]

if __name__ == "__main__":

    query = " ".join(
        sys.argv[1:]
    ).strip()

    if not query:

        print("Usage:")
        print(
            'python -m backend.image_search '
            '"Indian patent"'
        )

        sys.exit(1)

    print(
        f"\nSearching images for: {query}\n"
    )

    print(
        "Detected topic:",
        detect_ip_topic(query),
    )

    print(
        "Search queries:"
    )

    for search_query in build_search_queries(query):

        print(
            f"  - {search_query}"
        )

    print()

    results = search_images(
        query
    )

    print(
        f"Found {len(results)} images\n"
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"{index}. {result.get('source')}"
        )

        print(
            f"   Score: "
            f"{result.get('relevance_score', 0)}"
        )

        print(
            f"   Title: "
            f"{result.get('title')}"
        )

        print(
            f"   Author: "
            f"{result.get('author')}"
        )

        print(
            f"   URL: "
            f"{result.get('url')}"
        )

        print(
            f"   Source: "
            f"{result.get('source_url')}"
        )

        print()