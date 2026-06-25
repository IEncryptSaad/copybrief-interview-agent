# CopyBrief Interview Agent

CopyBrief Interview Agent is a deployable MVP for adaptive copywriting client interviews. It runs a chat-style intake, evaluates each client answer, asks targeted follow-up questions when answers are thin or vague, and generates a structured Markdown copywriting brief.

The current MVP is **free and rule-based**. It requires no paid APIs, no database, and no external paid services. The code is also **Claude-ready** through a provider interface so a paid LLM adapter can be added later without rewriting the interview flow.

## Features

- Conversational Gradio interview UI.
- Copywriting discovery across offer, audience, pains, transformation, story, objections, proof, voice, competitors, CTA, guarantees, and constraints.
- Rule-based answer quality scoring: strong, medium, thin, vague, or missing.
- Targeted follow-up questions for incomplete answers.
- Progress tracking and exact phrase capture.
- Markdown brief generation with recommended angles and hooks.
- Modular Python architecture with tests, logging, configuration, and safe error boundaries.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open the local Gradio URL printed in your terminal.

## Run tests

```bash
pytest
```

## Deploy to Hugging Face Spaces

1. Create a new Hugging Face Space.
2. Choose **Gradio** as the SDK.
3. Push this repository to the Space.
4. Hugging Face will install `requirements.txt` and run `app.py`.
5. No secrets are required for the default rule-based MVP.

## Optional Claude / Anthropic path

The app includes `src/providers/anthropic_provider.py` as a safe optional adapter. By default, `PROVIDER=rule_based` and no Anthropic calls are made.

To prepare for a future Claude-backed version:

```bash
cp .env.example .env
# edit .env
PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
```

If `ANTHROPIC_API_KEY` is missing, the app automatically keeps using the free rule-based provider. The current adapter intentionally preserves rule-based behavior until a real SDK-backed implementation is added.

## Architecture overview

```text
app.py                         Gradio UI only
src/config.py                  environment configuration
src/logging_config.py          standard library logging setup
src/models.py                  Pydantic state and result models
src/discovery_schema.py        discovery sections and starter questions
src/interview_controller.py    interview flow orchestration
src/answer_evaluator.py        answer quality scoring
src/followup_generator.py      targeted follow-up generation
src/brief_generator.py         Markdown brief generation
src/providers/base.py          provider interface
src/providers/rule_based.py    free default provider
src/providers/anthropic_provider.py optional future adapter
tests/                         pytest coverage for core behavior
```

The UI does not own interview logic. Answer evaluation, follow-up generation, interview orchestration, and brief generation are separated so each component can evolve independently.


## Extension architecture

The MVP keeps the Gradio app thin and routes all product logic through core services that can later be wrapped by FastAPI or another API layer:

- `app.py` owns Gradio widgets and calls `InterviewController` only.
- `src/interview_controller.py` orchestrates interview state, provider calls, storage, and exporting.
- `src/providers/registry.py` selects the active provider from config.
- `src/storage.py` defines persistence ports plus disabled, memory, and local JSON adapters.
- `src/exporters.py` defines brief exporters and the default Markdown exporter.
- `src/discovery_schema.py` contains data-driven interview templates.

### Feature flags

All premium-ready flags default to `false`, keeping the current app free and local:

| Flag | Current behavior | Future use |
| --- | --- | --- |
| `ENABLE_CLAUDE` | Off; rule-based provider remains default. | Allow a paid Claude adapter when `ANTHROPIC_API_KEY` is present. |
| `ENABLE_PERSISTENCE` | Off; storage is a safe no-op. | Enable local JSON now or Supabase/Postgres later. |
| `ENABLE_ANALYTICS` | Off; no tracking. | Add paid analytics integrations later. |
| `ENABLE_AUTH` | Off; no auth. | Add auth/team workspaces later. |
| `ENABLE_PDF_EXPORT` | Off; Markdown export only. | Add PDF export behind an exporter adapter. |

### How to add a new LLM provider

1. Create a class implementing `InterviewProvider` from `src/providers/base.py`.
2. Register it in `src/providers/registry.py`, for example `registry.register("openai", lambda settings: OpenAIProvider(...))`.
3. Add config/env settings as needed.
4. Set `PROVIDER=openai`. `InterviewController` does not need to change.

### How to add a new storage adapter

1. Implement `InterviewStorage` from `src/storage.py`.
2. Add a branch in `build_storage()` for a new `STORAGE_BACKEND` value.
3. Keep `DisabledStorage` as the fallback so the MVP still runs without persistence.

### How to add a new export format

1. Implement `BriefExporter` from `src/exporters.py`.
2. Inject it into `InterviewController(exporter=...)` or add a small exporter factory when multiple formats are enabled.
3. Keep `MarkdownExporter` as the default free option.

### How to add a new interview template

1. Add another list of `DiscoverySection` objects in `src/discovery_schema.py`.
2. Register it in `DISCOVERY_TEMPLATES`, such as `"customer_support"`, `"research"`, `"sales"`, `"internal_assistant"`, or a domain-specific key.
3. Instantiate `InterviewController(template_key="your_template")`.

### Free now vs premium-ready later

Free now: Gradio UI, rule-based evaluation, follow-ups, exact phrase capture, Markdown brief generation, disabled/in-memory/local JSON storage adapters, and tests.

Premium-ready later: Claude/OpenAI/Gemini/OpenRouter/local model adapters, Supabase/Postgres persistence, PDF/Google Docs/Notion/CRM/email exporters, authentication, analytics, payments, and domain-specific interview templates.

## Future upgrade path

- Replace or augment rule-based evaluation with an LLM provider.
- Add persistence for saved interviews.
- Add export formats such as PDF or Google Docs.
- Add paid features like advanced persona research, competitor analysis, or multi-brief projects.
- Add authentication and team workspaces.

These upgrades should fit behind the existing provider and controller boundaries without major refactoring.
