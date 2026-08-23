# Learning Doc 04: Gemini API Integration & RAG Pipeline

> **Topic**: Retrieval-Augmented Generation (RAG), Embedding Models vs. Generation Models, Similarity Cutoffs, and Hallucination Prevention.

---

## 1. Problem / Concept

Large Language Models (LLMs) are trained on general web corpora, making them prone to **hallucination** when answering questions about course-specific PDFs, professor slide decks, or custom study notes. 

**Retrieval-Augmented Generation (RAG)** overcomes this limitation by anchoring the LLM's answers in retrieved facts:
1. Instead of asking the LLM to answer from internal memory, we retrieve the top relevant passages from the user's specific PDF.
2. We insert those passages into a **grounded system prompt**.
3. We instruct the LLM to answer *strictly* using the provided context and cite the exact page numbers.

---

## 2. How It Works Generally

A production RAG architecture requires two distinct AI models:
- **Embedding Model (`models/text-embedding-004`)**: Converts text strings into 768-dimensional mathematical vectors. Used during document ingestion (chunking) and query processing.
- **Generative Model (`models/gemini-1.5-flash`)**: Takes text prompts and generates natural language responses. Fast, cost-efficient, and optimized for long-context grounding.

---

## 3. How StudyLink Specifically Uses It

In `backend/rag/client.py`, `backend/rag/search.py`, and `backend/rag/prompt.py`:

1. **Document Ingestion (`vault/tasks.py`)**:
   PDF documents are parsed with `pypdf`, split into chunks (~1000 characters with 200-character overlap) preserving page numbers, and embedded via `GeminiClient.get_embedding(chunk_text)`.
2. **Query Processing (`RAGAnswerService.answer_query`)**:
   - Computes query embedding using `text-embedding-004`.
   - Executes vector similarity search (`VectorSearchService.similarity_search`) to retrieve top 5 matching `ResourceChunk` records.
3. **Similarity Cutoff Threshold (`< 0.65`)**:
   To prevent hallucinating answers when a query is completely irrelevant to the document, StudyLink computes top-chunk similarity ($\text{Similarity} = 1 - \text{Cosine Distance}$). If $\text{Similarity} < 0.65$, StudyLink immediately short-circuits with a friendly fallback:
   > *"I couldn't find any relevant information in this specific document to answer that."*
4. **Grounded Prompt Synthesis**:
   If similarity exceeds 0.65, matching excerpts are formatted into `GROUNDING_PROMPT_TEMPLATE` with page tags `[Page X]: content` and passed to `gemini-1.5-flash`. The API response returns the answer alongside a structured list of page citations.

---

## 4. Key Files & Code References

- [backend/rag/client.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/rag/client.py#L5-L53) — `GeminiClient` wrapper for `text-embedding-004` and `gemini-1.5-flash`.
- [backend/rag/search.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/rag/search.py#L52-L115) — `RAGAnswerService` implementing threshold cutoff and RAG execution.
- [backend/rag/prompt.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/rag/prompt.py#L1-L15) — Strict grounding prompt template enforcing page citations and anti-hallucination rules.

---

## 5. Interview Deep-Dive Takeaways

> [!IMPORTANT]
> **What to highlight in an interview:**
> 1. **Cutoff Threshold Engineering**:  
>    "A major failure mode in basic RAG systems is forced answering when top retrieved chunks have low semantic relevance. Implementing a hard similarity score cutoff ($< 0.65$) ensures our RAG engine gracefully declines to answer rather than hallucinating."
> 2. **Page-Aware Citation Tracking**:  
>    "By preserving `page_number` during text chunking and injecting page metadata into the grounding prompt, StudyLink empowers students to jump directly to the exact page in the PDF viewer."
