---
applyTo: '**'
---

# User Memory

## User Preferences
- Programming languages: Python (Django)
- Code style preferences: Single quotes, 100-char line limit, Google docstrings, snake_case for functions/variables, PascalCase for classes
- Development environment: macOS, VS Code, pytest, ruff
- Communication style: Concise, thorough, minimal repetition

## Project Context
- Current project type: Django REST API backend for Next.js dashboard
- Tech stack: Django 5.2, DRF, drf-spectacular, PostgreSQL
- Architecture patterns: Modular apps (`main`, `users`, `deals`), DRF ViewSets, OpenAPI schema
- Key requirements: OpenAPI contract, standardized responses, incremental phased implementation

## Coding Patterns
- Use mixins for models (UUIDMixin, CreatedAtMixin, UpdatedAtMixin)
- DRF ViewSets with @extend_schema
- ApiResponse for all responses
- Absolute imports from server.apps
- Type annotations required

## Research History
- No external research yet; following provided implementation plan

## Conversation History
- Starting Phase 1: Core dashboard infrastructure (CommunityStats, user profile fields, dashboard overview endpoint)
- Implemented dynamic calculation of total_deals and total_affiliates in CommunityStats model as properties
- Updated CommunityStatsSerializer to expose these as SerializerMethodFields
- Dashboard overview endpoint returns real-time stats
- Edge cases validated: no stats record, inactive users, deal status filtering
- Ready for further business logic enhancements or new endpoints

## Notes
- Memory file created at project start for tracking decisions and progress
- Implementation robust and production-ready; no automated tests written per user request
