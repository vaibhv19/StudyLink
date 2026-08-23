# Learning Doc 02: Listing State Machine & Concurrency Handling

> **Topic**: Explicit State Machines, Pessimistic Row Locking (`SELECT FOR UPDATE`), and Transactional Integrity in Peer-to-Peer Marketplaces.

---

## 1. Problem / Concept

In peer-to-peer sharing platforms, physical items (textbooks, lab kits, study notes) exist in finite quantity—typically 1 unit. When multiple users attempt to request or claim the same item simultaneously, a naive system risks **concurrency race conditions** ("double-claiming"):
- User A and User B both request an available textbook.
- The item owner clicks "Accept" on User A's request and User B's request within milliseconds of each other.
- Without proper state control and row locking, both requests get marked as `ACCEPTED`, creating duplicate handoff promises and database inconsistency.

---

## 2. How It Works Generally

To guarantee correctness under concurrent load:
1. **Explicit State Machine**: States are defined with strict allowed transitions:
   - `AVAILABLE` → `REQUESTED` (when owner accepts a request)
   - `REQUESTED` → `AVAILABLE` (if accepted request is canceled/withdrawn)
   - `REQUESTED` → `GIVEN_AWAY` (when handoff is completed)
2. **Pessimistic Locking (`SELECT FOR UPDATE`)**: When a state-changing operation begins, the database acquires an exclusive row lock on the target listing record. Any concurrent HTTP requests attempting to modify the same listing must wait until the active transaction commits or rolls back.

---

## 3. How StudyLink Specifically Uses It

In `backend/market/services.py`:

- **Row Locking (`accept_request`)**:
  ```python
  with transaction.atomic():
      listing = Listing.objects.select_for_update().get(id=request_obj.listing_id)
      if listing.status != 'AVAILABLE':
          raise ConflictError("This listing is already requested or given away.")
      
      listing.status = 'REQUESTED'
      listing.save(update_fields=['status'])
  ```
- **Automatic Auto-Rejection**: When the owner accepts request $R_1$, StudyLink queries all other pending requests for that listing ($R_2, R_3, \dots$) and bulk updates their status to `REJECTED` in the same atomic block.
- **Audit Log (`ListingStatusHistory`)**: Every status mutation creates an immutable history record storing `from_status`, `to_status`, `changed_by`, `reason`, and timestamp.

---

## 4. Key Files & Code References

- [backend/market/models.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/models.py#L7-L62) — `Listing` model, `STATUS_CHOICES`, and `ListingStatusHistory`.
- [backend/market/services.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/services.py#L13-L81) — `accept_request()` implementing pessimistic locking and state transitions.
- [backend/market/services.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/services.py#L83-L152) — `cancel_request()` handling state reversion.
- [backend/market/services.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/services.py#L154-L197) — `complete_handoff()` handling terminal state transitions.

---

## 5. Interview Deep-Dive Takeaways

> [!IMPORTANT]
> **What to highlight in an interview:**
> 1. **Pessimistic vs. Optimistic Locking Choice**:  
>    "We chose pessimistic locking (`select_for_update()`) over optimistic locking (version tags) because item handoff acceptance is a high-contention, irreversible action. Locking the row directly at the database level guarantees zero race conditions."
> 2. **Transactional Rejection & Audit Trail**:  
>    "Auto-rejecting competing requests within the same `transaction.atomic()` block ensures that our database never enters an inconsistent state, while `ListingStatusHistory` gives us full auditability."
