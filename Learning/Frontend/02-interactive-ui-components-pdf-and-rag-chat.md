# Learning Doc 09: Interactive UI Components: PDF Viewer & RAG Q&A Sidebar

> **Topic**: Client-Side PDF Rendering (`react-pdf`), Page-Jump Citation Cross-Linking, Side-by-Side Split Workspace, and Interactive Discussion Trees.

---

## 1. Problem / Concept

Traditional academic resource hubs force users to download PDFs locally and open them in separate applications. This breaks user workflow and makes AI assistance cumbersome:
- Users must manually search the PDF to verify answers returned by AI.
- Discussion board comments are disconnected from the actual document page being referenced.

To deliver a **seamless document workspace**, the frontend must render PDFs in-browser and link AI answer citations directly to document page navigation in real time.

---

## 2. How It Works Generally

- **Canvas-Based PDF Rendering**: Using `react-pdf` (powered by Mozilla's `pdf.js`), PDFs are rendered directly into HTML5 `<canvas>` elements, enabling programmatic zoom, page turning, and text layer selection.
- **Cross-Component State Binding**: A parent layout container manages active `pageNumber` state. When the AI sidebar returns page citations (e.g. `[Page 4]`), clicking a citation badge updates the shared `pageNumber`, causing the PDF viewer to smoothly transition to page 4.

---

## 3. How StudyLink Specifically Uses It

In `frontend/src/components/` and `frontend/src/pages/ResourceDetail.jsx`:

1. **Split-Screen Workspace Layout (`ResourceDetail.jsx`)**:
   Organizes the viewport into a flexible 2-column layout:
   - Left Column (70% width): `PdfViewer.jsx` displaying the course PDF.
   - Right Column (30% width): Tabbed panel containing `RagChatPanel.jsx` and `DoubtBoard.jsx`.
2. **Interactive PDF Viewer (`PdfViewer.jsx`)**:
   Accepts `pageNumber` and `onPageChange` props. Displays total page count, zoom controls, and previous/next page buttons.
3. **RAG Q&A Sidebar (`RagChatPanel.jsx`)**:
   Submits questions to `/api/v1/rag/chat/`. Renders AI responses with interactive citation badges:
   ```jsx
   {sources.map(src => (
     <button 
       key={src.page_number}
       onClick={() => onSelectPage(src.page_number)}
       className="px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200"
     >
       Page {src.page_number} ({Math.round(src.similarity_score * 100)}% match)
     </button>
   ))}
   ```
4. **Interactive Doubt Board (`DoubtBoard.jsx`)**:
   Renders hierarchical comment threads for the current resource, allowing students to ask questions, post code/math solutions, and mark answers as solved.

---

## 4. Key Files & Code References

- [frontend/src/components/PdfViewer.jsx](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/components/PdfViewer.jsx#L1-L100) — Client-side PDF canvas renderer and page controls.
- [frontend/src/components/RagChatPanel.jsx](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/components/RagChatPanel.jsx#L1-L180) — RAG chat UI with page citation click handlers.
- [frontend/src/components/DoubtBoard.jsx](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/components/DoubtBoard.jsx#L1-L200) — Threaded discussion comment component.
- [frontend/src/pages/ResourceDetail.jsx](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/src/pages/ResourceDetail.jsx#L1-L150) — Parent coordinator component linking PDF state with RAG citations.

---

## 5. Interview Deep-Dive Takeaways

> [!TIP]
> **What to highlight in an interview:**
> 1. **Cross-Component Event Interoperability**:  
>    "By lifting `pageNumber` state up to the `ResourceDetail` page container, we created a seamless feedback loop: clicking a page badge inside an AI response immediately jumps the PDF viewer to that exact page."
> 2. **Client-Side Heavy PDF Rendering Efficiency**:  
>    "Using `react-pdf` offloads document rendering entirely to the browser canvas, keeping server workload limited to semantic vector retrieval and AI synthesis."
