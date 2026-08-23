# Learning Doc 07: Decoupled Notifications & Transaction Hooks

> **Topic**: Post-Commit Side Effects (`transaction.on_commit`), In-Process Synchronous Event Handling, and Asynchronous Upgrade Paths.

---

## 1. Problem / Concept

When a user performs a key domain action—such as accepting a marketplace claim request or commenting on a study resource—the application must notify the impacted user (e.g. sending a `REQUEST_ACCEPTED` or `NEW_COMMENT` notification).

Executing notification logic directly inside a database transaction creates two major risks:
1. **Phantom Side Effects**: If notification code runs before `transaction.commit()` completes and the transaction subsequently rolls back due to a database error, the user receives a notification for an event that never actually occurred.
2. **Transaction Bloat**: Heavy side effects executed inside an active transaction lock database rows longer than necessary, reducing system throughput.

---

## 2. How It Works Generally

Django provides `transaction.on_commit(callable)` to solve this problem. `on_commit` registers a callback function that Django executes **only after** the current atomic database transaction successfully commits to disk:
- If the transaction succeeds: `on_commit` callbacks execute immediately after commit.
- If the transaction rolls back: all registered callbacks are discarded without executing.

---

## 3. How StudyLink Specifically Uses It

In `backend/notifications/tasks.py`, `backend/market/services.py`, and `backend/vault/views.py`:

- **Synchronous In-Process Execution (v1 Architecture)**:  
  For v1 scope, StudyLink dispatches notifications synchronously in-process via `send_notification_sync()` inside `transaction.on_commit()` hooks:
  ```python
  transaction.on_commit(lambda: send_notification_sync(
      recipient_id,
      'REQUEST_ACCEPTED',
      f"Request accepted for {listing_title}",
      f"Your request for '{listing_title}' was accepted! Pickup area: {pickup_area}."
  ))
  ```
  This guarantees zero external infrastructure dependencies (no Redis or Celery worker processes required for local dev or v1 deployment) while preserving 100% transactional safety.

- **Design Tradeoff & v2 Celery Upgrade Path**:  
  To support seamless future scaling, `notifications/tasks.py` exports `send_notification_task` decorated with `@shared_task`, which wraps `send_notification_sync`. In v2, if high notification volume or external push services (email, APNS/FCM) introduce API latency, switching dispatch from `send_notification_sync(...)` to `send_notification_task.delay(...)` requires changing only the callback invocation, with zero changes to business domain logic.

---

## 4. Key Files & Code References

- [backend/notifications/tasks.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/notifications/tasks.py#L10-L45) — `send_notification_sync()` implementation and `@shared_task` wrapper.
- [backend/market/services.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/services.py#L60-L81) — `accept_request()` triggering `REQUEST_ACCEPTED` and `ITEM_CLAIMED` on commit.
- [backend/market/views.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/views.py#L113-L122) — `RequestItemView` triggering `NEW_REQUEST` notification.
- [backend/vault/views.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/views.py#L92-L101) — `UpvoteToggleView` triggering `UPVOTE_RECEIVED` notification.

---

## 5. Interview Deep-Dive Takeaways

> [!IMPORTANT]
> **What to highlight in an interview:**
> 1. **Why `transaction.on_commit` is Mandatory for Event Notifications**:  
>    "Triggering notifications inside `transaction.on_commit()` guarantees that users never receive phantom notifications for database state changes that rolled back."
> 2. **Pragmatic v1 Architecture with Clear v2 Upgrade Path**:  
>    "We deliberately opted for synchronous in-process notification creation for v1 to avoid the operational complexity of managing Redis/Celery workers. By wrapping the core logic in a shared task format, we retained a 1-line upgrade path to full async queueing whenever production scale requires it."
