# UIDesign.md — StudyLink Visual Design System

This document governs the visual identity and interface patterns for **StudyLink**. It defines how the digital **Resource Vault** and the physical **Giveaway Marketplace** maintain a cohesive product experience while signaling their distinct functional purposes.

---

## 1. Design Philosophy

StudyLink is a community-driven utility. It must feel more accessible than a professional IDE, yet more structured and trustworthy than a social media feed.

### Principles:
- **Contextual Duality:** The **Vault** should feel like a "Library" (organized, focused, quiet). The **Marketplace** should feel like a "Campus Square" (active, visual, local).
- **Academic Utility:** Minimize friction for students in high-stress periods (exam weeks). Information must be scannable.
- **Social Trust:** Use visual cues to validate users and resources (upvotes, condition tags, verified emails).
- **State Clarity:** Because items move through a strict lifecycle (Requested, Given Away), the user must always know exactly what "mode" an item is in without reading small text.

---

## 2. Visual Identity Options

Select one of the following palettes to define the product’s personality.

### Option A: The "Modern Ivy" (Classic Academic)
- **Vibe:** Established, trustworthy, high-contrast.
- **Palette:** 
    - `Primary:` Navy Blue (`#1e3a8a`)
    - `Accent:` Gold/Amber (`#fbbf24`)
    - `Surface:` Off-white/Cream (`#fefce8`)
- **Typography:** Serif headlines (Playfair Display) + Sans-serif body (Inter).
- **Rationale:** Mimics the feel of traditional university branding but with a modern, clean execution.

### Option B: The "Digital Campus" (Vibrant & Energetic)
- **Vibe:** Modern, tech-forward, social.
- **Palette:** 
    - `Primary:` Royal Purple (`#6366f1`)
    - `Accent:` Teal/Cyan (`#06b6d4`)
    - `Surface:` Clean White (`#ffffff`)
- **Typography:** Clean, geometric sans-serif (Geist or Satoshi) for all elements.
- **Rationale:** Feels like a modern productivity tool (similar to Notion or Slack). High energy for a peer-to-peer marketplace.

### Option C: The "Soft Studio" (Calm & Focused)
- **Vibe:** Low-stress, organic, approachable.
- **Palette:** 
    - `Primary:` Sage Green (`#15803d`)
    - `Accent:` Terracotta (`#c2410c`)
    - `Surface:` Warm Gray (`#f3f4f6`)
- **Typography:** Rounded sans-serif (Quicksand or Outfit).
- **Rationale:** Reduces eye strain during long study sessions. The green/terracotta pairing feels grounded and "local."

---

## 3. Key Screen Layouts

### 3.1 Resource Vault (The Library View)
- **Browse Screen:** A dense, searchable grid. Each card shows file type (PDF/Doc), Subject Tag, Upvote count, and "Chat Enabled" badge.
- **Sidebar:** Fixed persistent filters for Course Code, Semester, and Document Type.
- **Detail + Chat Panel:** 
    - **Left (70%):** PDF Viewer with annotation highlights.
    - **Right (30%):** Collapsible Chat interface.
    - **Chat UI:** Questions appear in user bubbles; AI answers appear in a distinct surface color with **"Source Excerpts"** rendered as small, clickable cards below the text that jump to the specific PDF page.

### 3.2 Giveaway Marketplace (The Classifieds View)
- **Browse Screen:** Image-heavy masonry or flex-grid. Emphasis on the photo and the "Pickup Location" badge.
- **Listing Creation:** Step-by-step form with a heavy focus on the "Condition" selector and "Photo Upload" preview.
- **Listing Detail:** Large hero image. Primary action button (e.g., "Request Item") is sticky at the bottom on mobile.

### 3.3 Owner Dashboard (The Management Hub)
- **Split-View:** 
    - **Top Section:** "Your Listings" carousel showing active items.
    - **Bottom Section:** "Pending Requests" list, grouped by listing. Each request shows the requester's name, their "reputation" (items given/taken), and an "Accept/Decline" button pair.

---

## 4. Component Patterns

### 4.1 Marketplace Status Badges
Status must be visible from the thumbnail view to prevent "click-fatigue."
- **`AVAILABLE`:** Outline border, Green text, "Open" icon.
- **`REQUESTED`:** Solid Amber background, White text. Signals "Pending Handoff."
- **`GIVEN AWAY`:** Desaturated Gray background, strike-through text on title. Removed from primary search after 24 hours.

### 4.2 Resource Upvotes
- A "pill" shaped component: `[ ▲ | 42 ]`. 
- Active state uses the Palette Accent color to show the user has already voted.

### 4.3 Notification Indicators
- **High Priority (Red dot):** New request on your listing; someone accepted your request.
- **Low Priority (Quiet toast):** New comment on a resource you follow; your resource was upvoted.

### 4.4 The "Doubt Board" Thread
- Nested comment structure localized to each resource. Uses a "Technical Support" visual style (monospace fonts for code snippets, clear "Solved" checkboxes for original posters).

---

## 5. Layout Density

- **Vault:** High density. Maximize information per square inch. Use 12px/14px text.
- **Marketplace:** Medium density. Focus on visual clarity and white space around images. Use 16px text for readability.
- **Mobile:** Single column for Marketplace; Tabbed view for Vault (PDF vs. Chat).