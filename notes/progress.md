# Progress

## Current state
- FastAPI app runs locally on port 8080.
- GET /health returns {"status": "ok"}.
- Health endpoint has one passing pytest test.
- Ruff passes.
- Smoke client can call the LLM gateway on port 8000.
- First curriculum generation returned valid JSON.
- Curriculum and CurriculumNode Pydantic models are being added.

## Last completed
- Proved downstream app -> gateway -> provider -> normalized response.
- Observed client timeout at 40s while gateway succeeded at ~57s.
- Increased smoke client timeout to 90s.
- Added Pydantic validation with Curriculum.model_validate_json(...).

## Next step
- Confirm the generated curriculum validates successfully.
- Save one raw generation output locally.
- Decide whether to add controlled RequestError and ValidationError handling.

## Open questions
- Where should generation records be stored before a database exists?
- What metadata belongs on Curriculum versus CurriculumGenerationRecord?
- What should the production timeout budget be between client and gateway?