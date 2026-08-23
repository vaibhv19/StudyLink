# Learning Doc 03: pgvector Embeddings & SQLite Compatibility Fallback

> **Topic**: Vector Embeddings, Cosine Distance Similarity, PostgreSQL `pgvector`, HNSW Indexing, and Dual-Database Compatibility Layers.

---

## 1. Problem / Concept

Traditional relational databases excel at exact equality and keyword searches (`WHERE title LIKE '%calculus%'`). However, academic study materials require **semantic search**:
- A query for *"rate of change in curves"* should match a textbook page discussing *"differential calculus derivatives"*, even if exact keywords do not overlap.

Vector embeddings solve this by converting text into high-dimensional numerical vectors (e.g. 768 floating-point numbers). In vector space, semantically similar concepts lie close together, allowing similarity retrieval via **Cosine Distance**:

$$\text{Cosine Distance} = 1 - \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$

---

## 2. How It Works Generally

Historically, implementing vector search required running a separate, specialized vector database (e.g. Pinecone, Weaviate, Milvus). `pgvector` is an open-source PostgreSQL extension that adds native vector data types and vector search operators directly inside PostgreSQL:
- **Cosine Distance Operator (`<=>`)**: Performs distance queries directly in SQL.
- **HNSW Indexing (Hierarchical Navigable Small World)**: Creates a multi-layer graph index (`vector_cosine_ops`) for approximate nearest neighbor (ANN) retrieval in sub-linear time.

Using `pgvector` keeps all application data (users, resources, embeddings) inside PostgreSQL, eliminating multi-database sync complexity and infrastructure overhead.

---

## 3. How StudyLink Specifically Uses It

In `backend/vault/models.py` and `backend/rag/search.py`:

- **Production (PostgreSQL + pgvector)**:
  `ResourceChunk` uses `pgvector.django.VectorField(dimensions=768)` and `HnswIndex` with `vector_cosine_ops`.
  `VectorSearchService` executes:
  ```python
  from pgvector.django import CosineDistance
  ResourceChunk.objects.filter(resource_id=resource_id)\
      .annotate(distance=CosineDistance('embedding', query_embedding))\
      .order_by('distance')[:5]
  ```

- **Local Development / Testing Fallback (`CompatibleVectorField`)**:
  To allow full unit testing and lightweight local development without requiring a live PostgreSQL + `pgvector` container, StudyLink implements a custom `CompatibleVectorField` and `CompatibleHnswIndex`:
  - When `connection.vendor == 'sqlite'`, `CompatibleVectorField` transparently serializes vectors to JSON `TEXT` in SQLite.
  - `VectorSearchService.similarity_search()` automatically detects SQLite and falls back to an in-memory Python cosine distance computation.

---

## 4. Key Files & Code References

- [backend/vault/models.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/models.py#L83-L166) — `CompatibleVectorField`, `CompatibleHnswIndex`, and `ResourceChunk` model.
- [backend/rag/search.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/rag/search.py#L13-L50) — `VectorSearchService` with PostgreSQL `pgvector` query and SQLite fallback logic.

---

## 5. Interview Deep-Dive Takeaways

> [!TIP]
> **What to highlight in an interview:**
> 1. **Why `pgvector` over a dedicated Vector DB?**  
>    "For our v1 scale, `pgvector` allows us to keep transactional metadata and vector embeddings co-located in Supabase PostgreSQL. This eliminates distributed transaction issues, lowers infrastructure cost, and simplifies backup/restore operations."
> 2. **Dual-Database Design Pattern**:  
>    "Our `CompatibleVectorField` abstraction demonstrates clean system design: production benefits from PostgreSQL HNSW-indexed vector search, while developers can run fast, zero-dependency unit tests locally on SQLite."
