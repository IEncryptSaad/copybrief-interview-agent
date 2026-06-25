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

## Future upgrade path

- Replace or augment rule-based evaluation with an LLM provider.
- Add persistence for saved interviews.
- Add export formats such as PDF or Google Docs.
- Add paid features like advanced persona research, competitor analysis, or multi-brief projects.
- Add authentication and team workspaces.

These upgrades should fit behind the existing provider and controller boundaries without major refactoring.
