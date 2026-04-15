# Anti-Patterns & Review Checklist

## Review Checklist (run top-to-bottom)

| # | Check | Red Flag | Fix |
|---|---|---|---|
| 1 | HTTP calls location | `Http::` in controller, action, or model | Move to Repository |
| 2 | Interface exists | No `{Name}Interface.php` | Add Interface, bind in Provider |
| 3 | Return type | `$response->json()` array returned raw | Wrap in DTO |
| 4 | Exception type | `catch (\Exception $e)` in controller | Create `{Name}Exception`, catch specifically |
| 5 | Facade exists | `new {Name}Repository()` at call sites | Create Facade, use `{Name}::method()` |
| 6 | Provider registered | `BindingResolutionException` at runtime | Register Provider in `config/app.php` |
| 7 | Environment branching | `if (app()->environment('testing'))` inside repo | Move `match()` to Provider |
| 8 | Constructor injection | `__construct(WeatherRepository $repo)` (concrete) | Type-hint Interface, not Repository |
| 9 | Config hardcoded | `Http::get('https://api.weather.com/...')` literal | Use `config('services.weather.url')` |
| 10 | DTO completeness | Missing properties, using `$data['key']` in consumer | Add typed property to DTO |

## Anti-Pattern Examples

### Direct HTTP in Controller
```php
// BAD
public function show(Request $request): JsonResponse
{
    $response = Http::get('https://api.weather.com/current', [
        'city' => $request->city,
    ]);
    return response()->json($response->json());
}

// GOOD
public function show(Request $request): JsonResponse
{
    try {
        $data = Weather::getCurrent($request->validated('city'));
        return response()->json(['temperature' => $data->temperature]);
    } catch (WeatherException $e) {
        return response()->json(['error' => $e->getMessage()], 502);
    }
}
```

### Raw Array Return
```php
// BAD — consumer doesn't know shape, risks undefined key errors
public function getCurrent(string $city): array
{
    return Http::get(...)->json();
}

// GOOD — typed, predictable
public function getCurrent(string $city): WeatherData
{
    return WeatherData::from(Http::get(...)->json());
}
```

### Concrete Class Injection
```php
// BAD — tests always hit real API
public function __construct(private WeatherRepository $weather) {}

// GOOD — Provider swaps implementation per environment
public function __construct(private WeatherInterface $weather) {}
```

### Environment Check in Business Logic
```php
// BAD — pollutes repository with environment awareness
public function getCurrent(string $city): WeatherData
{
    if (app()->environment('testing')) {
        return new WeatherData(city: $city, temperature: 22.0, condition: 'sunny');
    }
    return WeatherData::from(Http::get(...)->json());
}

// GOOD — create FakeWeatherRepository, bind in Provider match()
```

## Enhancement Suggestions

Offer these when reviewing a working-but-improvable service:

- **Caching:** Wrap `Http::get()` in `Cache::remember()` for stable data
- **Retry:** Use `Http::retry(3, 100)->get(...)` for flaky APIs
- **Timeout:** Add `Http::timeout(10)->get(...)` to prevent hung requests
- **Logging:** Log failures in the Exception constructor or a `report()` override
- **Fake repository:** Add `Fake{Name}Repository` for fast unit tests without HTTP
- **DTO casting:** Use `spatie/laravel-data` casts for nested objects or dates
