# Code Examples — Service Module Pattern

Replace `Weather`/`weather` with your service name throughout.

## Interface

```php
<?php

namespace App\Services\Weather\Repositories;

use App\Services\Weather\DTOs\WeatherData;

interface WeatherInterface
{
    public function getCurrent(string $city): WeatherData;
}
```

## Repository

```php
<?php

namespace App\Services\Weather\Repositories;

use App\Services\Weather\DTOs\WeatherData;
use App\Services\Weather\Exceptions\WeatherException;
use Illuminate\Support\Facades\Http;

class WeatherRepository implements WeatherInterface
{
    public function getCurrent(string $city): WeatherData
    {
        $response = Http::get(config('services.weather.url'), [
            'city' => $city,
            'key'  => config('services.weather.key'),
        ]);

        if ($response->failed()) {
            throw new WeatherException("Weather API failed for city: {$city}");
        }

        return WeatherData::from($response->json());
    }
}
```

## DTO (spatie/laravel-data)

```php
<?php

namespace App\Services\Weather\DTOs;

use Spatie\LaravelData\Data;

class WeatherData extends Data
{
    public function __construct(
        public readonly string $city,
        public readonly float  $temperature,
        public readonly string $condition,
    ) {}
}
```

## Exception

```php
<?php

namespace App\Services\Weather\Exceptions;

class WeatherException extends \Exception {}
```

## Provider

```php
<?php

namespace App\Services\Weather\Providers;

use App\Services\Weather\Repositories\WeatherInterface;
use App\Services\Weather\Repositories\WeatherRepository;
use Illuminate\Support\ServiceProvider;

class WeatherProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind(WeatherInterface::class, match($this->app->environment()) {
            'testing' => fn () => new FakeWeatherRepository(),
            default   => fn () => new WeatherRepository(),
        });
    }
}
```

## Facade

```php
<?php

namespace App\Services\Weather\Facades;

use App\Services\Weather\Repositories\WeatherInterface;
use Illuminate\Support\Facades\Facade;

class Weather extends Facade
{
    protected static function getFacadeAccessor(): string
    {
        return WeatherInterface::class;
    }
}
```

## Controller Usage

```php
use App\Services\Weather\Exceptions\WeatherException;
use App\Services\Weather\Facades\Weather;

try {
    $data = Weather::getCurrent($request->validated('city'));

    return response()->json([
        'city'        => $data->city,
        'temperature' => $data->temperature,
        'condition'   => $data->condition,
    ]);
} catch (WeatherException $e) {
    return response()->json(['error' => $e->getMessage()], 502);
}
```

## config/app.php Registration

```php
'providers' => [
    // ...
    App\Services\Weather\Providers\WeatherProvider::class,
],
```

## Alias (optional — if using Facade outside Laravel auto-discovery)

```php
'aliases' => [
    // ...
    'Weather' => App\Services\Weather\Facades\Weather::class,
],
```
