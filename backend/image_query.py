import re

VISUAL_TOPICS = {
    "ayurveda": [
        "ayurveda",
        "ayurvedic",
        "ayurvedic medicine",
        "ayurvedic medicinal plant",
        "ayurvedic medicinal plants",
        "medicinal plant",
        "medicinal plants",
        "medicinal herb",
        "medicinal herbs",
        "herbal medicine",
    ],

    "patent": [
        "patent",
        "patents",
        "invention",
        "patent application",
        "patent certificate",
        "patent office",
    ],

    "trademark": [
        "trademark",
        "trade mark",
        "logo",
        "brand",
        "brand name",
    ],

    "geographical_indication": [
        "geographical indication",
        "geographical indications",
        "gi tag",
        "gi tagged",
        "gi product",
        "gi products",
        "gi tagged product",
        "gi tagged products",
    ],

    "copyright": [
        "copyright",
        "creative work",
        "literary work",
        "artistic work",
        "copyright symbol",
    ],
}

def generate_image_query(question):

    if not question:
        return {
            "image_needed": False,
            "query": None,
            "topic": None,
        }

    text = question.lower().strip()

    if any(
        keyword in text
        for keyword in [
            "ayurveda",
            "ayurvedic",
            "medicinal plant",
            "medicinal plants",
            "medicinal herb",
            "medicinal herbs",
            "herbal medicine",
        ]
    ):
        return {
            "image_needed": True,
            "query": "Ayurvedic medicinal plants India",
            "topic": "ayurveda",
        }

    if any(
        keyword in text
        for keyword in [
            "gi product",
            "gi products",
            "gi tagged product",
            "gi tagged products",
            "examples of geographical indication",
            "examples of gi",
        ]
    ):
        return {
            "image_needed": True,
            "query": "Indian GI tagged products",
            "topic": "geographical_indication",
        }

    if any(
        keyword in text
        for keyword in [
            "geographical indication",
            "geographical indications",
            "gi tag",
            "gi tagged",
        ]
    ):
        return {
            "image_needed": True,
            "query": "Indian geographical indication products",
            "topic": "geographical_indication",
        }
    
    if any(
        keyword in text
        for keyword in [
            "trademark logo",
            "trade mark logo",
            "trademark examples",
            "trademark example",
        ]
    ):
        return {
            "image_needed": True,
            "query": "Indian trademark logo examples",
            "topic": "trademark",
        }
    
    if any(
        keyword in text
        for keyword in [
            "trademark",
            "trade mark",
        ]
    ):
        return {
            "image_needed": True,
            "query": "Indian trademark logo",
            "topic": "trademark",
        }

    if any(
        keyword in text
        for keyword in [
            "copyright symbol",
            "copyright creative work",
            "copyright example",
            "copyright examples",
        ]
    ):
        return {
            "image_needed": True,
            "query": "Indian copyright creative works",
            "topic": "copyright",
        }

    if any(
        keyword in text
        for keyword in [
            "patent certificate",
            "patent document",
            "patent application",
        ]
    ):
        return {
            "image_needed": True,
            "query": "Indian patent document",
            "topic": "patent",
        }

    if any(
        keyword in text
        for keyword in [
            "patent example",
            "patent examples",
            "patented invention",
            "patented inventions",
        ]
    ):
        return {
            "image_needed": True,
            "query": "patented inventions India",
            "topic": "patent",
        }

    if any(
        keyword in text
        for keyword in [
            "patent drawing",
            "patent drawings",
            "patent drawing look",
            "what does a patent drawing look like",
        ]
    ):
        return {
            "image_needed": True,
            "query": "patent drawings India",
            "topic": "patent",
        }

    procedural_patent_terms = [
        "compulsory licence",
        "compulsory license",
        "patent term",
        "patent duration",
        "patent expires",
        "patent expiry",
        "patent infringement",
        "patent rights",
        "patent eligibility",
        "patent requirements",
        "conditions for patent",
        "grant of patent",
        "revocation of patent",
        "opposition to patent",
    ]

    if "patent" in text and any(
        term in text
        for term in procedural_patent_terms
    ):
        return {
            "image_needed": False,
            "query": None,
            "topic": "patent",
        }
    
    if "patent" in text or "invention" in text:
        return {
            "image_needed": True,
            "query": "Indian patent document",
            "topic": "patent",
        }

    return {
        "image_needed": False,
        "query": None,
        "topic": None,
    }


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]).strip()

    if not question:
        print("Usage:")
        print(
            'python -m backend.image_query '
            '"What is a patent in India?"'
        )
        sys.exit(1)

    result = generate_image_query(question)

    print("\nImage Query Result")
    print("------------------")
    print(f"Image needed: {result['image_needed']}")
    print(f"Topic: {result['topic']}")
    print(f"Query: {result['query']}")