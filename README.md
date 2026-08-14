# StudyLink

StudyLink is a campus-centric peer-to-peer sharing hub. The project enables students to share digital study materials (with scoped RAG search) and trade physical campus equipment (textbooks, calculators, lab gear) via a strict state-machine listing exchange.

## Architecture & Project Structure

The project is organized as a monorepo containing:

- **`backend/`**: Django REST framework API application.
- **`frontend/`**: React Vite application styled with Tailwind CSS.
- **`Docs/`**: Architectural plans, database schema, API specs, and roadmap milestones.

## Setup & Running the Project

### Running the Backend
Please see instructions in [backend README](file:///d:/Coding/Projects----For%20Resume/StudyLink/backend/README.md).

### Running the Frontend
Please see instructions in [frontend README](file:///d:/Coding/Projects----For%20Resume/StudyLink/frontend/README.md).

## Local Development Services
We use Docker Compose to run local supporting services (like Redis for Celery background tasks).
To spin them up, run:
```bash
docker-compose up -d
```
