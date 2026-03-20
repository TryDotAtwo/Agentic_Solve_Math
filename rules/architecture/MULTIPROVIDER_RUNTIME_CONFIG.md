# Multiprovider Runtime Config

## Purpose

This document defines the root-level provider architecture for the live multi-agent runtime.

The goal is to keep `python main.py` as the single launch surface while letting the operator switch providers through root config instead of ad-hoc environment hacks.

## Canonical config surfaces

- `../../runtime_config.toml` — non-secret provider, launch, and model-routing config.
- `../../.env` — secret material and optional environment overrides.
- `../../workspace_orchestrator/provider_config.py` — config loader, provider resolver, OpenRouter catalog refresh, and g4f lifecycle management.
- `../../workspace_orchestrator/live_runtime.py` — root and subproject launch flows that activate the resolved provider runtime.
- `../../workspace_orchestrator/model_policy.py` — provider-aware per-agent model assignment.

## Supported providers

### OpenAI

- `active_provider = "openai"`
- Uses `OPENAI_API_KEY`.
- Keeps role-aware model routing:
  - manager / research / audit: `gpt-5.2`
  - coding: `gpt-5.2-codex`
  - history / support: `gpt-5-mini`
- Still accepts Google/Gemini compatibility keys and routes them to the Google OpenAI-compatible endpoint.

### OpenRouter

- `active_provider = "openrouter"`
- Uses `OPENROUTER_API_KEY`.
- Default strategy: `free_pool`.
- Model pool may come from:
  - static fallback list in `runtime_config.toml`;
  - dynamic catalog confirmation from `https://openrouter.ai/api/v1/models`;
  - temporary env override through `ASM_OPENROUTER_FREE_MODELS`.
- Runtime uses `MultiProvider` with:
  - `openai_prefix_mode = "model_id"`
  - `unknown_prefix_mode = "model_id"`
- This keeps namespaced OpenRouter ids usable inside Agents SDK.
- Catalog refresh is intentionally conservative:
  - runtime intersects the discovered free catalog with the root-curated pool;
  - it does not replace the pool with every catalog free model;
  - this keeps model routing reproducible across runs and avoids unstable provider backends entering the root debug path unexpectedly.
- The default curated pool was also tightened after a live failure on `arcee-ai/trinity-mini:free`; root no longer keeps the `arcee-ai/trinity-*` free variants in the default debug pool.

### g4f

- `active_provider = "g4f"`
- Uses a local OpenAI-compatible route, default:
  - `http://127.0.0.1:1337/v1`
- Root runtime can auto-start a local g4f API server from the same operator session.
- If `G4F_API_KEY` is absent, the local server may run without auth and the client uses a sentinel key only to satisfy OpenAI-compatible client requirements.

## Launch invariants

1. `python main.py` remains the single operator entrypoint.
2. Provider choice is config-first:
   - `runtime_config.toml`
   - optional override: `ASM_PROVIDER`
3. Secrets stay out of the committed runtime config and live in `.env` or process env.
4. Root runtime activates the provider, then builds runtime specs and launches agents.
5. The provider activation scope is temporary:
   - env is restored after run completion;
   - auto-started g4f service is terminated when the session ends.

## Why this replaces the old OpenRouter test mode

The previous model relied on `ASM_OPENROUTER_TEST_MODE` as a temporary branch spread across CLI, runtime, and model policy.

That caused:

- fragile bootstrap logic;
- mixed concerns between provider routing and agent model policy;
- poor operator ergonomics;
- harder documentation and reproducibility.

The new architecture moves provider concerns into a canonical root module and config file.

## Verification expectations

- unit tests for config loading, provider resolution, OpenRouter free-pool refresh, and g4f lifecycle;
- runtime tests for provider-aware root/subproject launch;
- CLI tests for config-driven launch behavior;
- dashboard/provider snapshot checks for operator visibility.

## 2026-03-20 stability note

An observed root launch failed with `Clarifai error: Failure` while OpenRouter had temporarily switched to a catalog-expanded free pool. The root runtime now stays pinned to the curated pool order from `runtime_config.toml`, with catalog intersection only. A subsequent live smoke no longer reproduced the Clarifai backend failure; the next blocker became account quota/billing, which is operational rather than architectural.
