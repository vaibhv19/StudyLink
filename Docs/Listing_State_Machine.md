# Listing_State_Machine.md — Marketplace Logic Specification

This document defines the technical implementation of the StudyLink Marketplace state machine. It ensures data integrity, handles concurrency, and provides a clear audit trail for the physical giveaway lifecycle.

---

## 1. State Diagram

The lifecycle of a physical listing is managed through three primary states. The transition from `AVAILABLE` to `REQUESTED` represents a soft-lock where the owner has committed to a specific recipient.

```text
       +------------------+
       |                  |
       |     CREATED      |
       |                  |
       +--------+---------+
                |
                v
       +------------------+                    +------------------+
       |                  |   Accept Request   |                  |
       |    AVAILABLE     +------------------->+    REQUESTED     |
       |                  |                    |                  |
       +--------+----^----+                    +--------+----^----+
                |    |                                  |    |
                |    +---------- Cancel/Fail -----------+    |
                |                                            |
                |             Confirm Handoff                |
                +--------------------------------------------> [ GIVEN AWAY ]
                                                               (Terminal State)
```

---

## 2. Transition Triggers & Ownership

| Transition | Trigger Action | Service/Endpoint | Owner |
| :--- | :--- | :--- | :--- |
| **Initialize** | Item creation | `POST /api/market/` | Owner |
| **Soft Lock** | Picking a recipient | `PATCH /api/market/requests/{id}/accept/` | Owner |
| **Revert** | Handoff fails/canceled | `PATCH /api/market/requests/{id}/cancel/` | Owner / Recipient |
| **Finalize** | Handoff confirmed | `PATCH /api/market/{id}/complete/` | Owner |

*Note: Simply sending a request (`POST /api/market/{id}/request/`) does **not** change the listing state; it creates a `ListingRequest` object associated with the listing.*

---

## 3. Concurrency & Edge Cases

To prevent race conditions (e.g., an owner accepting two people for one item), StudyLink employs **Atomic Database Transactions** and **Pessimistic Locking**.

### 3.1 Race Condition: Double Acceptance
**Scenario:** Owner opens two tabs and tries to "Accept" two different requests at the same time.
**Solution:** The `accept_request` method in `market/services.py` uses Django’s `.select_for_update()`:
1. Lock the `Listing` row.
2. Check `if listing.status != 'AVAILABLE'`.
3. If already taken, rollback and return `409 Conflict`.
4. If available, update status to `REQUESTED` and set `accepted_request_id`.

### 3.2 Audit Trail: Status History
Following the pattern in **Trajectory**, every state change is logged in a `ListingStatusHistory` table:
- `listing_id`: FK to Listing.
- `from_status`: String.
- `to_status`: String.
- `changed_by`: FK to User.
- `reason`: Optional text (e.g., "Recipient didn't show up").

---

## 4. Notification Triggers

| Event | Recipient(s) | Channel |
| :--- | :--- | :--- |
| **New Request Received** | Owner | In-app / Email |
| **Request Accepted** | Selected Recipient | In-app (Unlocks pickup details) |
| **Request Accepted** | Other Requesters | In-app ("Item no longer available") |
| **Request Canceled** | Owner / Recipient | In-app |
| **Item Given Away** | All active requesters | In-app (Archive notification) |

---

## 5. Permissions & Guardrails

### 5.1 Owner Permissions
- Only the `owner_id` can transition a listing to `REQUESTED` or `GIVEN_AWAY`.
- Owners can cancel an accepted request at any time to return the item to `AVAILABLE`.

### 5.2 Requester Permissions
- Non-owners can only `POST` a request if the item is `AVAILABLE`.
- A recipient whose request was `ACCEPTED` can "Withdraw" their request, which automatically triggers a transition back to `AVAILABLE`.
- Requesters cannot see the status history or other people's requests.

---

## 6. Failure Recovery

### 6.1 Mid-Transition Failure
If the `PATCH` to update the status to `REQUESTED` succeeds but the notification service fails, the DB transaction is **not** rolled back. The state integrity is prioritized over the notification. The owner can manually re-trigger a "Resend Info" action from the dashboard.

### 6.2 The "Ghosting" Fallback
If an item remains in the `REQUESTED` state for more than 48 hours without being finalized to `GIVEN_AWAY`, the Owner Dashboard surfaces a prominent "Handoff complete?" prompt, allowing for easy reversion to `AVAILABLE` if the student never picked up the item.