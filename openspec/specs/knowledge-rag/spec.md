## ADDED Requirements

### Requirement: Knowledge base supports semantic search

The system SHALL provide semantic search over company documents using vector embeddings, returning the most relevant document chunks for a given query.

#### Scenario: Search for driver late policy
- **WHEN** `search_knowledge("网约车司机迟到怎么处理")` is called
- **THEN** System returns top-K relevant document chunks ranked by semantic similarity, each containing: chunk_text, source_document, relevance_score

#### Scenario: Search returns empty for no relevant matches
- **WHEN** `search_knowledge("火星旅行退票政策")` is called with no related documents in the knowledge base
- **THEN** System returns an empty result set with `results: []`, allowing Agent to inform user that no relevant information was found

### Requirement: Knowledge base supports document ingestion

The system SHALL ingest documents from a designated directory, chunk them, generate embeddings, and store them in a vector database.

#### Scenario: Ingest a markdown policy document
- **WHEN** A markdown file is placed in the documents directory and ingestion is triggered
- **THEN** System chunks the document by sections, generates embeddings for each chunk, and stores them in the vector database with source metadata

#### Scenario: Ingestion supports incremental updates
- **WHEN** A previously ingested document is modified
- **THEN** System removes old embeddings for that document and re-ingests the updated version, without affecting other documents

### Requirement: Knowledge base is used as fallback when SOP has no match

The system SHALL be invoked by Agent when `search_sop` returns "no match", providing a secondary path for information retrieval.

#### Scenario: Agent falls back to knowledge search after SOP miss
- **WHEN** `search_sop(category="打车", issue_type="行李遗失")` returns no match
- **THEN** Agent SHALL call `search_knowledge("打车 行李遗失 处理")` to search the document corpus for relevant handling procedures

### Requirement: Vector database stores and retrieves embeddings locally

The system SHALL use Qdrant in local mode for vector storage and retrieval, requiring no external service dependencies.

#### Scenario: Start knowledge base service
- **WHEN** System starts
- **THEN** Qdrant is initialized in local mode with a configured storage path, ready for embedding storage and search

#### Scenario: Search after restart
- **WHEN** System restarts
- **THEN** Previously ingested documents are still searchable from the persisted local storage

#### Scenario: Zero external dependency
- **WHEN** Docker Compose starts only the backend service (without a separate vector DB container)
- **THEN** Qdrant runs in-process via `qdrant-client` in local mode, with data persisted to a local directory

### Requirement: Embedding generation uses configured embedding API

The system SHALL generate embeddings by calling a configurable embedding API (default: text-embedding-3-small).

#### Scenario: Generate embeddings for a document chunk
- **WHEN** A text chunk needs to be embedded
- **THEN** System calls the configured embedding API and stores the resulting vector in the vector database
