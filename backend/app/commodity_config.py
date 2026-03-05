"""Consolidated per-commodity configuration for all soft commodities.

Every module that needs commodity-specific data should import from here
rather than defining its own dictionaries.
"""

COMMODITIES: dict[str, dict] = {
    "Coffee": {
        "ticker": "KC=F",
        "av_fallback_function": "COFFEE",
        "estimated_price": 365.00,
        "unit": "\u00a2/lb",
        "icon": "\u2615",
        "regions": [
            {
                "region_name": "Minas Gerais",
                "country": "Brazil",
                "latitude": -18.51,
                "longitude": -44.55,
            },
            {
                "region_name": "S\u00e3o Paulo State",
                "country": "Brazil",
                "latitude": -22.19,
                "longitude": -48.79,
            },
            {
                "region_name": "Central Highlands",
                "country": "Vietnam",
                "latitude": 14.35,
                "longitude": 108.00,
            },
        ],
        "producers": [
            {"country": "Brazil", "share_percent": 37.4, "latitude": -18.51, "longitude": -44.55},
            {"country": "Vietnam", "share_percent": 17.4, "latitude": 14.35, "longitude": 108.00},
            {"country": "Colombia", "share_percent": 7.2, "latitude": 4.60, "longitude": -75.80},
            {"country": "Indonesia", "share_percent": 6.6, "latitude": -2.50, "longitude": 115.00},
            {"country": "Ethiopia", "share_percent": 4.5, "latitude": 7.00, "longitude": 38.00},
        ],
        "baselines": {
            "temp": {"Brazil": 23.0, "Vietnam": 24.0},
            "precip": {"Brazil": 5.0, "Vietnam": 6.0},
        },
        "thresholds": {
            "drought": {"precip_low": 1.5, "temp_high": 30.0, "humidity_low": 50.0},
            "flood": {"precip_high": 12.0, "humidity_high": 88.0},
            "heat_stress": 33.0,
            "risk": {
                "temp_watch": 28.0,
                "temp_alert": 32.0,
                "precip_low_watch": 2.0,
                "precip_low_alert": 1.0,
                "precip_high_watch": 10.0,
                "precip_high_alert": 14.0,
                "humidity_low": 50.0,
            },
        },
    },
    "Sugar": {
        "ticker": "SB=F",
        "av_fallback_function": None,
        "estimated_price": 14.00,
        "unit": "\u00a2/lb",
        "icon": "\ud83c\udf6c",
        "regions": [
            {
                "region_name": "S\u00e3o Paulo State",
                "country": "Brazil",
                "latitude": -22.19,
                "longitude": -48.79,
            },
            {
                "region_name": "Ribeir\u00e3o Preto",
                "country": "Brazil",
                "latitude": -21.18,
                "longitude": -47.81,
            },
            {
                "region_name": "Uttar Pradesh",
                "country": "India",
                "latitude": 27.18,
                "longitude": 80.35,
            },
        ],
        "producers": [
            {"country": "Brazil", "share_percent": 21.0, "latitude": -22.19, "longitude": -48.79},
            {"country": "India", "share_percent": 18.5, "latitude": 27.18, "longitude": 80.35},
            {"country": "Thailand", "share_percent": 5.8, "latitude": 14.88, "longitude": 100.00},
            {"country": "China", "share_percent": 5.5, "latitude": 23.83, "longitude": 108.33},
            {"country": "Pakistan", "share_percent": 3.6, "latitude": 30.20, "longitude": 71.50},
        ],
        "baselines": {
            "temp": {"Brazil": 24.0, "India": 28.0},
            "precip": {"Brazil": 4.5, "India": 3.0},
        },
        "thresholds": {
            "drought": {"precip_low": 1.5, "temp_high": 35.0, "humidity_low": 45.0},
            "flood": {"precip_high": 15.0, "humidity_high": 90.0},
            "heat_stress": 38.0,
            "risk": {
                "temp_watch": 32.0,
                "temp_alert": 36.0,
                "precip_low_watch": 2.0,
                "precip_low_alert": 1.0,
                "precip_high_watch": 12.0,
                "precip_high_alert": 16.0,
                "humidity_low": 45.0,
            },
        },
    },
    "Cocoa": {
        "ticker": "CC=F",
        "av_fallback_function": None,
        "estimated_price": 3050.00,
        "unit": "$/ton",
        "icon": "\ud83c\udf6b",
        "regions": [
            {
                "region_name": "Ashanti Region",
                "country": "Ghana",
                "latitude": 6.75,
                "longitude": -1.52,
            },
            {
                "region_name": "Western Region",
                "country": "Ghana",
                "latitude": 5.50,
                "longitude": -2.50,
            },
            {
                "region_name": "Bas-Sassandra",
                "country": "Ivory Coast",
                "latitude": 5.28,
                "longitude": -6.58,
            },
        ],
        "producers": [
            {"country": "Ivory Coast", "share_percent": 38.2, "latitude": 5.28, "longitude": -6.58},
            {"country": "Ghana", "share_percent": 17.0, "latitude": 6.75, "longitude": -1.52},
            {"country": "Indonesia", "share_percent": 5.1, "latitude": -1.50, "longitude": 120.50},
            {"country": "Nigeria", "share_percent": 4.8, "latitude": 7.50, "longitude": 3.90},
            {"country": "Ecuador", "share_percent": 4.5, "latitude": -1.80, "longitude": -79.50},
        ],
        "baselines": {
            "temp": {"Ghana": 27.0, "Ivory Coast": 27.0},
            "precip": {"Ghana": 5.5, "Ivory Coast": 6.0},
        },
        "thresholds": {
            "drought": {"precip_low": 2.0, "temp_high": 33.0, "humidity_low": 55.0},
            "flood": {"precip_high": 14.0, "humidity_high": 90.0},
            "heat_stress": 35.0,
            "risk": {
                "temp_watch": 30.0,
                "temp_alert": 34.0,
                "precip_low_watch": 2.5,
                "precip_low_alert": 1.5,
                "precip_high_watch": 12.0,
                "precip_high_alert": 15.0,
                "humidity_low": 55.0,
            },
        },
    },
}
