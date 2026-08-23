# Learning Doc 06: Doubt Board & Interactive Q&A Tree

> **Topic**: Hierarchical Data Trees (Self-Referential Models), Solution Marking, and Atomic Upvoting with Race Condition Prevention.

---

## 1. Problem / Concept

When students review study materials in the Resource Vault, they often have specific questions about formulas, diagrams, or problem sets on a given page. A flat comment section fails to capture discussion context:
- Students need **threaded discussions** (replying directly to a specific question).
- Questions need **status resolution** (marking a reply as `is_solved=True`).
- Resource popularity needs **peer upvoting** without allowing duplicate votes or race conditions in vote totals.

---

## 2. How It Works Generally

1. **Self-Referential Models**: A model represents a tree node by declaring a foreign key pointing to itself (`parent = models.ForeignKey('self', null=True, blank=True)`). Top-level comments have `parent=None`, while replies reference their parent comment.
2. **Recursive Serialization**: The serializer serializes top-level comments and recursively resolves child nodes via a `SerializerMethodField` or nested serializer invocation.
3. **Atomic Upvote Counters**: Modifying counter fields in databases using standard Python assignment (`obj.count += 1; obj.save()`) creates race conditions under concurrent requests. Using Django's `F('upvote_count') + 1` executes an atomic SQL update directly inside the database engine:
   $$\text{UPDATE vault\_resource SET upvote\_count = upvote\_count + 1 WHERE id = ...}$$

---

## 3. How StudyLink Specifically Uses It

In `backend/vault/models.py`, `serializers.py`, and `views.py`:

- **Doubt Board Model (`DoubtBoardComment`)**:
  ```python
  class DoubtBoardComment(models.Model):
      resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="comments")
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
      parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
      content = models.TextField()
      is_solved = models.BooleanField(default=False)
      created_at = models.DateTimeField(auto_now_add=True)
  ```
- **Recursive Tree Serializer (`DoubtBoardCommentSerializer`)**:
  `CommentListCreateView` fetches top-level comments (`parent=None`). `DoubtBoardCommentSerializer.get_replies()` recursively serializes child replies ordered by `created_at`.
- **Solution Marking (`CommentDetailView`)**:
  Allows either the comment author or the resource uploader to toggle `is_solved=True`, visually highlighting resolved doubts.
- **Atomic Upvoting (`ResourceUpvote` + `F()` expression)**:
  `ResourceUpvote` enforces a database `unique_together = ('resource', 'user')` constraint. `UpvoteToggleView` wraps insertion/deletion and `F('upvote_count') +/- 1` inside an atomic transaction.

---

## 4. Key Files & Code References

- [backend/vault/models.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/models.py#L43-L81) — `ResourceUpvote` and `DoubtBoardComment` model definitions.
- [backend/vault/serializers.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/serializers.py#L70-L93) — `DoubtBoardCommentSerializer` with recursive `get_replies()`.
- [backend/vault/views.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/views.py#L54-L106) — `UpvoteToggleView` atomic counter mutation.
- [backend/vault/views.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/views.py#L161-L183) — `CommentDetailView` solution marking authorization logic.

---

## 5. Interview Deep-Dive Takeaways

> [!TIP]
> **What to highlight in an interview:**
> 1. **Why `F()` Expressions for Counters?**  
>    "Using `F('upvote_count') + 1` avoids read-modify-write race conditions by performing the arithmetic directly inside the SQL query engine, guaranteeing atomic accuracy under concurrent API traffic."
> 2. **Self-Referential Tree Traversal**:  
>    "Modeling comments with a self-referential foreign key allows clean representation of unlimited discussion depth while keeping top-level queries fast with `select_related` and prefetching."
