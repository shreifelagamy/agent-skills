# Service Module Pattern Overview

Source: https://medium.com/@theshreif/simplify-external-api-integrations-in-laravel-using-service-modules-56493a651a0e

## Directory Structure

```
app/Services/{ServiceName}/
├── Repositories/
│   ├── {ServiceName}Interface.php   ← defines method contracts
│   └── {ServiceName}Repository.php  ← real HTTP implementation
├── Providers/
│   └── {ServiceName}Provider.php    ← binds interface per environment
├── Facades/
│   └── {ServiceName}.php            ← app-wide access shortcut
├── Exceptions/
│   └── {ServiceName}Exception.php   ← typed, service-specific error
└── DTOs/
    └── {ServiceName}Data.php        ← typed response (spatie/laravel-data)
```

## Component Roles

| Component | Responsibility |
|---|---|
| Interface | Contract — defines method signatures only, no logic |
| Repository | Makes HTTP calls, returns DTOs, throws Exception on failure |
| DTO | Typed value object wrapping the API response |
| Exception | Service-specific error, extends `\Exception` |
| Provider | Binds Interface → Repository in the container, environment-aware |
| Facade | Provides static-style access to the Interface via container |

## Data Flow

```
Controller/Action
  → Facade::method()
    → resolves Interface from container
      → Provider bound Repository
        → HTTP call to external API
          → response mapped to DTO
            → DTO returned up the chain
              ← Exception thrown on failure (caught in controller)
```

## Namespace Convention

```
App\Services\{ServiceName}\Repositories\{ServiceName}Interface
App\Services\{ServiceName}\Repositories\{ServiceName}Repository
App\Services\{ServiceName}\DTOs\{ServiceName}Data
App\Services\{ServiceName}\Exceptions\{ServiceName}Exception
App\Services\{ServiceName}\Providers\{ServiceName}Provider
App\Services\{ServiceName}\Facades\{ServiceName}
```

For this project use `Tamkeen\Musaned` as root namespace.

## Key Principles

- Controllers never call `Http::` directly
- Repositories implement the Interface, not abstract classes
- Providers use `match($this->app->environment())` for fake/real binding
- Facades map to the Interface (not the Repository) for testability
- DTOs use `spatie/laravel-data` — extend `Spatie\LaravelData\Data`
- One service = one folder, fully self-contained
