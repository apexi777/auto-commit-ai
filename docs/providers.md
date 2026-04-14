# Provider Guide

This page gives a practical comparison of all supported providers.

Notes:
- Pricing and limits can change. Verify on official pages before production rollout.
- Cost estimates below are rough and assume a typical commit prompt/response size.
- Rough estimate model: ~1,000 input tokens + ~80 output tokens per commit.

## OpenAI

- Typical rate limits: tier-based RPM/TPM limits in account settings.
- Cost estimate per 100 commits (rough): low single-digit USD for `gpt-4o`; lower for smaller models.
- Best use case: balanced quality and speed.
- Pricing: https://openai.com/api/pricing
- Rate limits: https://platform.openai.com/docs/guides/rate-limits

## Anthropic

- Typical rate limits: tier and model dependent (requests/min and tokens/min).
- Cost estimate per 100 commits (rough): low-to-mid single-digit USD for Sonnet-class usage patterns.
- Best use case: strong reasoning and nuanced message quality.
- Pricing: https://www.anthropic.com/pricing
- Rate limits: https://docs.anthropic.com/en/api/rate-limits

## Gemini (Google)

- Typical rate limits: model-based limits with free/paid tiers.
- Cost estimate per 100 commits (rough): free-to-low cost depending on model/tier.
- Best use case: low-cost default and fast iterations.
- Pricing: https://ai.google.dev/gemini-api/docs/pricing
- Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits

## DeepSeek

- Typical rate limits: documented per account/tier in platform docs.
- Cost estimate per 100 commits (rough): generally low cost for chat-class models.
- Best use case: low-cost commit generation and experimentation.
- Pricing: https://platform.deepseek.com/api-docs/pricing
- Docs: https://platform.deepseek.com/api-docs

## Grok (xAI)

- Typical rate limits: account and model dependent.
- Cost estimate per 100 commits (rough): low-to-mid single-digit USD depending on model.
- Best use case: xAI ecosystem users and alternative model behavior.
- Pricing: https://docs.x.ai/docs/models
- Docs: https://docs.x.ai/

## Mistral

- Typical rate limits: model and plan based.
- Cost estimate per 100 commits (rough): low cost for small/latest models; higher for large models.
- Best use case: fast and affordable coding-oriented generation.
- Pricing: https://mistral.ai/pricing
- Docs: https://docs.mistral.ai/
