---
name: laravel-service-modules
description: Scaffolds, reviews, or refactors external API integrations in Laravel using the Service Module pattern (Repository + Interface + Provider + Facade + DTO + Exception). Use when user asks to "create a new service", "integrate an external API", "build a service module", "review my service class", "refactor API calls out of controllers", "add a facade for my API", or "convert code to service module pattern".
license: MIT
compatibility: Laravel 10+, PHP 8.1+, spatie/laravel-data
tags:
  - laravel
  - php
  - api-integration
  - repository-pattern
  - service-modules
metadata:
  author: theshreif
  version: 1.0.0
---

# Laravel Service Modules

External API integrations belong in self-contained Service Modules — not controllers, not actions, not ad-hoc `Http::` calls. This skill covers three workflows. Ask the user which one they need if not stated:

1. **Implement** — scaffold a new service module from scratch
2. **Review** — audit existing service code for pattern compliance
3. **Refactor** — migrate ad-hoc API code into the pattern

Full pattern reference: `references/pattern-overview.md`
Code examples: `references/code-examples.md`
Anti-patterns & review checklist: `references/anti-patterns.md`

## Scope Boundary (applies to all modes)

**This skill only addresses Service Module pattern adherence.** It is NOT a general code reviewer, security scanner, bug finder, or performance optimizer.

**In scope:**
- File/directory structure under `app/Services/{Name}/`
- Naming conventions (`{Name}Interface`, `{Name}Repository`, `{Name}Data`, etc.)
- Pattern adherence (HTTP calls in Repository, Interface used, DTO returned, typed Exception, Provider binds Interface, Facade maps to Interface)
- Call-site usage (Facade used, Interface type-hinted not concrete)
- Environment branching location (must live in Provider, not Repository)
- Config usage for URLs/keys (via `config()`, not hardcoded)

**Out of scope — do NOT report:**
- Generic PHP hygiene (missing return types, nullable hints, strict types)
- Security issues unrelated to the pattern (hardcoded secrets, CSRF, XSS)
- Generic bug patterns (useless catch-rethrow, silent null returns, typos)
- General code smells (static methods, global helpers, long parameter lists)
- Performance tuning (caching, query optimization) unless directly tied to the pattern

If you notice out-of-scope issues, do not list them as findings. You may add ONE trailing line: `Out of scope: general code review — run /review or /security-review`.

## Output Contract (applies to all modes)

Every output MUST include these sections in this order:

### 1. Tree Diff

Show the current vs expected directory structure using `✓` / `✗` / `⚠` markers:

```
app/Services/{Name}/
├── Repositories/
│   ├── {Name}Interface.php       ✗ missing
│   └── {Name}Repository.php      ✓
├── DTOs/
│   └── {Name}Data.php             ✗ missing
├── Exceptions/
│   └── {Name}Exception.php        ⚠ wrong location (found at app/Exceptions/)
├── Providers/
│   └── {Name}Provider.php         ✗ missing
└── Facades/
    └── {Name}.php                 ⚠ wrong location (found at app/Facades/)

config/app.php providers[]         ⚠ binding lives in AppServiceProvider
```

Legend: `✓` present & correct · `✗` missing · `⚠` present but wrong location/name

### 2. Checklist Summary

Confirm every pattern checkpoint was evaluated. Format: `N/M checked, K passed`.

```
Structure checks:   7/7 checked, 2 passed
Pattern checks:    10/10 checked, 6 passed
Naming checks:      6/6 checked, 6 passed
```

### 3. Findings

Every finding uses this exact format and one of these taxonomy tags:

- `[STRUCTURE]` — missing file, wrong directory, missing Provider registration
- `[PATTERN]` — HTTP in controller, raw array return, concrete injection, env branch in repo, hardcoded URL
- `[NAMING]` — class/file name doesn't match convention

```
[TAG-N] Short title
- Location: path/to/file.php:line
- Problem: one sentence, pattern-focused
- Fix: concrete change, link to references/code-examples.md if scaffolding needed
```

No other tags allowed. No `[SECURITY]`, `[BUG]`, `[CODE]`, `[PERF]`.

### 4. Remediation Order (Review + Refactor only)

List findings in the order the user should fix them. Structure → Pattern → Naming.

## Instructions

### Step 1: Determine Mode

If not clear from context, ask:
> "Do you want me to (1) implement a new service, (2) review existing service code, or (3) refactor code into the service module pattern?"

### Step 2: Gather Info

For **Implement**: ask for the service name and the API methods needed (e.g., `getCurrent(string $city): WeatherData`).
For **Review**: ask user to share the service class(es) or directory path.
For **Refactor**: ask user to share the code containing inline API calls.

### Step 3: Execute

Consult `references/pattern-overview.md` for the directory structure and component roles.
Consult `references/code-examples.md` for boilerplate code per component.
Consult `references/anti-patterns.md` for the pattern checklist and red flags.

---

#### Implement Mode

Generate all six files in order. Follow scope boundary — do NOT add caching, logging, retry logic, or security hardening unless the user explicitly asks. Ship the minimal correct pattern.

1. `{Name}Interface.php`
2. `{Name}Repository.php`
3. `{Name}Data.php` (DTO)
4. `{Name}Exception.php`
5. `{Name}Provider.php`
6. `{Name}.php` (Facade)

Then remind user to register the Provider in `config/app.php`.

**Output:** Tree Diff (all `✓` after generation) + Checklist Summary (all passed) + one-line note on Provider registration. No Findings section needed.

---

#### Review Mode

**Structure violations are first-class findings.** A missing file, wrong directory, or incorrect naming is as critical as a pattern violation. Never bury structure issues in a summary table — each one gets its own `[STRUCTURE-N]` entry.

Step 1 — Structure audit (mandatory, always first):
Verify the expected directory tree under `app/Services/{Name}/` using the Tree Diff format. Check:
- `Repositories/{Name}Interface.php` present?
- `Repositories/{Name}Repository.php` present?
- `DTOs/{Name}Data.php` present?
- `Exceptions/{Name}Exception.php` present?
- `Providers/{Name}Provider.php` present?
- `Facades/{Name}.php` present?
- Provider registered in `config/app.php`?

Step 2 — Pattern audit:
Run every item in `references/anti-patterns.md` checklist. Report `[PATTERN]` findings only for items that violate the pattern. Skip items that are general code hygiene.

Step 3 — Naming audit:
Verify every class/file matches naming convention from `references/pattern-overview.md`.

**Output:** Tree Diff + Checklist Summary + Findings (grouped by tag, `[STRUCTURE]` first) + Remediation Order.

---

#### Refactor Mode

Extract HTTP calls → Repository, derive Interface, wrap responses → DTO, create Exception/Provider/Facade, update call sites to use Facade. Follow scope boundary — do NOT fix unrelated bugs, add features, or improve code quality beyond pattern requirements. If the existing code has a bug, preserve it (note it in Out of scope line if critical).

**Output:** Before Tree Diff + After Tree Diff + Checklist Summary + Findings (each extraction tagged `[STRUCTURE]` or `[PATTERN]` describing what moved) + Remediation Order for anything not yet done.

## Common Issues

Error: Provider not found at runtime
Cause: Provider not registered in `config/app.php`
Solution: Add `\App\Services\{Name}\Providers\{Name}Provider::class` to the `providers` array.

Error: Facade returns null
Cause: `getFacadeAccessor()` returns wrong string or binding missing
Solution: Verify it returns the Interface class string and Provider is registered.
