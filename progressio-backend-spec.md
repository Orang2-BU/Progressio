# Progressio Backend Technical Specification (MVP)

> **Version:** MVP v1.0
> **Project:** Progressio
> **Backend Framework:** Django + Django REST Framework

---

## Overview

This document defines the backend architecture and responsibilities for the Progressio MVP.

The backend should **not** implement AI logic or Blockchain logic directly. Instead, it should expose clean APIs and business logic while integrating with AI and Blockchain as external services.

---

## Backend Responsibilities

The backend is responsible for:

- Authentication & Authorization
- Learning Engine
- Competency Management
- Assessment Management
- Progress Tracking
- Credential Management
- Verification API
- Event Publishing
- AI Integration Layer
- Blockchain Integration Layer

The backend is **NOT** responsible for:

- LLM reasoning
- Prompt engineering
- Smart contract implementation
- Blockchain consensus
- AI decision making

---

## System Architecture

```
                Next.js Web
                      │
                      │
React Native App ─────┼────────────▶ Django REST API
                      │
                      ▼
               Business Logic
                      │
     ┌────────────────┼────────────────┐
     │                │                │
     ▼                ▼                ▼
 PostgreSQL      AI Service      Blockchain Service
```

---

## Django App Structure

```
backend/
apps/
├── accounts/
├── careers/
├── competencies/
├── skills/
├── learning/
├── assessments/
├── credentials/
├── verification/
├── ai/
├── blockchain/
└── common/
```

---

## Domain Model

```
User
    │
    ▼
Career Track
    │
    ▼
Competency
    │
    ▼
Skill
    │
    ▼
Lesson
    │
    ▼
Assessment
    │
    ▼
Submission
    │
    ▼
Evidence
    │
    ▼
Credential
```

---

## Database Design

### User

| Field | Notes |
|---|---|
| `id` | |
| `name` | |
| `email` | |
| `password` | |
| `role` | `student`, `recruiter`, `admin` |

---

### CareerTrack

Represents a career pathway.

**Example:** Backend Engineering

| Field | Notes |
|---|---|
| `id` | |
| `title` | |
| `slug` | |
| `description` | |
| `is_active` | |
| `created_at` | |
| `updated_at` | |

---

### Competency

Represents a competency inside a career track.

**Examples:**
- Programming Fundamentals
- Backend Foundations
- Database Engineering
- Authentication
- API Development

| Field | Notes |
|---|---|
| `id` | |
| `career_track_id` | FK → CareerTrack |
| `title` | |
| `slug` | |
| `description` | |
| `order` | |
| `created_at` | |
| `updated_at` | |

---

### Skill

Represents a measurable skill inside a competency.

**Examples:** JWT, SQL, REST API, Docker

| Field | Notes |
|---|---|
| `id` | |
| `competency_id` | FK → Competency |
| `title` | |
| `slug` | |
| `description` | |
| `difficulty` | |
| `estimated_learning_minutes` | |
| `created_at` | |
| `updated_at` | |

---

### SkillPrerequisite

Defines the Skill Graph.

| Field | Notes |
|---|---|
| `id` | |
| `skill_id` | FK → Skill |
| `required_skill_id` | FK → Skill |

**Example:**

```
REST API
   ↓
Authentication
   ↓
Security
```

---

### Lesson

Learning materials.

| Field | Notes |
|---|---|
| `id` | |
| `skill_id` | FK → Skill |
| `title` | |
| `content_type` | `video`, `article`, `exercise`, `reading` |
| `content_url` | |
| `duration` | |
| `order` | |

---

### Assessment

Assessment belongs to one Skill.

**Types:** Quiz, Coding Challenge, Mini Project

| Field | Notes |
|---|---|
| `id` | |
| `skill_id` | FK → Skill |
| `title` | |
| `assessment_type` | `quiz`, `challenge`, `project` |
| `passing_score` | |
| `max_score` | |

---

### Submission

Student submission.

| Field | Notes |
|---|---|
| `id` | |
| `assessment_id` | FK → Assessment |
| `user_id` | FK → User |
| `status` | `draft`, `submitted`, `evaluating`, `completed` |
| `score` | |
| `feedback` | |
| `submitted_at` | |

---

### Evidence

Evidence supporting competency.

**Examples:** GitHub Repository, Uploaded File, Project URL

| Field | Notes |
|---|---|
| `id` | |
| `submission_id` | FK → Submission |
| `github_url` | |
| `file_url` | |
| `demo_url` | |
| `notes` | |

---

### SkillProgress

Stores user mastery.

| Field | Notes |
|---|---|
| `id` | |
| `user_id` | FK → User |
| `skill_id` | FK → Skill |
| `mastery` | |
| `xp` | |
| `confidence` | |
| `last_assessed_at` | |

---

### CompetencyProgress

Stores competency score.

| Field | Notes |
|---|---|
| `id` | |
| `user_id` | FK → User |
| `competency_id` | FK → Competency |
| `score` | |
| `confidence` | |
| `last_updated` | |

---

### Credential

Represents verified competency.

| Field | Notes |
|---|---|
| `id` | |
| `user_id` | FK → User |
| `competency_id` | FK → Competency |
| `status` | `draft`, `issued`, `revoked` |
| `score` | |
| `issued_at` | |

---

### BlockchainCredential

Blockchain metadata only.

| Field | Notes |
|---|---|
| `id` | |
| `credential_id` | FK → Credential |
| `credential_hash` | |
| `transaction_hash` | |
| `network` | |
| `verified` | |
| `revoked` | |

> **Never store student personal information or assessment data on blockchain.**
> Only store credential proof.

---

## API Design

### Authentication

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

---

### Career Tracks

```
GET    /api/v1/career-tracks
GET    /api/v1/career-tracks/{id}
```

---

### Competencies

```
GET    /api/v1/competencies
GET    /api/v1/competencies/{id}
```

---

### Skills

```
GET    /api/v1/skills
GET    /api/v1/skills/{id}
GET    /api/v1/skills/{id}/lessons
```

---

### Learning

```
GET    /api/v1/learning-path
GET    /api/v1/progress
POST   /api/v1/lesson/{id}/complete
```

---

### Assessment

```
GET    /api/v1/assessments
GET    /api/v1/assessments/{id}
POST   /api/v1/assessments/{id}/submit
```

---

### Credentials

```
GET    /api/v1/credentials
GET    /api/v1/credentials/{id}
POST   /api/v1/credentials/issue
```

---

### Verification

```
GET    /api/v1/verify/{credential_id}
```

Public endpoint. Recruiters should not need authentication.

---

## Backend Events

The backend should publish domain events instead of tightly coupling business logic.

### LessonCompleted

```
Lesson Completed
   ↓
Update XP
   ↓
Update Skill Progress
   ↓
Recalculate Learning Progress
```

---

### AssessmentPassed

```
Assessment Passed
   ↓
Update Skill Progress
   ↓
Update Competency Progress
   ↓
Check Credential Eligibility
```

---

### CredentialIssued

```
Credential Created
   ↓
Generate Credential
   ↓
Send Blockchain Job
   ↓
Notify Student
```

---

## Background Jobs (Celery)

The following tasks should be asynchronous:

- AI Evaluation
- Project Evaluation
- Credential PDF Generation
- Blockchain Transaction
- Email Notification
- Push Notification

---

## AI Integration

Backend should never directly call LLM inside Views.

**Recommended architecture:**

```
API
   ↓
Service Layer
   ↓
AI Adapter
   ↓
OpenAI
```

**Example responsibilities:**

- Learning Recommendation
- Skill Gap Analysis
- AI Tutor
- Assessment Evaluation

The AI service should receive structured data and return structured results.

---

## Blockchain Integration

Blockchain is a verification layer. It should only handle:

- Issue Credential
- Verify Credential
- Revoke Credential
- Integrity Check

**Workflow:**

```
Credential Issued
   ↓
Generate Credential JSON
   ↓
SHA-256 Hash
   ↓
Blockchain Service
   ↓
Store Hash
   ↓
Save Transaction Hash
```

---

## Suggested Project Structure

```
backend/
apps/
    accounts/
    careers/
    competencies/
    skills/
    learning/
    assessments/
    credentials/
    verification/
    ai/
    blockchain/
    common/
config/
tests/
```

---

## Sprint Plan

### Sprint 1 — Backend Foundation

- Authentication
- Career Track
- Competency
- Skill
- Skill Graph
- Lesson

---

### Sprint 2 — Learning Engine

- Assessment
- Submission
- Skill Progress
- Competency Progress
- XP

---

### Sprint 3 — Credential System

- Credential
- Evidence
- Verification API

---

### Sprint 4 — External Services

- AI Integration
- Blockchain Integration

---

## Deliverables Before Coding

Before implementation begins, complete the following design artifacts.

### 1. Entity Relationship Diagram (ERD)

Define all entities and relationships.

---

### 2. API Specification

Document all endpoints using OpenAPI / Swagger.

---

### 3. State Machine

Define state transitions for:

- Assessment
- Submission
- Credential

**Example:**

```
Draft
   ↓
Submitted
   ↓
Evaluating
   ↓
Completed
   ↓
Credential Issued
```

---

### 4. Event Catalog

Define all domain events.

**Examples:**

- LessonCompleted
- AssessmentPassed
- CompetencyUpdated
- CredentialIssued

---

## Backend Development Principles

- Follow Clean Architecture principles.
- Separate business logic from Views.
- Use Service Layer for complex logic.
- Keep AI and Blockchain integrations isolated behind adapters.
- Design APIs to be frontend-agnostic.
- Use asynchronous processing for long-running tasks.
- Treat the backend as the source of truth for learning progress, competency scores, and credential eligibility.

---

## MVP Goal

Deliver a complete backend that supports the following end-to-end flow:

```
User Registration
   ↓
Select Career Track
   ↓
Complete Lessons
   ↓
Submit Assessment
   ↓
Update Skill Progress
   ↓
Update Competency Score
   ↓
Issue Credential
   ↓
Store Credential Proof on Blockchain
   ↓
Recruiter Verification
```

This MVP provides the technical foundation for Progressio while allowing AI capabilities and blockchain verification to evolve independently.
