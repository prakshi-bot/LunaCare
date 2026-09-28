"""
LunaCare: Health Document Ingestion Pipeline
-------------------------------------------
Demonstrates Week 4 Syllabus Concepts:
- Document Chunking: Why chunking is necessary for RAG:
  1. Precision: A query about 'menstrual cramps' needs the specific paragraph
     explaining dysmenorrhea, not a whole 140-page report.
  2. Context Windows: Smaller chunks fit neatly into LLM prompts alongside
     conversation history and safety instructions.
  3. Chunk Overlap: Keeping a 150-character overlap between consecutive chunks
     ensures thoughts and medical explanations aren't cut in half at borders.
- Embeddings & Vector Storage:
  Translates extracted text chunks into 3072-dimensional vectors and stores
  them alongside metadata in a persistent local Chroma database.
- Idempotency & Deterministic IDs:
  Generates stable chunk identifiers (topic_filename_page_chunkIndex) so the
  pipeline can be rerun safely without duplicating records.
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ensure terminal stdout handles Unicode cleanly on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pypdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from config import (
    KNOWLEDGE_BASE_DIR,
    VECTOR_STORE_DIR,
    CHROMA_COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
)
from services.embedding_service import get_embedding_service

# Configure ingestion logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lunacare.ingest")


def load_pdf_documents(knowledge_base_dir: Path) -> List[Document]:
    """
    Recursively scans knowledge_base_dir for supported PDF documents,
    extracts text page-by-page, and constructs LangChain Document objects.
    
    Metadata attached to each document:
    - source: filename of the PDF
    - topic: category name derived from the parent folder (e.g. 'menstrual_health')
    - page: 1-indexed page number
    """
    documents: List[Document] = []
    pdf_paths = sorted(knowledge_base_dir.rglob("*.pdf"))

    print(f"\n[1/4] Scanning knowledge base: {knowledge_base_dir}")
    print(f"      Found {len(pdf_paths)} PDF file(s) across topic directories.\n")

    for pdf_path in pdf_paths:
        topic_folder = pdf_path.parent.name
        filename = pdf_path.name

        print(f"      • Processing: [{topic_folder}] {filename}")

        try:
            reader = pypdf.PdfReader(str(pdf_path), strict=False)
            total_pages = len(reader.pages)
            pages_with_text = 0

            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                except Exception as extract_err:
                    logger.warning("Could not extract text from page %d of %s: %s", page_num, filename, extract_err)
                    text = ""

                if text and text.strip():
                    pages_with_text += 1
                    doc = Document(
                        page_content=text.strip(),
                        metadata={
                            "source": filename,
                            "topic": topic_folder,
                            "page": page_num,
                        },
                    )
                    documents.append(doc)

            print(f"        -> Successfully extracted text from {pages_with_text}/{total_pages} page(s).")

        except Exception as read_err:
            logger.error("Could not read PDF '%s': %s", filename, str(read_err))
            print(f"        ⚠️  Skipped corrupt or unreadable PDF: {filename} ({read_err})")

    return documents


def split_documents_into_chunks(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Document]:
    """
    Splits long document pages into smaller, semantically coherent chunks using
    RecursiveCharacterTextSplitter.
    
    Separators prioritized: paragraphs ('\\n\\n'), sentences ('\\n', '. '), and words (' ').
    """
    print(f"\n[2/4] Splitting documents into chunks...")
    print(f"      Settings: chunk_size={chunk_size} characters, chunk_overlap={chunk_overlap} characters")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
    )

    chunks: List[Document] = []
    for doc in documents:
        page_chunks = splitter.split_documents([doc])
        for chunk_idx, chunk in enumerate(page_chunks):
            # Attach chunk index and stable deterministic ID
            chunk.metadata["chunk_index"] = chunk_idx
            stable_id = f"{chunk.metadata['topic']}_{chunk.metadata['source']}_p{chunk.metadata['page']}_c{chunk_idx}"
            chunk.metadata["chunk_id"] = stable_id
            chunks.append(chunk)

    print(f"      -> Created {len(chunks)} total text chunks from {len(documents)} page documents.")
    return chunks


def ingest_to_chroma(
    chunks: List[Document],
    collection_name: str = CHROMA_COLLECTION_NAME,
    persist_dir: Path = VECTOR_STORE_DIR,
) -> int:
    """
    Generates embeddings and stores chunks in local persistent Chroma storage.
    
    Idempotent: Uses stable IDs so that re-running this script updates existing
    records rather than creating duplicate entries.
    """
    if not chunks:
        print("      ⚠️ No chunks available to ingest.")
        return 0

    print(f"\n[3/4] Connecting to Chroma vector store: {persist_dir}")
    print(f"      Collection: '{collection_name}' | Embedding model: '{EMBEDDING_MODEL}'")

    embedding_service = get_embedding_service()

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_service,
        persist_directory=str(persist_dir),
    )

    # Prepare IDs and documents
    chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]

    print(f"\n[4/4] Embedding & indexing {len(chunks)} chunks...")
    
    # Add documents in batches to show clear progress
    batch_size = 50
    total_added = 0

    for i in range(0, len(chunks), batch_size):
        sub_chunks = chunks[i : i + batch_size]
        sub_ids = chunk_ids[i : i + batch_size]
        
        # add_documents with explicit IDs performs idempotent upserts in Chroma
        vector_store.add_documents(documents=sub_chunks, ids=sub_ids)
        total_added += len(sub_chunks)
        print(f"      -> Indexed {total_added}/{len(chunks)} chunks...")

    return total_added


def run_ingestion():
    """Main ingestion coordinator function."""
    print("==================================================================")
    print(" LUNACARE: KNOWLEDGE BASE INGESTION PIPELINE (Week 4 RAG)")
    print("==================================================================")

    # 1. Load documents
    raw_docs = load_pdf_documents(KNOWLEDGE_BASE_DIR)
    if not raw_docs:
        print("\n❌ Ingestion stopped: No valid PDF pages could be read from data/knowledge_base/.")
        return

    # 2. Chunk documents
    chunks = split_documents_into_chunks(raw_docs, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    # 3. Embed and store
    total_stored = ingest_to_chroma(chunks)

    # 4. Final summary report
    print("\n==================================================================")
    print(" INGESTION COMPLETE — SUMMARY REPORT")
    print("==================================================================")
    print(f"  • Knowledge Base Path:       {KNOWLEDGE_BASE_DIR}")
    print(f"  • PDFs Found:                {len(list(KNOWLEDGE_BASE_DIR.rglob('*.pdf')))}")
    print(f"  • Pages Processed:           {len(raw_docs)}")
    print(f"  • Chunks Created:            {len(chunks)}")
    print(f"  • Vectors Stored:            {total_stored}")
    print(f"  • Embedding Model:           {EMBEDDING_MODEL}")
    print(f"  • Vector Dimensions:         3072")
    print(f"  • Chroma Collection:         {CHROMA_COLLECTION_NAME}")
    print(f"  • Persistence Directory:     {VECTOR_STORE_DIR}")
    print("==================================================================\n")


if __name__ == "__main__":
    run_ingestion()
