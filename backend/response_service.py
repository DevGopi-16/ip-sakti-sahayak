from typing import Any, Dict, List

def clean_image_result(
    image: Dict[str, Any],
) -> Dict[str, Any]:
 
    return {
        "provider": image.get("source", ""),
        "title": image.get("title", ""),
        "description": image.get("description", ""),
        "author": image.get("author", ""),
        "url": image.get("url", ""),
        "thumbnail": image.get("thumbnail", ""),
        "source_url": image.get("source_url", ""),
        "license": image.get("license", ""),
    }


def prepare_images(
    images: List[Dict[str, Any]] | None = None,
) -> List[Dict[str, Any]]:

    if not images:
        return []

    prepared = []

    for image in images:
        if not isinstance(image, dict):
            continue

        cleaned = clean_image_result(image)

        if cleaned.get("url"):
            prepared.append(cleaned)

    return prepared


def build_combined_response(
    answer: str,
    images: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:

    prepared_images = prepare_images(images)

    return {
        "answer": answer or "",
        "show_images": bool(prepared_images),
        "images": prepared_images,
    }


def create_response(
    answer: str,
    images: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    
    return build_combined_response(
        answer=answer,
        images=images,
    )


if __name__ == "__main__":

    test_answer = (
        "An Indian patent is a legal right "
        "granted under Indian patent law."
    )

    test_images = [
        {
            "source": "wikimedia",
            "title": "Example Patent Drawing",
            "description": "Example patent document",
            "author": "Example Author",
            "url": "https://example.com/image.png",
            "thumbnail": "https://example.com/thumb.png",
            "source_url": "https://example.com",
            "license": "CC BY-SA",
        }
    ]

    result = create_response(
        answer=test_answer,
        images=test_images,
    )

    print("\n=== Phase 11 Combined Response ===")
    print(result)