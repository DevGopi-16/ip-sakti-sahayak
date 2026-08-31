import os
import re
import sys

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")

STATUTE_MAP = {
    "PA": "patents_act_1970",
    "TM": "trademarks_act_1999",
    "GI": "gi_act_1999",
    "BD": "biological_diversity_act_2002",
    "CR": "copyright_act_1957",
    "DS": "designs_act_2000",
    "DC": "drugs_and_cosmetics_act_1940",
    "DR": "drugs_and_cosmetics_rules_1945",
    "TMS": "traditional_medicine_strategy_2014_2023",
}


def clean_legal_text(text: str) -> str:
    if not text:
        return ""

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            cleaned_lines.append("")
            continue

        if re.fullmatch(r"\d+", stripped):
            continue

        if re.fullmatch(
            r"Page\s*\d+(?:\s*of\s*\d+)?",
            stripped,
            re.IGNORECASE,
        ):
            continue

        if re.fullmatch(
            r"\d+\s+of\s+\d+",
            stripped,
            re.IGNORECASE,
        ):
            continue

        if re.fullmatch(
            r"\d+\s*\*\s*\d+",
            stripped,
        ):
            continue

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n[ \t]+", "\n", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    cleaned_text = re.sub(
        r"\[\s*(\d+)\s*\]",
        r"[\1]",
        cleaned_text,
    )

    cleaned_text = re.sub(
        r"\(\s*([a-zA-Z0-9]+)\s*\)",
        r"(\1)",
        cleaned_text,
    )

    cleaned_text = re.sub(
        r"(\d+)\s*\.\s*\*\s*",
        r"\1. ",
        cleaned_text,
    )

    return cleaned_text.strip()


def identify_statute(filename: str):
    normalized = re.sub(
        r"[^a-z0-9]+",
        "_",
        filename.lower(),
    ).strip("_")

    if (
        "traditional_medicine_strategy" in normalized
        or "medicine_strategy" in normalized
        or "traditional_medicine" in normalized
    ):
        return "TMS", "Traditional Medicine Strategy 2014–2023"

    if (
        "drugs_and_cosmetics_rules" in normalized
        or "drugs_cosmetics_rules" in normalized
        or "drugsandcosmeticsact1940rules1945" in normalized
        or (
            "drug" in normalized
            and "rule" in normalized
        )
    ):
        return "DR", "Drugs & Cosmetics Rules, 1945"

    if (
        "drugs_and_cosmetics_act" in normalized
        or "drug_and_cosmetics_act" in normalized
        or (
            "drug" in normalized
            and "cosmetic" in normalized
            and "act" in normalized
        )
    ):
        return "DC", "Drugs And Cosmetics Act, 1940"

    if "patent" in normalized:
        return "PA", "Patents Act, 1970"

    if (
        "trademark" in normalized
        or "trade_mark" in normalized
    ):
        return "TM", "Trademarks Act, 1999"

    if (
        "gi_act" in normalized
        or "geographical_indication" in normalized
        or "geographical_indications" in normalized
    ):
        return "GI", "GI Act, 1999"

    if (
        "biological_diversity" in normalized
        or "biodiversity" in normalized
    ):
        return "BD", "Biodiversity Act, 2002"

    if "copyright" in normalized:
        return "CR", "Copyright Act, 1957"

    if (
        "design" in normalized
        or "designs_act" in normalized
    ):
        return "DS", "Designs Act, 2000"

    return (
        "OTHER",
        os.path.splitext(filename)[0]
        .replace("_", " ")
        .title(),
    )


def is_footnote_section(line: str) -> bool:
    stripped = line.strip()

    if re.match(
        r"^\d+\.\s+(Ins\.|Subs\.|Sub-clause|The words|The bracket|Clause|Omitted)",
        stripped,
        re.IGNORECASE,
    ):
        return True

    if re.match(
        r"^\d+\.\s+.*\bAct\s+\d+\s+of\s+\d+",
        stripped,
        re.IGNORECASE,
    ):
        return True

    if re.match(
        r"^\d+\.\s+.*\(w\.e\.f\.",
        stripped,
        re.IGNORECASE,
    ):
        return True

    return False


def extract_sections(text: str):
    lines = text.splitlines()

    section_pattern = re.compile(
        r"^\s*(?:(Rule|Section|Sec\.)\s+)?"
        r"(\d{1,3}[A-Za-z]?(?:\([A-Za-z0-9]+\))?)"
        r"\s*[\.\-:]\s+(.+?)\s*$",
        re.IGNORECASE,
    )

    sections = []
    current_section = None
    current_lines = []
    prefix_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if current_section is not None:
                current_lines.append("")
            elif prefix_lines:
                prefix_lines.append("")
            continue

        match = section_pattern.match(stripped)

        if match and not is_footnote_section(stripped):
            prefix = (
                match.group(1) or ""
            ).strip().lower()

            number = match.group(2).upper()
            title = match.group(3).strip()
            
            if current_section is not None:
                current_section["text"] = "\n".join(
                    current_lines
                ).strip()

                sections.append(current_section)

            if prefix == "rule":
                provision_type = "rule"
            elif prefix in {"section", "sec."}:
                provision_type = "section"
            else:
                provision_type = "unknown"

            current_section = {
                "section_number": number,
                "section_title": title,
                "provision_type": provision_type,
                "text": "",
            }

            current_lines = [stripped]

        else:
            if current_section is not None:
                current_lines.append(line)
            else:
                prefix_lines.append(line)

    if current_section is not None:
        current_section["text"] = "\n".join(
            current_lines
        ).strip()

        sections.append(current_section)

    prefix = "\n".join(prefix_lines).strip()

    if prefix:
        sections.insert(
            0,
            {
                "section_number": None,
                "section_title": None,
                "provision_type": "unknown",
                "text": prefix,
            },
        )

    if not sections:
        return [
            {
                "section_number": None,
                "section_title": None,
                "provision_type": "unknown",
                "text": text.strip(),
            }
        ]

    return sections


def split_section(section, splitter):
    text = section["text"]

    if len(text) <= splitter._chunk_size:
        return [text]

    return splitter.split_text(text)


def load_and_chunk_docs():
    all_chunks = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=250,
        separators=[
            "\n\n",
            "\n",
            " ",
            "",
        ],
    )

    if not os.path.exists(DATA_DIR):
        print(
            f"Data directory not found at: {DATA_DIR}"
        )
        return []

    pdf_files = sorted(
        f
        for f in os.listdir(DATA_DIR)
        if f.lower().endswith(".pdf")
    )

    if not pdf_files:
        print(
            f"No PDF files found in {DATA_DIR}"
        )
        return []

    for file in pdf_files:
        file_path = os.path.join(DATA_DIR, file)

        print(
            f"Loading legal act: {file}..."
        )

        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()

            raw_full_text = "\n".join(
                doc.page_content
                for doc in docs
            )

            processed_text = clean_legal_text(
                raw_full_text
            )

            statute_code, statute_name = identify_statute(
                file
            )

            if not processed_text.strip():
                print(
                    f"Skipping empty document: {file}"
                )
                continue

            sections = extract_sections(
                processed_text
            )

            document_chunk_index = 0

            for section in sections:
                section_number = section[
                    "section_number"
                ]

                section_title = section[
                    "section_title"
                ]

                section_chunks = split_section(
                    section,
                    text_splitter,
                )

                for local_index, section_chunk in enumerate(
                    section_chunks
                ):
                    content = (
                        f"[Source Document: {statute_name}]\n"
                        f"[Statute Code: {statute_code}]\n"
                    )

                    if section_number:
                        content += (
                            f"[Provision: {section_number}]\n"
                        )

                    if section_title:
                        content += (
                            f"[Title: {section_title}]\n"
                        )

                    content += section_chunk.strip()

                    chunk = Document(
                        page_content=content,
                        metadata={
                            "source": file,
                            "document_name": statute_name,
                            "statute": statute_code,
                            "statute_code": statute_code,
                            "section_number": section_number,
                            "section_title": section_title,
                            "provision_type": section.get(
                                "provision_type",
                                "unknown",
                            ),
                            "section_chunk_index": local_index,
                            "chunk_index": document_chunk_index,
                        },
                    )

                    all_chunks.append(chunk)

                    document_chunk_index += 1

            print(
                f"  → {statute_code} | "
                f"{statute_name} | "
                f"{document_chunk_index} chunks"
            )

        except Exception as e:
            print(
                f"Error processing {file}: {e}"
            )

    print(
        f"Total Chunks Processed: "
        f"{len(all_chunks)}"
    )

    return all_chunks


if __name__ == "__main__":
    load_and_chunk_docs()