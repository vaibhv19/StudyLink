# Learning Doc 10: Supabase Storage & S3 API Interoperability

> **Topic**: Object Storage Abstractions, The S3 Protocol as a De Facto Industry Standard, `django-storages`, and Environment-Driven Storage Drivers.

---

## 1. Problem / Concept

Applications that accept file uploads (such as PDF study guides or marketplace listing photos) require durable **cloud object storage**. However, coupling application code to vendor-specific SDKs (e.g. Supabase JS/Python client vs. AWS SDK) creates vendor lock-in and makes local development and multi-cloud deployment difficult.

---

## 2. How It Works Generally

**Amazon S3 as an Industry Standard**:  
Amazon S3 introduced a simple REST API model for cloud objects (buckets, keys, presigned URLs, multipart uploads). Because S3 dominated cloud infrastructure for over a decade, its API became the **de facto standard protocol for object storage**.

Modern cloud providers (Supabase, Cloudflare R2, DigitalOcean Spaces, MinIO) implement S3-compatible REST endpoints. This allows standard S3 client libraries—such as Python's `boto3` and Django's `django-storages`—to interact with non-AWS storage services simply by overriding the **S3 Endpoint URL**.

---

## 3. How StudyLink Specifically Uses It

In `backend/config/settings.py`, `backend/vault/storage.py`, and `backend/market/storage.py`:

- **Configuration (`config/settings.py`)**:
  When `USE_S3=True`, Django configures `storages.backends.s3.S3Storage` using standard `AWS_*` variable names, but points `AWS_S3_ENDPOINT_URL` to Supabase:
  ```python
  if USE_S3:
      AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
      AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
      AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
      AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL') # https://<project-ref>.storage.supabase.co/storage/v1/s3
      AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
      AWS_S3_SIGNATURE_VERSION = 's3v4'
  ```
- **Custom Storage Drivers (`ResourceStorage` & `ListingStorage`)**:
  Inherits dynamically from `S3Storage` (if `USE_S3=True`) or `FileSystemStorage` (if `USE_S3=False`):
  ```python
  class ResourceStorage(S3Storage if getattr(settings, 'USE_S3', False) else FileSystemStorage):
      def __init__(self, *args, **kwargs):
          if getattr(settings, 'USE_S3', False):
              kwargs['location'] = 'resources'
          else:
              kwargs['location'] = os.path.join(settings.MEDIA_ROOT, 'resources')
          super().__init__(*args, **kwargs)
  ```
  This allows uploaded files to land in Supabase S3 bucket subfolders in production, while landing in local `media/resources/` during offline development.

---

## 4. Key Files & Code References

- [backend/config/settings.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/config/settings.py#L131-L161) — `USE_S3` and `AWS_*` settings configuration block.
- [backend/vault/storage.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/vault/storage.py#L1-L14) — `ResourceStorage` dual-driver implementation.
- [backend/market/storage.py](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/market/storage.py#L1-L14) — `ListingStorage` implementation for marketplace images.

---

## 5. Interview Deep-Dive Takeaways

> [!IMPORTANT]
> **What to highlight in an interview:**
> 1. **Why standard `AWS_*` settings are used for Supabase**:  
>    "Using `django-storages` with `AWS_*` variable names to target Supabase Storage reveals a key architectural insight: S3 is no longer just an AWS product, but an industry-standard protocol. Using the S3-compatible endpoint gives us zero vendor lock-in."
> 2. **Environment-Driven Driver Switching**:  
>    "Our storage classes inspect `USE_S3` at runtime to inherit dynamically from either `S3Storage` or `FileSystemStorage`. Developers can run the application offline with zero cloud credentials required."
