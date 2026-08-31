import os
import re
import sys
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

from backend.image_query import generate_image_query

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

PROVIDERS = [
    "pexels",
    "unsplash",
    "wikimedia",
]

DEFAULT_PER_PROVIDER = 5
DEFAULT_MAX_IMAGES = 4
REQUEST_TIMEOUT = 15

IMAGE_QUERY_MAP = {

    "ayurvedic medicinal plants": [
        "Indian Ayurvedic medicinal plants",
        "Indian medicinal herbs Ayurveda",
        "amla turmeric neem tulsi ashwagandha medicinal plants",
        "Ayurvedic herbs India",
    ],

    "ayurvedic medicine": [
        "Ayurvedic medicine India",
        "traditional Indian herbal medicine",
        "Ayurvedic herbs and medicine",
    ],

    "indian traditional medicine": [
        "Indian Ayurveda traditional medicine",
        "Indian herbal medicine",
        "Ayurvedic treatment India",
    ],

    "gi tagged indian product": [
        "Indian GI tagged products",
        "Indian GI handicrafts",
        "Indian geographical indication products",
        "Indian traditional GI products",
    ],

    "indian patent": [
        "Indian patent",
        "Indian patent document",
        "Indian patent certificate",
        "Indian patent application",
        "Indian invention patent",
        "patent document India",
    ],

    "patent": [
        "patent document invention",
        "patent certificate",
        "patent technical drawing",
        "invention technical drawing",
    ],


    "trademark": [
        "Indian trademark logo",
        "trademark registration certificate",
        "brand trademark logo",
    ],

    "copyright": [
        "copyright certificate India",
        "copyright creative work",
        "copyright document",
    ],
}

def clean_search_query(query: Any) -> str:
    query = str(query or "").strip()

    if not query:
        return ""

    phrases = [
        r"\bshow me\b",
        r"\bshow us\b",
        r"\bcan you show\b",
        r"\bplease show\b",
        r"\bfind me\b",
        r"\bfind some\b",
        r"\bgive me\b",
        r"\bimages of\b",
        r"\bpictures of\b",
        r"\bphotos of\b",
        r"\bimage of\b",
        r"\bpicture of\b",
        r"\bphoto of\b",
        r"\bshow\b",
        r"\bimages\b",
        r"\bpictures\b",
        r"\bphotos\b",
    ]
    for pattern in phrases:
        query = re.sub(
            pattern,
            "",
            query,
            flags=re.IGNORECASE,
        )
    query = re.sub(r"\s+", " ", query).strip()

    return query

def normalize_text(text: Any) -> str:
    text = str(text or "").lower()

    text = text.replace("_", " ")
    text = text.replace("-", " ")
    text = text.replace("/", " ")

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()

def detect_query_category(query: Any) -> str:
    text = normalize_text(query)
    if (
        "geographical indication" in text
        or "gi tag" in text
        or "gi tagged" in text
        or "gi product" in text
        or "gi products" in text
    ):
        return "gi"

    if "patent" in text:
        return "patent"

    if "trademark" in text:
        return "trademark"

    if "copyright" in text:
        return "copyright"

    if "traditional knowledge" in text:
        return "traditional_knowledge"

    if (
        "ayurveda" in text
        or "ayurvedic" in text
        or "medicinal plant" in text
        or "medicinal plants" in text
        or "medicinal herb" in text
        or "medicinal herbs" in text
        or "herbal medicine" in text
    ):
        return "ayurveda"

    if (
        "device" in text
        or "machine" in text
        or "invention" in text
        or "technology" in text
        or "engineering" in text
    ):
        return "invention"

    return "general"

def query_mentions_india(query: Any) -> bool:
    text = normalize_text(query)

    return (
        "india" in text
        or "indian" in text
    )

def build_provider_query(
    query: Any,
    provider: str,
) -> str:
    cleaned = clean_search_query(query)

    if not cleaned:
        return ""

    category = detect_query_category(cleaned)

    india_requested = query_mentions_india(cleaned)
    if category == "ayurveda":

        if provider == "pexels":
            return (
                "Indian medicinal plants herbs "
                "amla turmeric neem tulsi"
            )

        if provider == "unsplash":
            return (
                "Indian medicinal herbs "
                "Ayurveda plants spices"
            )

        if provider == "wikimedia":
            return (
                "Indian medicinal plants "
                "Ayurvedic herbs"
            )
        
    if category == "gi":

        if provider == "pexels":
            return (
                "Indian traditional handicrafts "
                "Indian products artisan"
            )

        if provider == "unsplash":
            return (
                "Indian handicrafts traditional products"
            )

        if provider == "wikimedia":
            return (
                "Indian geographical indication "
                "handicrafts products"
            )

    if category == "patent":

        if india_requested:

            if provider == "pexels":
                return (
                    "Indian patent document "
                    "Indian invention patent"
                )

            if provider == "unsplash":
                return (
                    "Indian patent document "
                    "patent India invention"
                )

            if provider == "wikimedia":
                return (
                    "Indian patent "
                    "India patent document invention"
                )

        if provider == "pexels":
            return (
                "patent document invention "
                "technical drawing"
            )

        if provider == "unsplash":
            return (
                "patent document invention "
                "technical drawing"
            )

        if provider == "wikimedia":
            return (
                "patent invention "
                "patent document"
            )

    if category == "trademark":

        if provider == "pexels":
            return (
                "trademark logo brand identity"
            )

        if provider == "unsplash":
            return (
                "brand logo trademark"
            )

        if provider == "wikimedia":
            return (
                "trademark logo brand India"
            )

    if category == "copyright":

        if provider == "pexels":
            return (
                "copyright creative work "
                "book music art"
            )

        if provider == "unsplash":
            return (
                "creative work copyright art"
            )

        if provider == "wikimedia":
            return (
                "copyright creative work India"
            )
        
    if category == "traditional_knowledge":

        if provider == "pexels":
            return (
                "Indian traditional crafts culture"
            )

        if provider == "unsplash":
            return (
                "Indian traditional crafts culture"
            )

        if provider == "wikimedia":
            return (
                "Indian traditional knowledge "
                "handicrafts culture"
            )

    if category == "invention":

        if provider == "pexels":
            return (
                "technology invention machine device"
            )

        if provider == "unsplash":
            return (
                "technology invention device"
            )

        if provider == "wikimedia":
            return (
                "technology invention machine India"
            )
        
    return cleaned

def get_query_variations(query: Any) -> List[str]:
    cleaned = clean_search_query(query)

    if not cleaned:
        return []

    normalized = normalize_text(cleaned)
    variations = [cleaned]

    for key, mapped_queries in IMAGE_QUERY_MAP.items():

        if normalize_text(key) == normalized:
            variations.extend(mapped_queries)

    if (
        "patent" in normalized
        and (
            "india" in normalized
            or "indian" in normalized
        )
    ):
        variations.extend(
            [
                "Indian patent",
                "Indian patent document",
                "Indian patent certificate",
                "Indian patent application",
                "Indian patent technical drawing",
                "Indian invention patent",
                "patent document India",
            ]
        )

    elif "patent" in normalized:
        variations.extend(
            [
                "patent document",
                "patent certificate",
                "patent technical drawing",
                "invention technical drawing",
            ]
        )

    if (
        "ayurvedic medicinal plants" in normalized
        or "ayurveda medicinal plants" in normalized
    ):
        variations.extend(
            [
                "amla medicinal plant India",
                "tulsi holy basil medicinal plant India",
                "neem medicinal plant India",
                "ashwagandha medicinal plant India",
                "turmeric plant India",
            ]
        )

    if (
        "gi tagged indian product" in normalized
        or "indian gi product" in normalized
    ):
        variations.extend(
            [
                "Indian handicraft GI product",
                "Indian traditional handicraft",
                "Indian GI handicraft",
                "Indian GI product",
            ]
        )

    if "trademark" in normalized:
        variations.extend(
            [
                "trademark logo",
                "Indian trademark",
                "brand trademark",
                "trademark registration",
            ]
        )

    if "copyright" in normalized:
        variations.extend(
            [
                "copyright document",
                "copyright creative work",
                "copyright certificate",
            ]
        )

    unique = []
    seen = set()

    for item in variations:
        normalized_item = normalize_text(item)

        if (
            normalized_item
            and normalized_item not in seen
        ):
            seen.add(normalized_item)
            unique.append(item)

    return unique

def search_pexels(
    query: Any,
    per_page: int = DEFAULT_PER_PROVIDER,
) -> List[Dict[str, Any]]:
    if not PEXELS_API_KEY:
        print("Pexels API key not configured.")
        return []

    provider_query = build_provider_query(
        query,
        "pexels",
    )

    if not provider_query:
        return []

    url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
    }
    params = {
        "query": provider_query,
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
        thumbnail_url = src.get("medium")

        if not image_url:
            continue

        results.append(
            {
                "url": image_url,
                "thumbnail": thumbnail_url,
                "title": (
                    photo.get("alt")
                    or provider_query
                ),
                "description": photo.get("alt"),
                "source": "pexels",
                "author": photo.get("photographer"),
                "source_url": photo.get("url"),
                "provider_id": photo.get("id"),
                "width": photo.get("width"),
                "height": photo.get("height"),
            }
        )

    return results

def search_unsplash(
    query: Any,
    per_page: int = DEFAULT_PER_PROVIDER,
) -> List[Dict[str, Any]]:

    if not UNSPLASH_ACCESS_KEY:
        print("Unsplash access key not configured.")
        return []

    provider_query = build_provider_query(
        query,
        "unsplash",
    )

    if not provider_query:
        return []

    url = "https://api.unsplash.com/search/photos"

    headers = {
        "Authorization": (
            f"Client-ID {UNSPLASH_ACCESS_KEY}"
        )
    }

    params = {
        "query": provider_query,
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
            or provider_query
        )

        image_url = (
            photo.get("urls", {})
            .get("regular")
        )

        thumbnail_url = (
            photo.get("urls", {})
            .get("small")
        )

        if not image_url:
            continue

        results.append(
            {
                "url": image_url,
                "thumbnail": thumbnail_url,
                "title": title,
                "description": (
                    photo.get("description")
                    or photo.get("alt_description")
                ),
                "source": "unsplash",
                "author": user.get("name"),
                "source_url": (
                    photo.get("links", {})
                    .get("html")
                ),
                "provider_id": photo.get("id"),
                "width": photo.get("width"),
                "height": photo.get("height"),
            }
        )

    return results

def search_wikimedia(
    query: Any,
    per_page: int = DEFAULT_PER_PROVIDER,
) -> List[Dict[str, Any]]:

    provider_query = build_provider_query(
        query,
        "wikimedia",
    )

    if not provider_query:
        return []

    url = "https://commons.wikimedia.org/w/api.php"

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": provider_query,
        "gsrnamespace": 6,
        "gsrlimit": per_page,
        "prop": "imageinfo",
        "iiprop": (
            "url|mime|size|extmetadata"
        ),
        "iiurlwidth": 1000,
        "format": "json",
    }

    headers = {
        "User-Agent": (
            "IP-SAKTI-Sahayak/1.0 "
            "(legal-research-project)"
        )
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
    pages = (
        data
        .get("query", {})
        .get("pages", {})
    )

    for page in pages.values():
        image_info = page.get(
            "imageinfo",
            [],
        )

        if not image_info:
            continue

        info = image_info[0]

        mime = str(
            info.get("mime", "")
        ).lower()

        if not mime.startswith("image/"):
            continue

        blocked_mimes = {
            "image/vnd.djvu",
            "image/tiff",
            "image/svg+xml",
        }

        if mime in blocked_mimes:
            continue

        image_url = info.get("url")

        thumbnail_url = (
            info.get("thumburl")
            or image_url
        )

        if not image_url:
            continue

        extmetadata = info.get(
            "extmetadata",
            {},
        )

        description = (
            extmetadata
            .get("ImageDescription", {})
            .get("value")
        )

        author = (
            extmetadata
            .get("Artist", {})
            .get("value")
        )

        license_name = (
            extmetadata
            .get("LicenseShortName", {})
            .get("value")
        )

        results.append(
            {
                "url": image_url,
                "thumbnail": thumbnail_url,
                "title": page.get(
                    "title",
                    "",
                ),
                "description": description,
                "source": "wikimedia",
                "author": author,
                "source_url": (
                    info.get("descriptionurl")
                ),
                "provider_id": page.get(
                    "pageid"
                ),
                "mime": mime,
                "width": info.get("width"),
                "height": info.get("height"),
                "license": license_name,
            }
        )

    return results

def search_provider(
    query: Any,
    provider: str,
    per_page: int = DEFAULT_PER_PROVIDER,
) -> List[Dict[str, Any]]:

    if provider == "pexels":
        return search_pexels(
            query,
            per_page,
        )

    if provider == "unsplash":
        return search_unsplash(
            query,
            per_page,
        )

    if provider == "wikimedia":
        return search_wikimedia(
            query,
            per_page,
        )

    return []

def search_provider_exact(
    provider_query: str,
    provider: str,
    per_page: int = DEFAULT_PER_PROVIDER,
) -> List[Dict[str, Any]]:
    if not provider_query:
        return []

    if provider == "pexels":
        if not PEXELS_API_KEY:
            return []

        url = "https://api.pexels.com/v1/search"
        headers = {
            "Authorization": PEXELS_API_KEY,
        }

        params = {
            "query": provider_query,
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
            thumbnail_url = src.get("medium")

            if not image_url:
                continue

            results.append(
                {
                    "url": image_url,
                    "thumbnail": thumbnail_url,
                    "title": (
                        photo.get("alt")
                        or provider_query
                    ),
                    "description": photo.get("alt"),
                    "source": "pexels",
                    "author": photo.get(
                        "photographer"
                    ),
                    "source_url": photo.get(
                        "url"
                    ),
                    "provider_id": photo.get(
                        "id"
                    ),
                    "width": photo.get(
                        "width"
                    ),
                    "height": photo.get(
                        "height"
                    ),
                }
            )

        return results

    if provider == "unsplash":
        if not UNSPLASH_ACCESS_KEY:
            return []

        url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": (
                f"Client-ID "
                f"{UNSPLASH_ACCESS_KEY}"
            )
        }

        params = {
            "query": provider_query,
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

            user = photo.get(
                "user",
                {},
            )

            image_url = (
                photo.get("urls", {})
                .get("regular")
            )

            thumbnail_url = (
                photo.get("urls", {})
                .get("small")
            )

            if not image_url:
                continue

            results.append(
                {
                    "url": image_url,
                    "thumbnail": thumbnail_url,
                    "title": (
                        photo.get(
                            "alt_description"
                        )
                        or photo.get(
                            "description"
                        )
                        or provider_query
                    ),
                    "description": (
                        photo.get(
                            "description"
                        )
                        or photo.get(
                            "alt_description"
                        )
                    ),
                    "source": "unsplash",
                    "author": user.get(
                        "name"
                    ),
                    "source_url": (
                        photo.get(
                            "links",
                            {},
                        ).get("html")
                    ),
                    "provider_id": photo.get(
                        "id"
                    ),
                    "width": photo.get(
                        "width"
                    ),
                    "height": photo.get(
                        "height"
                    ),
                }
            )

        return results

    if provider == "wikimedia":
        url = "https://commons.wikimedia.org/w/api.php"

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": provider_query,
            "gsrnamespace": 6,
            "gsrlimit": per_page,
            "prop": "imageinfo",
            "iiprop": (
                "url|mime|size|extmetadata"
            ),
            "iiurlwidth": 1000,
            "format": "json",
        }

        headers = {
            "User-Agent": (
                "IP-SAKTI-Sahayak/1.0 "
                "(legal-research-project)"
            )
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
        pages = (
            data
            .get("query", {})
            .get("pages", {})
        )

        for page in pages.values():
            image_info = page.get(
                "imageinfo",
                [],
            )

            if not image_info:
                continue

            info = image_info[0]
            mime = str(
                info.get("mime", "")
            ).lower()

            if not mime.startswith("image/"):
                continue

            blocked_mimes = {
                "image/vnd.djvu",
                "image/tiff",
                "image/svg+xml",
            }

            if mime in blocked_mimes:
                continue

            image_url = info.get("url")

            thumbnail_url = (
                info.get("thumburl")
                or image_url
            )

            if not image_url:
                continue

            extmetadata = info.get(
                "extmetadata",
                {},
            )

            description = (
                extmetadata
                .get(
                    "ImageDescription",
                    {},
                )
                .get("value")
            )

            author = (
                extmetadata
                .get(
                    "Artist",
                    {},
                )
                .get("value")
            )

            license_name = (
                extmetadata
                .get(
                    "LicenseShortName",
                    {},
                )
                .get("value")
            )

            results.append(
                {
                    "url": image_url,
                    "thumbnail": thumbnail_url,
                    "title": page.get(
                        "title",
                        "",
                    ),
                    "description": description,
                    "source": "wikimedia",
                    "author": author,
                    "source_url": (
                        info.get(
                            "descriptionurl"
                        )
                    ),
                    "provider_id": page.get(
                        "pageid"
                    ),
                    "mime": mime,
                    "width": info.get(
                        "width"
                    ),
                    "height": info.get(
                        "height"
                    ),
                    "license": license_name,
                }
            )

        return results

    return []


def remove_duplicates(
    results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    seen_urls = set()

    unique_results = []

    for result in results:

        url = result.get("url")

        if not url:
            continue

        normalized_url = (
            url.split("?")[0]
            .strip()
            .lower()
        )

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        unique_results.append(result)

    return unique_results


def contains_phrase(
    text: Any,
    phrase: Any,
) -> bool:

    text = normalize_text(text)
    phrase = normalize_text(phrase)

    if not phrase:
        return False

    return phrase in text

def score_image_quality(
    result: Dict[str, Any],
) -> int:
    width = result.get("width") or 0
    height = result.get("height") or 0

    if not width or not height:
        return 0

    area = width * height
    score = 0

    if width >= 2000 and height >= 1200:
        score += 10

    elif width >= 1600 and height >= 900:
        score += 8

    elif width >= 1200 and height >= 800:
        score += 6

    elif width >= 1000 and height >= 600:
        score += 4

    elif width >= 800 and height >= 500:
        score += 2

    if area >= 3_000_000:
        score += 4

    elif area >= 2_000_000:
        score += 3

    elif area >= 1_000_000:
        score += 2

    return score

def score_india_relevance(
    query: Any,
    result: Dict[str, Any],
) -> int:
    query_text = normalize_text(query)

    if not (
        "india" in query_text
        or "indian" in query_text
    ):
        return 0

    title = normalize_text(
        result.get("title", "")
    )

    description = normalize_text(
        result.get("description", "")
    )

    combined = (
        f"{title} {description}"
    ).strip()

    score = 0


    if "indian" in combined:
        score += 12

    if "india" in combined:
        score += 12

    if "indian patent" in combined:
        score += 10

    if "patent india" in combined:
        score += 10

    if "india patent" in combined:
        score += 8

    india_ip_terms = {
        "ip india": 10,
        "intellectual property india": 10,
        "indian patent office": 12,
        "patent office india": 12,
        "controller general of patents": 12,
        "cgdtm": 10,
    }

    for term, points in india_ip_terms.items():

        if term in combined:
            score += points

    wrong_country_terms = {
        "russian": -20,
        "russia": -20,
        "american": -18,
        "united states": -18,
        "usa": -18,
        "us patent": -18,
        "british": -18,
        "britain": -18,
        "uk patent": -18,
        "german": -18,
        "germany": -18,
        "french": -18,
        "france": -18,
        "canadian": -18,
        "canada": -18,
        "australian": -18,
        "australia": -18,
        "chinese": -18,
        "china": -18,
        "japanese": -18,
        "japan": -18,
        "italian": -18,
        "italy": -18,
        "spanish": -18,
        "spain": -18,
        "brazilian": -18,
        "brazil": -18,
    }

    for term, points in wrong_country_terms.items():

        if term in combined:
            score += points

    return score

def score_image_relevance(
    query: Any,
    result: Dict[str, Any],
) -> int:

    query_text = normalize_text(query)

    title = normalize_text(
        result.get("title", "")
    )

    description = normalize_text(
        result.get("description", "")
    )

    combined = (
        f"{title} {description}"
    ).strip()

    source = str(
        result.get(
            "source",
            "",
        )
    ).lower()

    score = 0

    query_words = {
        word
        for word in query_text.split()
        if len(word) >= 3
    }

    title_words = set(
        title.split()
    )

    description_words = set(
        description.split()
    )

    for word in query_words:
        if word in title_words:
            score += 4

        elif word in description_words:
            score += 2

        elif word in title:
            score += 1

    important_phrases = {
        "ayurvedic medicinal plants": 10,
        "ayurvedic medicine": 8,
        "medicinal plants": 8,
        "medicinal herbs": 8,
        "indian medicinal plants": 8,
        "indian handicrafts": 8,
        "gi tagged": 10,
        "gi tag": 10,
        "geographical indication": 10,
        "indian patent": 12,
        "patent document": 8,
        "patent certificate": 8,
        "patent application": 8,
        "trademark": 8,
        "copyright": 8,
        "traditional knowledge": 8,
    }

    for phrase, points in important_phrases.items():
        if (
            phrase in query_text
            and phrase in combined
        ):
            score += points

    if (
        "ayurveda" in query_text
        or "ayurvedic" in query_text
        or "medicinal plant" in query_text
        or "medicinal plants" in query_text
        or "medicinal herb" in query_text
        or "medicinal herbs" in query_text
    ):

        medicinal_terms = {
            "amla": 8,
            "phyllanthus": 8,
            "emblica": 7,
            "turmeric": 8,
            "curcuma": 8,
            "neem": 8,
            "azadirachta": 8,
            "tulsi": 8,
            "holy basil": 8,
            "ocimum": 8,
            "ashwagandha": 8,
            "withania": 8,
            "bhringraj": 8,
            "eclipta": 8,
            "ginger": 6,
            "cinnamon": 6,
            "aloe": 6,
            "aloe vera": 7,
            "brahmi": 7,
            "moringa": 6,
            "bael": 7,
            "bilva": 8,
            "aegle": 8,
        }

        for term, points in medicinal_terms.items():
            if (
                term in query_text
                and term in combined
            ):
                score += points

        visual_terms = {
            "plant": 4,
            "plants": 4,
            "herb": 4,
            "herbs": 4,
            "leaf": 3,
            "leaves": 3,
            "flower": 3,
            "flowers": 3,
            "fruit": 3,
            "root": 3,
            "spice": 3,
            "spices": 3,
        }

        for term, points in visual_terms.items():
            if (
                term in query_text
                and term in combined
            ):
                score += points

    if (
        "gi" in query_text
        or "geographical indication" in query_text
    ):

        gi_terms = {
            "handicraft": 8,
            "handicrafts": 8,
            "craft": 5,
            "artisan": 5,
            "traditional": 4,
            "product": 4,
            "textile": 4,
            "pottery": 4,
            "weaving": 4,
            "embroidery": 4,
            "food": 3,
        }

        for term, points in gi_terms.items():
            if term in combined:
                score += points

        if query_mentions_india(query_text):
            if (
                "india" in combined
                or "indian" in combined
            ):
                score += 7

    if "patent" in query_text:

        patent_terms = {
            "patent": 10,
            "patents": 10,
            "invention": 6,
            "document": 4,
            "certificate": 5,
            "drawing": 5,
            "technical": 4,
            "machine": 3,
            "device": 3,
            "engineering": 3,
            "blueprint": 4,
            "diagram": 4,
            "specification": 5,
            "prototype": 4,
            "application": 4,
            "intellectual property": 5,
        }

        for term, points in patent_terms.items():
            if term in combined:
                score += points

    if "trademark" in query_text:
        trademark_terms = {
            "trademark": 10,
            "logo": 7,
            "brand": 6,
            "identity": 4,
            "registration": 4,
            "certificate": 4,
        }

        for term, points in trademark_terms.items():
            if term in combined:
                score += points

    if "copyright" in query_text:
        copyright_terms = {
            "copyright": 10,
            "book": 4,
            "music": 4,
            "art": 4,
            "creative": 5,
            "author": 3,
            "writing": 3,
        }

        for term, points in copyright_terms.items():
            if term in combined:
                score += points

    score += score_india_relevance(
        query_text,
        result,
    )

    if source == "wikimedia":
        if (
            "patent" in query_text
            or "trademark" in query_text
            or "copyright" in query_text
            or "geographical indication"
            in query_text
        ):
            score += 3

    visual_keywords = {
        "document": 3,
        "certificate": 4,
        "logo": 4,
        "brand": 3,
        "product": 3,
        "machine": 3,
        "device": 3,
        "drawing": 4,
        "diagram": 4,
        "illustration": 3,
        "invention": 4,
        "handicraft": 5,
        "handicrafts": 5,
        "craft": 3,
        "food": 2,
        "plant": 3,
        "plants": 3,
        "herb": 3,
        "herbs": 3,
    }

    for keyword, points in visual_keywords.items():
        if (
            keyword in query_text
            and keyword in combined
        ):
            score += points

    negative_keywords = {
        "citizenship": -15,
        "graduation": -12,
        "graduate": -12,
        "diploma": -10,
        "degree": -10,
        "university": -9,
        "academic": -8,
        "school": -8,
        "student": -7,
        "air force": -10,
        "navy": -8,
        "military": -10,
        "journalism": -7,
        "football": -8,
        "cricket": -8,
        "wedding": -8,
        "vacation": -6,
        "travel": -5,
        "airport": -5,
    }

    for keyword, points in negative_keywords.items():
        if (
            keyword in combined
            and keyword not in query_text
        ):
            score += points

    generic_titles = {
        "image",
        "photo",
        "picture",
        "untitled",
        "printer paper",
    }

    if title in generic_titles:
        score -= 4

    width = result.get("width") or 0
    height = result.get("height") or 0

    if width and height:

        if width < 300 or height < 200:
            score -= 5

    return score

def is_bad_result(
    query: Any,
    result: Dict[str, Any],
) -> bool:

    title = normalize_text(
        result.get("title", "")
    )

    description = normalize_text(
        result.get("description", "")
    )

    combined = (
        f"{title} {description}"
    )

    query_text = normalize_text(query)
    bad_terms = [
        "citizenship",
        "graduation",
        "graduate",
        "diploma",
        "degree",
        "university",
        "academic",
        "school",
        "air force",
        "military",
        "journalism",
        "football",
        "cricket",
        "wedding",
    ]

    for term in bad_terms:
        if (
            term in combined
            and term not in query_text
        ):
            return True

    mime = str(
        result.get("mime", "")
    ).lower()

    blocked_mimes = {
        "application/pdf",
        "image/vnd.djvu",
        "image/tiff",
        "image/svg+xml",
    }

    if mime in blocked_mimes:
        return True

    if mime and not mime.startswith("image/"):
        return True
    
    width = result.get("width") or 0
    height = result.get("height") or 0

    if width and height:

        if width < 800 or height < 500:
            return True

        if (width * height) < 500_000:
            return True
        
    if query_mentions_india(query_text):

        wrong_country_terms = {
            "russian",
            "russia",
            "american",
            "united states",
            "usa",
            "us patent",
            "british",
            "britain",
            "uk patent",
            "german",
            "germany",
            "french",
            "france",
            "canadian",
            "canada",
            "australian",
            "australia",
            "chinese",
            "china",
            "japanese",
            "japan",
            "italian",
            "italy",
            "spanish",
            "spain",
            "brazilian",
            "brazil",
        }

        for country in wrong_country_terms:

            if country in combined:
                if (
                    "patent" in combined
                    or "certificate" in combined
                    or "document" in combined
                ):
                    return True

    return False

def passes_exact_relevance_gate(
    query: Any,
    result: Dict[str, Any],
) -> bool:
    query_text = normalize_text(query)

    title = normalize_text(
        result.get("title", "")
    )

    description = normalize_text(
        result.get("description", "")
    )

    combined = (
        f"{title} {description}"
    ).strip()

    category = detect_query_category(query)

    if not combined:
        return False
    
    if query_mentions_india(query_text):

        wrong_country_terms = {
            "russian",
            "russia",
            "american",
            "united states",
            "usa",
            "us patent",
            "british",
            "britain",
            "uk patent",
            "german",
            "germany",
            "french",
            "france",
            "canadian",
            "canada",
            "australian",
            "australia",
            "chinese",
            "china",
            "japanese",
            "japan",
            "italian",
            "italy",
            "spanish",
            "spain",
            "brazilian",
            "brazil",
        }

        for country in wrong_country_terms:

            if country in combined:
                if (
                    "patent" in combined
                    or "certificate" in combined
                    or "document" in combined
                    or "application" in combined
                ):
                    return False
                
    if category == "patent":

        if not any(
            term in combined
            for term in {
                "patent",
                "patents",
                "invention",
            }
        ):
            return False

        patent_visual_terms = {
            "document",
            "certificate",
            "drawing",
            "technical",
            "invention",
            "machine",
            "device",
            "engineering",
            "blueprint",
            "diagram",
            "specification",
            "prototype",
            "application",
            "intellectual property",
            "patent office",
        }

        if not any(
            term in combined
            for term in patent_visual_terms
        ):
            return False

        return True

    if category == "trademark":
        if not any(
            term in combined
            for term in {
                "trademark",
                "logo",
                "brand",
                "branding",
            }
        ):
            return False

        return True

    if category == "copyright":
        if not any(
            term in combined
            for term in {
                "copyright",
                "creative",
                "art",
                "music",
                "book",
                "writing",
                "author",
            }
        ):
            return False
        return True
    
    if category == "gi":
        if not any(
            term in combined
            for term in {
                "geographical indication",
                "gi",
                "handicraft",
                "handicrafts",
                "artisan",
                "traditional",
                "textile",
                "pottery",
                "weaving",
                "embroidery",
                "product",
            }
        ):
            return False
        return True

    if category == "ayurveda":
        if not any(
            term in combined
            for term in {
                "ayurveda",
                "ayurvedic",
                "medicinal",
                "medicine",
                "herb",
                "herbs",
                "plant",
                "plants",
                "herbal",
            }
        ):
            return False
        return True

    if category == "traditional_knowledge":
        if not any(
            term in combined
            for term in {
                "traditional",
                "knowledge",
                "culture",
                "craft",
                "handicraft",
                "medicine",
                "herbal",
            }
        ):
            return False
        return True

    if category == "invention":

        if not any(
            term in combined
            for term in {
                "invention",
                "technology",
                "machine",
                "device",
                "engineering",
                "prototype",
                "robot",
                "electronic",
            }
        ):
            return False
        return True
    return True

def minimum_score_for_query(
    query: Any,
) -> int:

    category = detect_query_category(query)
    if category == "ayurveda":
        return 3

    if category == "gi":
        return 3

    if category == "patent":
        return 3

    if category == "trademark":
        return 3

    if category == "copyright":
        return 3

    return 2

def search_images(
    query: Any,
    per_provider: int = DEFAULT_PER_PROVIDER,
) -> List[Dict[str, Any]]:
    query = str(query or "").strip()

    if not query:
        return []

    cleaned_query = clean_search_query(query)

    if not cleaned_query:
        return []

    query_variations = get_query_variations(
        cleaned_query
    )

    all_results = []
    for provider in PROVIDERS:
        provider_query = build_provider_query(
            cleaned_query,
            provider,
        )
        if not provider_query:
            continue

        try:
            results = search_provider(
                cleaned_query,
                provider,
                per_provider,
            )

            all_results.extend(results)

        except Exception as error:
            print(
                f"{provider.capitalize()} "
                f"search failed: {error}"
            )

    target_result_count = (
        per_provider
        * len(PROVIDERS)
        * 2
    )

    for variation in query_variations[1:]:
        if len(all_results) >= target_result_count:
            break
        for provider in PROVIDERS:
            if len(all_results) >= target_result_count:
                break
            try:
                results = search_provider_exact(
                    variation,
                    provider,
                    3,
                )

                all_results.extend(results)

            except Exception as error:

                print(
                    f"{provider.capitalize()} "
                    f"fallback search failed: "
                    f"{error}"
                )

    all_results = remove_duplicates(
        all_results
    )

    filtered_results = []
    for result in all_results:
        if is_bad_result(
            cleaned_query,
            result,
        ):
            continue

        if not passes_exact_relevance_gate(
            cleaned_query,
            result,
        ):
            continue

        filtered_results.append(
            result
        )

    for result in filtered_results:
        result["relevance_score"] = (
            score_image_relevance(
                cleaned_query,
                result,
            )
        )

        result["quality_score"] = (
            score_image_quality(
                result,
            )
        )

        result["india_relevance_score"] = (
            score_india_relevance(
                cleaned_query,
                result,
            )
        )

        result["final_score"] = (
            result["relevance_score"] * 2
            + result["quality_score"]
        )

    filtered_results.sort(
        key=lambda result: (
            result.get(
                "final_score",
                0,
            ),
            result.get(
                "india_relevance_score",
                0,
            ),
            result.get(
                "relevance_score",
                0,
            ),
            result.get(
                "quality_score",
                0,
            ),
        ),
        reverse=True,
    )

    minimum_score = (
        minimum_score_for_query(
            cleaned_query
        )
    )

    filtered_results = [
        result
        for result in filtered_results
        if result.get(
            "relevance_score",
            0,
        ) >= minimum_score
    ]

    return filtered_results

def get_provider_queries(
    query: Any,
) -> Dict[str, str]:

    return {
        "pexels": build_provider_query(
            query,
            "pexels",
        ),
        "unsplash": build_provider_query(
            query,
            "unsplash",
        ),
        "wikimedia": build_provider_query(
            query,
            "wikimedia",
        ),
    }


def get_images_for_response(
    query: Any,
    answer: Any = "",
    max_images: int = DEFAULT_MAX_IMAGES,
) -> Dict[str, Any]:
    query = str(query or "").strip()
    answer = str(answer or "").strip()
    if not query:
        return {
            "show_images": False,
            "search_query": "",
            "images": [],
        }
    
    image_decision = generate_image_query(query)
    if not image_decision["image_needed"]:
        return {
            "show_images": False,
            "search_query": "",
            "images": [],
        }

    focused_query = image_decision.get("query")

    if not focused_query:
        return {
            "show_images": False,
            "search_query": "",
            "images": [],
        }

    search_query = clean_search_query(
        focused_query
    )

    if not search_query:
        return {
            "show_images": False,
            "search_query": "",
            "images": [],
        }
    
    try:

        results = search_images(
            search_query,
            per_provider=DEFAULT_PER_PROVIDER,
        )

    except Exception as error:

        print(
            f"Image search failed: {error}"
        )

        return {
            "show_images": False,
            "search_query": search_query,
            "images": [],
        }
    results = results[:max_images]

    return {
        "show_images": bool(results),
        "search_query": search_query,
        "category": detect_query_category(
            search_query
        ),
        "provider_queries": (
            get_provider_queries(
                search_query
            )
        ),
        "images": results,
    }

if __name__ == "__main__":
    query = " ".join(
        sys.argv[1:]
    ).strip()

    if not query:
        print("Usage:")
        print(
            'python -m backend.image_router '
            '"Indian patent"'
        )
        sys.exit(1)

    print(
        f"\nSearching images for: {query}\n"
    )
    print("Category:")

    print(
        f"  {detect_query_category(query)}"
    )
    print(
        "\nProvider queries:"
    )

    provider_queries = (
        get_provider_queries(query)
    )

    for provider, provider_query in (
        provider_queries.items()
    ):

        print(
            f"  {provider}: "
            f"{provider_query}"
        )

    print(
        "\nQuery variations:"
    )

    variations = get_query_variations(
        query
    )

    for index, variation in enumerate(
        variations,
        start=1,
    ):

        print(
            f"  {index}. {variation}"
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
            f"{index}. "
            f"{result.get('source')}"
        )

        print(
            f"   Final score: "
            f"{result.get('final_score')}"
        )

        print(
            f"   Relevance score: "
            f"{result.get('relevance_score')}"
        )

        print(
            f"   India relevance: "
            f"{result.get('india_relevance_score')}"
        )

        print(
            f"   Quality score: "
            f"{result.get('quality_score')}"
        )

        print(
            f"   Title: "
            f"{result.get('title')}"
        )

        print(
            f"   Description: "
            f"{result.get('description')}"
        )

        print(
            f"   Author: "
            f"{result.get('author')}"
        )

        if result.get("license"):

            print(
                f"   License: "
                f"{result.get('license')}"
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