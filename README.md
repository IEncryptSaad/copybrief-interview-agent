---
title: CopyBrief Interview Agent
emoji: 📝
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.49.1
python_version: 3.11
app_file: app.py
pinned: false
---

# CopyBrief Interview Agent

CopyBrief Interview Agent is a Hugging Face Spaces-ready MVP for adaptive copywriting client discovery. It runs a chat-style intake, asks copywriter-specific follow-ups when answers are thin, preserves useful client phrases, and generates a structured Markdown copywriting brief that remains useful even when the interview is incomplete.

The default app is **free, local, and rule-based**: no paid APIs, no required secrets, no database, no authentication, and no analytics. The architecture is intentionally extensible so Claude or another LLM can be added later behind the provider interface without changing the core interview flow.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the local Gradio URL printed in your terminal.

## Local run command

```bash
python app.py
```

## Test command

```bash
pytest
```

## Hugging Face Spaces deployment

1. Create a new Hugging Face Space.
2. Select **Gradio** as the SDK.
3. Push this repository to the Space.
4. Spaces installs the minimal `requirements.txt` automatically.
5. Spaces runs `app.py` with `python app.py`.
6. Do **not** add secrets for the default demo. `PROVIDER=rule_based` works without API keys.
7. Optional: copy `.env.example` values into Space variables only when you need to override defaults.

## Requirements and secrets

`requirements.txt` intentionally stays small for free-tier deployability:

- `gradio` for the UI
- `pydantic` for state models
- `pytest` for tests
- `python-dotenv` for optional local `.env` files

No secret is required for default operation. `.env.example` clearly marks Anthropic/Claude and persistence-related settings as optional paid or premium-ready features.

## Features

- Gradio chatbot UI using `type="messages"` when supported.
- Polished opening assistant message for copywriting discovery.
- Sections for offer, audience, pains, transformation, story, objections, proof, voice, competitors, CTA, guarantees, and constraints.
- Rule-based answer quality scoring and targeted follow-up questions.
- Exact phrase capture for quotable client language.
- Partial-brief generation at any point in the interview.
- Missing-information list in every generated brief.
- Reset flow that clears chat state, progress, brief preview, and download file.
- Concise logging around startup, reset, answers, and brief generation.
- Safe UI error boundaries that avoid exposing stack traces to users.

## Architecture overview

```text
app.py                         Gradio UI and UI-safe error handling
src/config.py                  environment configuration
src/logging_config.py          standard library logging setup
src/models.py                  Pydantic state and result models
src/discovery_schema.py        copywriting discovery sections and questions
src/interview_controller.py    interview orchestration
src/answer_evaluator.py        answer quality scoring
src/followup_generator.py      targeted follow-up generation
src/brief_generator.py         Markdown brief generation and missing-info handling
src/providers/base.py          provider interface
src/providers/rule_based.py    free default provider
src/providers/anthropic_provider.py optional future Claude adapter placeholder
src/storage.py                 disabled, memory, and local JSON storage adapters
tests/                         pytest coverage for core behavior and UI regressions
```

The UI is thin. Product logic lives in controller, provider, evaluator, follow-up, and brief-generation modules so the app can later be wrapped with an API, persistence layer, or paid LLM provider.

## Extension points

### Add a new LLM provider

1. Implement `InterviewProvider` from `src/providers/base.py`.
2. Register it in `src/providers/registry.py`.
3. Add optional config in `src/config.py` / `.env.example`.
4. Set `PROVIDER=your_provider`.

### Add storage

1. Implement `InterviewStorage` from `src/storage.py`.
2. Add a `build_storage()` branch in `src/interview_controller.py`.
3. Keep `DisabledStorage` as the default fallback so the free demo still works.

### Add export formats

1. Implement `BriefExporter` from `src/exporters.py`.
2. Inject it into `InterviewController(exporter=...)`.
3. Keep Markdown as the default free option.

### Add interview templates

1. Add a list of `DiscoverySection` objects in `src/discovery_schema.py`.
2. Register it in `DISCOVERY_TEMPLATES`.
3. Instantiate `InterviewController(template_key="your_template")`.

## Optional Claude integration

The repository includes `src/providers/anthropic_provider.py` as an optional Claude-ready adapter path. The current MVP does not require Anthropic and does not make paid calls by default.

For a future Claude-backed version:

```bash
cp .env.example .env
# edit .env
PROVIDER=anthropic
ENABLE_CLAUDE=true
ANTHROPIC_API_KEY=your_key_here
python app.py
```

If Claude is not configured, keep `PROVIDER=rule_based` for the free MVP.

## Known limitations

- Rule-based evaluation is deterministic and useful for an MVP, but less nuanced than a real LLM interviewer.
- No database or account system is included; sessions are in-memory unless a future storage adapter is enabled.
- Markdown is the only default export format.
- No analytics dashboard, payments, team workspaces, or CRM integrations are included.
- The generated brief is a strong starting point, not final copy.

## Suggested next paid upgrades

- Claude/OpenAI provider for deeper follow-ups, better synthesis, and richer voice-of-customer extraction.
- PDF, Google Docs, Notion, or CRM export adapters.
- Saved client projects with Supabase/Postgres persistence.
- Authentication and team workspaces.
- Competitor and audience research workflows.
- Paid analytics for interview completion and brief quality.

## Suggested Upwork demo script

1. Open the Space and point out that no paid API key is required.
2. Show the polished first prompt and explain the app is copywriting-specific.
3. Enter one thin answer to demonstrate an adaptive follow-up.
4. Enter a stronger answer with an exact phrase in quotes to show phrase preservation.
5. Click **Generate / Download Markdown Brief** before finishing to demonstrate partial-brief support.
6. Show the **Missing Information** section.
7. Click **Reset Interview** to show a clean session reset.
8. Explain extension points: Claude provider, persistence, export adapters, and additional templates.
