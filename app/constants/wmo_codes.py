# Source: https://open-meteo.com/en/docs

WMO_CODES: dict = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Drizzle: light",
    53: "Drizzle: moderatore",
    55: "Drizzle: dense intensity",
    61: "Rain: slight",
    63: "Rain: moderatore",
    65: "Rain: heavy intensity",
    66: "Freezing rain: light",
    67: "Freezing rain: heavy intensity",
    71: "Snow fall: light",
    73: "Snow fall: moderate",
    75:	"Snow fall: heavy intensity",
    77:	"Snow grains",
    80: "Rain showers: light",
    81: "Rain showers: moderate",
    82:	"Rain showers: violent",
    85: "Snow showers: light", 
    86:	"Snow showers: heavy",
    95:	"Thunderstorm: slight or moderate", # Thunderstorm forecast with hail is only available in Central Europe
    96:	"Thunderstorm with slight hail",    # Thunderstorm forecast with hail is only available in Central Europe
    99: "Thunderstorm with heavy hail"      # Thunderstorm forecast with hail is only available in Central Europe
}