"""Provision a Vertex AI RAG Engine corpus (vector search) and ingest knowledge docs.

Run once:  uv run python scripts/provision_rag.py
Prints the RAG_CORPUS resource name to put in .env / Cloud Run env.
"""

from __future__ import annotations

import os
from pathlib import Path

import vertexai
from google.cloud import storage

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0795401430")
# RAG Engine is regional; use a well-supported region (not 'global').
RAG_LOCATION = os.getenv("RAG_LOCATION", "us-central1")
BUCKET = os.getenv("RAG_BUCKET", f"{PROJECT}-rag-knowledge")
CORPUS_DISPLAY_NAME = "agentic-data-platform-knowledge"

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"


def _import_rag():
    try:
        from vertexai import rag  # newer SDK
        return rag
    except Exception:  # noqa: BLE001
        from vertexai.preview import rag  # older SDK
        return rag


def upload_docs() -> list[str]:
    client = storage.Client(project=PROJECT)
    bucket = client.bucket(BUCKET)
    if not bucket.exists():
        bucket = client.create_bucket(BUCKET, location=RAG_LOCATION)
        print(f"Created bucket gs://{BUCKET}")
    uris = []
    for doc in KNOWLEDGE_DIR.glob("*.md"):
        blob = bucket.blob(f"knowledge/{doc.name}")
        blob.upload_from_filename(str(doc))
        uri = f"gs://{BUCKET}/knowledge/{doc.name}"
        uris.append(uri)
        print(f"Uploaded {uri}")
    return uris


def main() -> None:
    rag = _import_rag()
    vertexai.init(project=PROJECT, location=RAG_LOCATION)

    # Switch RAG Engine to Serverless (Basic) tier — Spanner mode is restricted for
    # new projects in us-central1 due to capacity limits.
    try:
        cfg_name = f"projects/{PROJECT}/locations/{RAG_LOCATION}/ragEngineConfig"
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg_name,
                rag_managed_db_config=rag.RagManagedDbConfig(tier=rag.Basic()),
            )
        )
        print("Set RAG Engine tier to Basic (serverless).")
    except Exception as exc:  # noqa: BLE001
        print(f"(warn) could not set engine tier, continuing: {exc}")

    uris = upload_docs()

    backend_config = rag.RagVectorDbConfig(
        rag_embedding_model_config=rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model="publishers/google/models/text-embedding-005"
            )
        )
    )
    corpus = rag.create_corpus(
        display_name=CORPUS_DISPLAY_NAME,
        backend_config=backend_config,
    )
    print(f"Created corpus: {corpus.name}")

    rag.import_files(
        corpus.name,
        uris,
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100),
        ),
        max_embedding_requests_per_min=900,
    )
    print("Imported knowledge docs into corpus.")
    print()
    print("=" * 60)
    print(f"RAG_CORPUS={corpus.name}")
    print("=" * 60)
    print("Add the line above to agentic-data-platform/.env and Cloud Run env.")


if __name__ == "__main__":
    main()
