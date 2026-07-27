# App_Flow.md — StudyLink

This document maps the primary user journeys and execution lifecycles within StudyLink, detailing the interactions between the React frontend and the Django backend.

---

## 1. Authentication & Identity Lifecycle

This flow manages secure access and the intersection of local JWT accounts and third-party OAuth providers.

1.  **Entry:** User selects Login or Signup via email/password or Social Login (React).
2.  **JWT Path:** User submits credentials; Django validates and returns `access` and `refresh` tokens (Django).
3.  **OAuth Path:** User redirects to Google/GitHub; provider returns auth code; Django exchanges code for user profile (React → Provider → Django).
4.  **Identity Check:** Django checks if an account with that email already exists (Django).
5.  **Conflict Flag (Open Question):** If the email exists via a password-based account but the user is logging in via OAuth for the first time, the system flags a "Conflict State" instead of silently merging or duplicating the account (Django).
6.  **Session Establishment:** Tokens are stored in local storage/cookies; frontend updates `authStore` (React).
7.  **Termination:** User logs out; frontend clears tokens and calls backend to blacklist the refresh token (React → Django).

---

## 2. Resource Vault: Ingestion & Discovery

This flow handles the lifecycle of digital study materials from upload to community interaction.

1.  **Submission:** User uploads a PDF and fills in metadata (Subject, Course, Tags) (React).
2.  **Storage:** Django saves metadata to Postgres and streams the file to Supabase Storage (Django).
3.  **Background Processing:** Django triggers a background task to extract text and generate embeddings for the "Chat-with-notes" feature (Django).
4.  **Discovery:** User applies subject/course filters on the Vault dashboard (React).
5.  **Retrieval:** Django executes a filtered query and returns a paginated list of resources (Django).
6.  **Engagement:** User upvotes a resource or posts a question on the "Doubt Board" (React → Django).
7.  **Social Update:** Django updates the rating count or comment thread; state reflects instantly for the user (Django → React).

---

## 3. Chat-with-Notes Flow (Scoped RAG)

This flow details the AI-powered retrieval process restricted to a single document context.

1.  **Activation:** User opens a specific PDF in the Vault and clicks "Chat with Notes" (React).
2.  **Query Input:** User types a technical question about the specific document (React).
3.  **Vectorization:** Django calls Gemini `text-embedding-004` to convert the query into a 768-dim vector (Django).
4.  **Similarity Search:** Django performs a `pgvector` search against chunks filtered by the current `document_id` (Django).
5.  **Context Construction:** The top matching text chunks are retrieved and formatted into a prompt (Django).
6.  **Generation:** Gemini 1.5 Flash generates an answer strictly grounded in the provided chunks (Django).
7.  **Response:** Django returns the answer and the metadata (page numbers/text snippets) of the sources used (Django).
8.  **Render:** Chat UI displays the answer with "Source Excerpts" for verification (React).

---

## 4. Marketplace Listing & State Machine

This flow manages the lifecycle of physical items using a strict state-transition pattern.

1.  **Creation:** User lists an item (Title, Condition, Photo, Pickup Location) (React).
2.  **Initialization:** Django creates a `Listing` record with status `AVAILABLE` (Django).
3.  **Interest:** A browsing student clicks "Request Item" on a listing (React).
4.  **Request State:** Django creates a `ListingRequest` and notifies the owner (Django).
5.  **Review:** Owner views the listing in their dashboard and selects a recipient (React).
6.  **Commitment:** Owner clicks "Accept Request"; status transitions `AVAILABLE` → `REQUESTED` (React → Django).
7.  **Notification:** Requesters are notified; the chosen recipient sees the owner's contact info for handoff (Django → React).
8.  **Completion Path:** Owner confirms handoff; status transitions `REQUESTED` → `GIVEN AWAY` (React → Django).
9.  **Fallback Path:** If the handoff fails, the owner cancels the request; status reverts `REQUESTED` → `AVAILABLE`, and the item becomes searchable again (React → Django).

---

## 5. Owner Dashboard Flow

The consolidated view for a user to manage their contributions and active listings.

1.  **Access:** User navigates to the "My Listings" tab in the dashboard (React).
2.  **Data Fetch:** Django returns all listings owned by the user, nested with their associated pending requests (Django).
3.  **Visual Grouping:** React renders a list where each item shows its current state and a badge for "New Requests" (React).
4.  **Action: Manage Requests:** User expands a listing to see a list of interested students (React).
5.  **Action: Archive/Delete:** User can remove an `AVAILABLE` listing; Django performs a soft-delete (React → Django).
6.  **Sync:** dashboard state updates automatically after any state-machine transition (React).