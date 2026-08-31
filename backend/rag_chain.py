import os
import re
import sys
import subprocess

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")

load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from backend.providers import get_embeddings, get_llm
except ImportError:
    from providers import get_embeddings, get_llm

from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

STATUTE_MAP = {
    "PA": "Patents Act, 1970",
    "TM": "Trademarks Act, 1999",
    "GI": "GI Act, 1999",
    "BD": "Biodiversity Act, 2002",
    "CR": "Copyright Act, 1957",
    "DS": "Designs Act, 2000",
    "DC": "Drugs And Cosmetics Act, 1940",
    "DR": "Drugs & Cosmetics Rules, 1945",
    "TMS": "Traditional Medicine Strategy 2014–2023",
}


STATUTE_MAPPING = {
    "PA": [
        "patent",
        "patents",
        "patents act",
        "patent act",
        "indian patents act",
        "indian patent act",
        "patents_act_1970",
        "the_patents_act",
    ],
    "TM": [
        "trademark",
        "trademarks",
        "trademark act",
        "trademarks act",
        "trade mark",
        "trade marks",
        "trade mark act",
        "trade marks act",
        "trademarks_act_1999",
    ],
    "GI": [
        "gi act",
        "geographical indications act",
        "geographical indication act",
        "geographical indications",
        "geographical indication",
        "gi_act_1999",
        "geographical_indications",
    ],
    "BD": [
        "biodiversity act",
        "biological diversity act",
        "biodiversity",
        "biological diversity",
        "biological_diversity_act_2002",
    ],
    "CR": [
        "copyright",
        "copyright act",
        "copyright_act_1957",
    ],
    "DS": [
        "design",
        "designs",
        "design act",
        "designs act",
        "designs_act_2000",
    ],
    "DC": [
        "drugs and cosmetics act",
        "drugs & cosmetics act",
        "drugs_and_cosmetics_act",
        "drugs_cosmetics",
    ],
    "DR": [
        "drugs and cosmetics rules",
        "drugs & cosmetics rules",
        "drugs_and_cosmetics_rules",
        "drugs_rules",
    ],
    "TMS": [
        "traditional medicine strategy",
        "traditional_medicine",
        "tms",
    ],
}


# ============================================================
# PROMPT
# ============================================================

PROMPT_TEMPLATE = """You are IP-SAKTI Sahayak, an AI Legal Assistant specializing in Indian Intellectual Property Laws and regulatory guidance concerning Ayurveda.

Previous Conversation:

{chat_history}

Statutory Context:

{context}

Question:

{question}

Instructions:

1. Answer using ONLY the provided Statutory Context.

2. Treat the selected statute as a strict boundary. Never use information from another statute.

3. Distinguish strictly between Section and Rule.

4. Distinguish strictly between:
- Rule 157
- Rule 157A
- Rule 157(1)
- Rule 157(1A)
- Rule 157(2)
- Section 157
- Section 157A
- Section 3(p)

5. A provision and a cross-reference to that provision are different.

6. A provision and a Schedule referring to that provision are different.

7. The requested provision type must match the evidence.

8. If a specific provision is requested, use only evidence belonging to that exact provision or sub-provision. For an extracted sub-rule, the sub-rule marker itself, such as (IA), (IB), or (IC), identifies the exact sub-rule when the surrounding context identifies the parent Rule.

9. For a request such as Section 3(p), do not treat the general heading "Section 3" as sufficient evidence. The actual text of subsection/clause (p) must be present.

10. For a request such as Rule 157(1A), Rule 157(1B), or Rule 157(1C), accept the corresponding sub-clause marker (IA), (IB), or (IC) as the exact sub-rule evidence when it appears in the Statutory Context under Rule 157. Do not require the full phrase "Rule 157(1A)" to be repeated inside the extracted text.

11. If the requested provision exists in the context, state the relevant text or requirements clearly.

12. If the requested provision or topic is completely absent from the provided context, respond with NO citation using exactly this sentence structure, replacing the placeholder with the actual provision name or topic from the Question (do not include square brackets in your output):

The provided statutory context does not contain the text or substantive requirements of <the actual provision or topic asked about>.

13. Do not infer missing legal requirements.

14. Citations must identify the exact evidence used.

15. Citation format must be exactly:

[Source: <statute/document>; <Section/Rule/sub-rule/Topic>; Chunk: <chunk_index>]

16. Keep answers concise and structured.

17. Do not output <think> tags or internal reasoning.

Answer:"""


PROMPT = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
def clean_reasoning_output(text: str) -> str:
    if not text:
        return ""

    text = str(text)

    text = re.sub(
        r"<think\b[^>]*>.*?</think\s*>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )


    text = re.sub(
        r"<think\b[^>]*>.*$",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"</?think\b[^>]*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^\s*(?:\*\*)?\s*assistant\s*:?\s*(?:\*\*)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    if "does not contain the text or substantive requirements" in text:
        text = re.sub(
            r"\[Source:.*?\]",
            "",
            text,
            flags=re.DOTALL,
        ).strip()

    return text.strip()

def is_toc_chunk(text: str) -> bool:
    if not text:
        return True

    upper_text = text.upper()

    toc_indicators = [
        "ARRANGEMENT OF SECTIONS",
        "ARRANGEMENT OF RULES",
        "TABLE OF CONTENTS",
        "STATEMENT OF OBJECTS AND REASONS",
    ]

    if any(indicator in upper_text for indicator in toc_indicators):
        return True

    if text.count("..........") > 2:
        return True

    return False


def normalize_reference(number: str) -> str:

    if not number:
        return ""

    value = str(number).upper().strip()

    value = re.sub(r"\s+", "", value)
    value = re.sub(
        r"\(\s*IA\s*\)",
        "(1A)",
        value,
        flags=re.IGNORECASE,
    )

    return value

def get_document_provision_type(doc) -> str | None:
    metadata = doc.metadata or {}

    evidence_type = str(
        metadata.get("evidence_type", "")
    ).lower().strip()

    if evidence_type in {
        "section",
        "rule",
        "sub-rule",
        "subrule",
    }:
        if evidence_type in {"sub-rule", "subrule"}:
            return "rule"

        return evidence_type

    document_name = str(
        metadata.get("document_name", "")
    ).lower()

    source_name = str(
        metadata.get("source", "")
    ).lower()

    combined_name = f"{document_name} {source_name}"

    if "rules" in combined_name:
        return "rule"

    if str(
        metadata.get("statute_code", "")
    ).upper() == "DR":
        return "rule"

    return "section"


def extract_legal_reference(question: str):
    if not question:
        return None

    q = question.lower()
    rule_match = re.search(
        r"\brule\s+(\d+[a-z]?)"
        r"(?:\s*\(\s*([a-z0-9]+)\s*\))?",
        q,
        re.IGNORECASE,
    )

    if rule_match:

        base = rule_match.group(1)
        sub = rule_match.group(2)

        number = base

        if sub:
            number = f"{base}({sub})"

        return {
            "type": "rule",
            "number": normalize_reference(number),
            "base_number": normalize_reference(base),
            "subclause": (
                normalize_reference(sub)
                if sub
                else None
            ),
        }

    section_match = re.search(
        r"\bsection\s+(\d+[a-z]?)"
        r"(?:\s*\(\s*([a-z0-9]+)\s*\))?",
        q,
        re.IGNORECASE,
    )

    if section_match:

        base = section_match.group(1)
        sub = section_match.group(2)

        number = base

        if sub:
            number = f"{base}({sub})"

        return {
            "type": "section",
            "number": normalize_reference(number),
            "base_number": normalize_reference(base),
            "subclause": (
                normalize_reference(sub)
                if sub
                else None
            ),
        }

    return None

def infer_statute_from_question(question: str):
    if not question:
        return None
    
    q = question.lower()
    ordered_patterns = [
        (
            "DR",
            [
                "drugs and cosmetics rules",
                "drugs & cosmetics rules",
            ],
        ),
        (
            "DC",
            [
                "drugs and cosmetics act",
                "drugs & cosmetics act",
            ],
        ),
        (
            "TMS",
            [
                "traditional medicine strategy",
            ],
        ),
        (
            "PA",
            [
                "indian patents act",
                "indian patent act",
                "patents act",
                "patent act",
            ],
        ),
        (
            "TM",
            [
                "trademarks act",
                "trademark act",
                "trade marks act",
                "trade mark act",
            ],
        ),
        (
            "GI",
            [
                "geographical indications act",
                "geographical indication act",
                "gi act",
            ],
        ),
        (
            "BD",
            [
                "biological diversity act",
                "biodiversity act",
            ],
        ),
        (
            "CR",
            [
                "copyright act",
            ],
        ),
        (
            "DS",
            [
                "designs act",
                "design act",
            ],
        ),
    ]

    for statute_code, patterns in ordered_patterns:
        for pattern in patterns:
            if pattern in q:
                return statute_code

    return None

def resolve_effective_statute(
    question: str,
    selected_statute: str,
):
    selected = str(
        selected_statute or "ALL"
    ).upper().strip()

    inferred = infer_statute_from_question(question)

    if inferred:
        return inferred

    if selected not in {
        "",
        "ALL",
        "NONE",
    }:
        return selected

    return "ALL"


def filter_docs_by_statute(
    docs,
    statute: str,
):
    if not statute:
        return list(docs)

    statute_key = str(
        statute
    ).upper().strip()

    if statute_key in {
        "ALL",
        "NONE",
        "",
    }:
        return list(docs)

    return [
        doc
        for doc in docs
        if str(
            (doc.metadata or {}).get(
                "statute_code",
                "",
            )
        ).upper().strip()
        == statute_key
    ]


def contains_section_heading(
    text: str,
    section_number: str,
) -> bool:
    if not text or not section_number:
        return False

    number = re.escape(
        normalize_reference(section_number)
    )

    pattern = rf"""
        (?im)
        ^
        \s*
        (?:
            section\s+{number}
            |
            sec\.?\s*{number}
            |
            {number}\s*[\.\-:]
        )
    """

    return bool(
        re.search(
            pattern,
            text,
            re.VERBOSE,
        )
    )


def contains_rule_heading(
    text: str,
    rule_number: str,
) -> bool:
    
    if not text or not rule_number:
        return False

    number = re.escape(
        normalize_reference(rule_number)
    )

    pattern = rf"""
        (?im)
        ^
        \s*
        (?:
            rule\s+{number}
            |
            {number}\s*[\.\-:]
        )
    """

    return bool(
        re.search(
            pattern,
            text,
            re.VERBOSE,
        )
    )


def contains_subclause(
    text: str,
    base_number: str,
    subclause: str,
) -> bool:

    if not text or not base_number or not subclause:
        return False

    normalized_sub = normalize_reference(subclause)

    sub_variants = {
        normalized_sub,
    }

    if normalized_sub.startswith("1") and len(normalized_sub) == 2:
        suffix = normalized_sub[1]

        if suffix.isalpha():
            sub_variants.add(
                "I" + suffix
            )


    base = re.escape(
        normalize_reference(base_number)
    )

    if not re.search(
        rf"\b{base}\b",
        text,
        re.IGNORECASE,
    ):
        return False

    for variant in sub_variants:
        sub = re.escape(variant)
        pattern = re.compile(
            rf"""
            \(
            \s*
            {sub}
            \s*
            \)
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        if pattern.search(text):
            return True

    return False

def text_contains_exact_provision(
    doc,
    ref: dict,
) -> bool:

    text = doc.page_content or ""

    if is_toc_chunk(text):
        return False

    target_type = ref["type"]
    base_number = ref["base_number"]
    subclause = ref.get("subclause")

    actual_type = get_document_provision_type(doc)

    if actual_type != target_type:
        return False

    metadata = doc.metadata or {}

    metadata_number = normalize_reference(
        metadata.get(
            "section_number",
            "",
        )
    )

    base_number_normalized = normalize_reference(
        base_number
    )

    if metadata_number != base_number_normalized:
        if target_type == "section":
            if not contains_section_heading(
                text,
                base_number,
            ):
                return False

        elif target_type == "rule":
            if not contains_rule_heading(
                text,
                base_number,
            ):
                return False

        else:
            return False

    if subclause:
        if not contains_subclause(
            text,
            base_number,
            subclause,
        ):
            return False

        if metadata_number == base_number_normalized:
            return True

        if target_type == "section":
            return contains_section_heading(
                text,
                base_number,
            )

        if target_type == "rule":
            return contains_rule_heading(
                text,
                base_number,
            )

        return False

    section_title = str(
        metadata.get(
            "section_title",
            "",
        )
    ).strip()


    if target_type == "rule":
        if contains_rule_heading(
            text,
            base_number,
        ):
            return True

    elif target_type == "section":

        if contains_section_heading(
            text,
            base_number,
        ):
            return True

    if section_title:
        title_lower = section_title.lower()
        if target_type == "rule":
            if title_lower == "dipivefrin hydrochloride":
                return False

        return True

    return False

def extract_exact_subclause(
    text: str,
    base_number: str,
    subclause: str,
) -> str | None:
    if not text or not base_number or not subclause:
        return None

    normalized_sub = normalize_reference(subclause)

    variants = {
        normalized_sub,
    }

    if (
        len(normalized_sub) == 2
        and normalized_sub.startswith("1")
        and normalized_sub[1].isalpha()
    ):
        variants.add(
            "I" + normalized_sub[1]
        )

    start_matches = []
    for variant in variants:
        pattern = re.compile(
            rf"""
            \(
                \s*
                {re.escape(variant)}
                \s*
            \)
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        start_matches.extend(
            pattern.finditer(text)
        )

    if not start_matches:
        return None

    start_match = max(
        start_matches,
        key=lambda match: match.start(),
    )

    start = start_match.start()
    sibling_pattern = re.compile(
        r"""
        \(
            \s*
            (?:
                \d+[A-Z]{1,4}
                |
                [A-Z]{1,4}
                |
                \d+
            )
            \s*
        \)
        """,
        re.VERBOSE,
    )

    end = len(text)

    for match in sibling_pattern.finditer(
        text,
        start_match.end(),
    ):

        if match.start() <= start:
            continue

        marker = re.sub(
            r"\s+",
            "",
            match.group(0),
        ).upper()

        requested_markers = {
            f"({v})".upper()
            for v in variants
        }

        if marker in requested_markers:
            continue


        end = match.start()
        break

    extracted = text[
        start:end
    ].strip()

    extracted = re.sub(
        r"\[Source Document:.*?\]",
        "",
        extracted,
        flags=re.IGNORECASE,
    )

    extracted = re.sub(
        r"\[Statute Code:.*?\]",
        "",
        extracted,
        flags=re.IGNORECASE,
    )

    extracted = re.sub(
        r"\[Provision:.*?\]",
        "",
        extracted,
        flags=re.IGNORECASE,
    )

    extracted = re.sub(
        r"\[Title:.*?\]",
        "",
        extracted,
        flags=re.IGNORECASE,
    )
    extracted = extracted.strip()

    extracted = re.sub(
        r"\n+\s*\d+\.\s*(?:Ins\.|Subs\.).*$",
        "",
        extracted,
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()

    if not extracted:
        return None

    return extracted

def build_subclause_document(
    doc,
    base_number: str,
    subclause: str,
):
    text = doc.page_content or ""
    if not text:
        return None

    normalized_sub = normalize_reference(
        subclause
    )
    variants = {
        normalized_sub,
    }
    if (
        len(normalized_sub) == 2
        and normalized_sub.startswith("1")
        and normalized_sub[1].isalpha()
    ):
        variants.add(
            "I" + normalized_sub[1]
        )


    start_match = None
    for variant in variants:
        pattern = re.compile(
            rf"""
            \(
                \s*
                {re.escape(variant)}
                \s*
            \)
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        match = pattern.search(text)

        if match:
            start_match = match
            break

    if not start_match:
        return None

    start = start_match.start()
    remaining_start = start_match.end()
    remaining = text[
        remaining_start:
    ]

    next_pattern = re.compile(
        r"""
        \(
            \s*
            (?:
                \d+[A-Z]{1,4}
                |
                \d+
                |
                [A-Z]{1,4}
            )
            \s*
        \)
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    next_match = next_pattern.search(
        remaining
    )

    if next_match:

        end = (
            remaining_start
            + next_match.start()
        )

    else:

        end = len(text)

    extracted = text[
        start:end
    ].strip()

    if not extracted:
        return None


    metadata = dict(
        doc.metadata or {}
    )

    metadata["requested_provision"] = (
        f"{base_number}({normalized_sub})"
    )

    metadata["is_exact_subclause"] = True

    metadata["provision_type"] = (
        metadata.get(
            "provision_type",
            "rule",
        )
    )

 

    return Document(
        page_content=extracted,
        metadata=metadata,
    )


def retrieve_exact_legal_reference(
    question: str,
    statute: str,
    all_docs,
):


    ref = extract_legal_reference(question)

    if not ref:
        return []

    statute_docs = filter_docs_by_statute(
        all_docs,
        statute,
    )

    if not statute_docs:
        return []

    target_type = ref.get("type", "")

    base_number = normalize_reference(
        ref.get("base_number", "")
    )

    subclause = ref.get("subclause")

    number = normalize_reference(
        ref.get("number", "")
    )



    if number == "3(P)":

        matches = []

        for doc in statute_docs:

            text = doc.page_content or ""

            if is_toc_chunk(text):
                continue

            if get_document_provision_type(doc) != target_type:
                continue

            if not contains_subclause(
                text,
                "3",
                "P",
            ):
                continue

            matches.append(doc)

        return deduplicate_docs(matches)

    if subclause:
        parent_candidates = []
        for doc in statute_docs:
            text = doc.page_content or ""

            if is_toc_chunk(text):
                continue

            if get_document_provision_type(doc) != target_type:
                continue

            metadata = doc.metadata or {}

            metadata_number = normalize_reference(
                metadata.get(
                    "section_number",
                    "",
                )
            )

            heading_match = False

            if target_type == "rule":

                heading_match = contains_rule_heading(
                    text,
                    base_number,
                )

            elif target_type == "section":

                heading_match = contains_section_heading(
                    text,
                    base_number,
                )

            metadata_match = (
                metadata_number == base_number
            )

            section_title = str(
                metadata.get(
                    "section_title",
                    "",
                )
            ).strip().lower()

            if (
                target_type == "rule"
                and base_number == "157"
                and section_title
                == "dipivefrin hydrochloride"
            ):
                metadata_match = False

            if heading_match or metadata_match:

                parent_candidates.append(doc)

        if not parent_candidates:
            return []

        def chunk_order(doc):

            metadata = doc.metadata or {}

            value = metadata.get(
                "chunk_index",
                0,
            )

            try:
                return int(value)
            except (
                TypeError,
                ValueError,
            ):
                return 0

        parent_candidates.sort(
            key=chunk_order
        )

        root_doc = None
        for doc in parent_candidates:
            text = doc.page_content or ""
            if target_type == "rule":

                if contains_rule_heading(
                    text,
                    base_number,
                ):
                    root_doc = doc
                    break

            elif target_type == "section":

                if contains_section_heading(
                    text,
                    base_number,
                ):
                    root_doc = doc
                    break

        if root_doc is None:
            root_doc = parent_candidates[0]

        root_chunk = chunk_order(root_doc)

        ordered_docs = []
        for doc in parent_candidates:
            current_chunk = chunk_order(doc)

            if current_chunk < root_chunk:
                continue
            if current_chunk > root_chunk + 2:
                continue

            text = doc.page_content or ""

            if not text.strip():
                continue

            ordered_docs.append(doc)


        filtered_docs = []
        for doc in ordered_docs:
            text = doc.page_content or ""
            normalized_text = re.sub(
                r"\s+",
                " ",
                text,
            ).strip()

            if re.search(
                r"(?i)"
                r"\b157\.\s*Dipivefrin hydrochloride\b",
                normalized_text,
            ):
                continue

            if re.match(
                r"^\s*1\.\s*Ins\.",
                normalized_text,
                re.IGNORECASE,
            ):
                continue

            filtered_docs.append(doc)

        ordered_docs = filtered_docs

        ordered_docs.sort(
            key=chunk_order
        )

        merged_parts = []
        for doc in ordered_docs:
            content = (
                doc.page_content or ""
            ).strip()

            if content:
                merged_parts.append(content)

        merged_text = "\n\n".join(
            merged_parts
        )

        if not merged_text:
            return []

        if not contains_subclause(
            merged_text,
            base_number,
            subclause,
        ):
            return []

        extracted = extract_exact_subclause(
            merged_text,
            base_number,
            subclause,
        )

        if not extracted:
            return []

        metadata = dict(
            root_doc.metadata or {}
        )

        normalized_sub = normalize_reference(
            subclause
        )

        metadata[
            "requested_provision"
        ] = (
            f"{base_number}"
            f"({normalized_sub})"
        )

        metadata[
            "is_exact_subclause"
        ] = True

        metadata[
            "provision_type"
        ] = target_type

        metadata[
            "source_chunks"
        ] = [
            str(
                chunk_order(doc)
            )
            for doc in ordered_docs
        ]

        metadata[
            "source_chunk_start"
        ] = str(root_chunk)

        return [
            Document(
                page_content=extracted,
                metadata=metadata,
            )
        ]


    exact_matches = []
    for doc in statute_docs:
        text = doc.page_content or ""
        if is_toc_chunk(text):
            continue

        if get_document_provision_type(doc) != target_type:
            continue

        metadata = doc.metadata or {}

        metadata_number = normalize_reference(
            metadata.get(
                "section_number",
                "",
            )
        )

        if metadata_number == base_number:
            section_title = str(
                metadata.get(
                    "section_title",
                    "",
                )
            ).strip().lower()

            if (
                target_type == "rule"
                and base_number == "157"
                and section_title
                == "dipivefrin hydrochloride"
            ):
                continue

            exact_matches.append(doc)

            continue

        if target_type == "rule":
            if contains_rule_heading(
                text,
                base_number,
            ):
                exact_matches.append(doc)

        elif target_type == "section":

            if contains_section_heading(
                text,
                base_number,
            ):
                exact_matches.append(doc)

    return deduplicate_docs(
        exact_matches
    )


def retrieve_full_section(
    section_number: str,
    statute: str,
    all_docs,
):
    if not section_number:
        return []

    statute_key = str(
        statute
    ).upper().strip()

    if statute_key in {
        "",
        "ALL",
        "NONE",
    }:
        return []

    target_section = normalize_reference(
        section_number
    )

    statute_docs = filter_docs_by_statute(
        all_docs,
        statute_key,
    )

    section_docs = []

    for doc in statute_docs:

        metadata = doc.metadata or {}

        doc_section = normalize_reference(
            str(
                metadata.get(
                    "section_number",
                    "",
                )
            )
        )

        if doc_section != target_section:
            continue

        text = doc.page_content or ""

        if is_toc_chunk(text):
            continue

        if target_section == "157":
            normalized_text = re.sub(
                r"\s+",
                " ",
                text,
            ).strip()

            if re.search(
                r"(?i)"
                r"\b157\.\s*Dipivefrin hydrochloride\b",
                normalized_text,
            ):
                continue

        section_docs.append(doc)



    def section_order(doc):
        metadata = doc.metadata or {}

        value = metadata.get(
            "section_chunk_index",
            0,
        )

        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0

    section_docs.sort(
        key=section_order
    )

    result = []
    seen_content = set()

    for doc in section_docs:

        content = (
            doc.page_content or ""
        ).strip()

        if content in seen_content:
            continue

        seen_content.add(content)
        result.append(doc)

    return result

def deduplicate_docs(docs):
    unique_docs = []
    seen = set()

    for doc in docs:

        metadata = doc.metadata or {}
        content = doc.page_content or ""

        key = (
            metadata.get(
                "source",
                "",
            ),
            metadata.get(
                "document_name",
                "",
            ),
            metadata.get(
                "statute_code",
                "",
            ),
            metadata.get(
                "section_number",
                "",
            ),
            metadata.get(
                "section_chunk_index",
                "",
            ),
            metadata.get(
                "chunk_index",
                "",
            ),
            content[:500],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_docs.append(doc)

    return unique_docs


def retrieve_statute_docs(
    question: str,
    statute: str,
    all_docs,
    vectorstore=None,
    limit: int = 15,
):
    effective_statute = resolve_effective_statute(
        question,
        statute,
    )

    ref = extract_legal_reference(
        question
    )

    if ref:

        exact_docs = retrieve_exact_legal_reference(
            question,
            effective_statute,
            all_docs,
        )

        if exact_docs:
            return deduplicate_docs(
                exact_docs
            )[:limit]

        return []

    statute_docs = filter_docs_by_statute(
        all_docs,
        effective_statute,
    )

    expanded_query = question
    if "ayurvedic" in question.lower():
        expanded_query = (
            "Ayurvedic Siddha Unani "
            "manufacture for sale "
            "licence form 25D "
            "licensing authority "
            "rule 153 154 155 "
            "schedule T"
        )


    vector_docs = []
    if vectorstore:
        try:
            vector_results = (
                vectorstore.similarity_search(
                    expanded_query,
                    k=limit,
                )
            )

            vector_docs = filter_docs_by_statute(
                vector_results,
                effective_statute,
            )

        except Exception:
            vector_docs = []

    bm25_docs = []
    if statute_docs:
        try:
            bm25 = BM25Retriever.from_documents(
                statute_docs
            )

            bm25.k = min(
                max(limit, 20),
                len(statute_docs),
            )

            bm25_docs = bm25.invoke(
                expanded_query
            )

        except Exception:
            bm25_docs = []

    combined = deduplicate_docs(
        vector_docs + bm25_docs
    )
    valid_docs = [
        doc
        for doc in combined
        if not is_toc_chunk(
            doc.page_content or ""
        )
    ]

    return valid_docs[:limit]

def find_provision_headings(text: str):
    if not text:
        return []

    headings = []

    pattern = re.compile(
        r"(?im)"
        r"^\s*"
        r"(?:"
        r"section\s+(\d+[A-Za-z]?)"
        r"|sec\.?\s*(\d+[A-Za-z]?)"
        r"|rule\s+(\d+[A-Za-z]?)"
        r"|(\d+[A-Za-z]?)\."
        r")"
    )

    for match in pattern.finditer(text):

        if match.group(1):
            headings.append(
                (
                    "section",
                    match.group(1).upper(),
                    match.start(),
                )
            )

        elif match.group(2):
            headings.append(
                (
                    "section",
                    match.group(2).upper(),
                    match.start(),
                )
            )

        elif match.group(3):
            headings.append(
                (
                    "rule",
                    match.group(3).upper(),
                    match.start(),
                )
            )

        elif match.group(4):
            headings.append(
                (
                    "unknown",
                    match.group(4).upper(),
                    match.start(),
                )
            )

    return headings



def get_provision_label(text: str):

    if not text:
        return None

    if re.search(
        r"\(\s*p\s*\)",
        text,
        re.IGNORECASE,
    ):
        if "traditional knowledge" in text.lower():
            return "3(P)"

    if re.search(
        r"\b157\s*\(\s*(?:1A|IA)\s*\)",
        text,
        re.IGNORECASE,
    ):
        return "157(1A)"

    headings = find_provision_headings(text)

    if not headings:
        return None

    heading_type, heading_number, _ = headings[0]

    if heading_type == "unknown":
        return heading_number

    pattern = re.compile(
        rf"(?im)"
        rf"^\s*{heading_type}\s+"
        rf"{re.escape(heading_number)}"
        rf"(?:\s*\(\s*([A-Za-z0-9]+)\s*\))?"
    )

    match = pattern.search(text)

    if match and match.group(1):

        subpart = match.group(1).upper()

        if subpart == "IA":
            subpart = "1A"

        return (
            f"{heading_number}"
            f"({subpart})"
        )

    return heading_number

def format_docs(docs):

    if not docs:
        return (
            "No relevant statutory context was found."
        )

    formatted_blocks = []

    for doc in docs:

        metadata = doc.metadata or {}

        content = (
            doc.page_content or ""
        )

        source_name = metadata.get(
            "document_name",
            metadata.get(
                "source",
                "Unknown Document",
            ),
        )

        statute_code = metadata.get(
            "statute_code",
            metadata.get(
                "statute",
                "",
            ),
        )

        chunk_index = metadata.get(
            "chunk_index",
            "",
        )

        section_number = metadata.get(
            "section_number",
            "",
        )

        provision_type = (
            get_document_provision_type(
                doc
            )
        )

        content_provision_label = get_provision_label(content)
        provision_label = (
            content_provision_label
            if content_provision_label
            else (
                str(section_number).upper()
                if section_number != ""
                else None
            )
        )

        header = (
            f"[Source Document: {source_name}]"
        )

        if statute_code:
            header += (
                f"\n[Statute Code: "
                f"{statute_code}]"
            )

        if provision_type:
            header += (
                f"\n[Evidence Type: "
                f"{provision_type}]"
            )

        if provision_label:
            header += (
                f"\n[Evidence Provision: "
                f"{provision_label}]"
            )

        if chunk_index != "":
            header += (
                f"\n[Chunk: "
                f"{chunk_index}]"
            )

        citation_parts = [
            source_name
        ]

        if provision_label:

            citation_parts.append(
                f"{provision_type.title()} "
                f"{provision_label}"
            )

        if chunk_index != "":

            citation_parts.append(
                f"Chunk: {chunk_index}"
            )

        citation_anchor = (
            "[Citation Anchor: "
            + "; ".join(citation_parts)
            + "]"
        )


        formatted_blocks.append(
            f"{header}\n"
            f"{citation_anchor}\n"
            f"{content}"
        )

    return "\n\n---\n\n".join(
        formatted_blocks
    )

def get_relevant_context(
    question: str,
    chat_history: str,
    statute: str,
    vectorstore,
    all_docs,
) -> str:

    statute_upper = (
        str(
            statute or "ALL"
        )
        .upper()
        .strip()
    )

    docs = retrieve_statute_docs(
        question,
        statute_upper,
        all_docs,
        vectorstore=vectorstore,
        limit=10,
    )

    return format_docs(docs)


def get_rag_chain():

    embeddings = get_embeddings()

    if not os.path.exists(
        INDEX_PATH
    ):
        raise FileNotFoundError(
            f"FAISS index missing at "
            f"'{INDEX_PATH}'. "
            f"Please execute build_index.py first."
        )

    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    all_docs = list(
        vectorstore.docstore._dict.values()
    )

    llm = get_llm()

    def debug_llm_output(
        response: str
    ) -> str:

        if os.environ.get(
            "DEBUG_RAG",
            "",
        ).lower() in {
            "true",
            "1",
        }:

            print(
                "RAW LLM OUTPUT "
            )

            print(
                repr(response)
            )

            print(  
                "END RAW OUTPUT "
            )

        return response
    
    chain = (
        {
            "context": RunnableLambda(
                lambda inputs:
                    get_relevant_context(
                        inputs.get(
                            "question",
                            "",
                        ),
                        inputs.get(
                            "chat_history",
                            "",
                        ),
                        inputs.get(
                            "statute",
                            "ALL",
                        ),
                        vectorstore,
                        all_docs,
                    )
            ),

            "question": RunnableLambda(
                lambda inputs:
                    inputs.get(
                        "question",
                        "",
                    )
            ),

            "chat_history": RunnableLambda(
                lambda inputs:
                    inputs.get(
                        "chat_history",
                        "None",
                    )
            ),
        }

        | PROMPT
        | llm
        | StrOutputParser()
        | RunnableLambda(
            debug_llm_output
        )
        | RunnableLambda(
            clean_reasoning_output
        )
    )

    return chain


def reload_rag_chain():

    build_script = os.path.join(
        BASE_DIR,
        "backend",
        "build_index.py",
    )

    if not os.path.exists(
        build_script
    ):
        build_script = os.path.join(
            CURRENT_DIR,
            "build_index.py",
        )

    result = subprocess.run(
        [
            sys.executable,
            build_script,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Index rebuild failed: "
            f"{result.stderr}"
        )

    return get_rag_chain()