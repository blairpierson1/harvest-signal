"""Signal generation logic for soft commodities based on weather data."""

from app.models import Signal, Confidence


# Thresholds for signal generation
DROUGHT_THRESHOLDS = {
    "Coffee": {"precip_low": 1.5, "temp_high": 30.0, "humidity_low": 50.0},
    "Sugar": {"precip_low": 1.5, "temp_high": 35.0, "humidity_low": 45.0},
    "Cocoa": {"precip_low": 2.0, "temp_high": 33.0, "humidity_low": 55.0},
}

FLOOD_THRESHOLDS = {
    "Coffee": {"precip_high": 12.0, "humidity_high": 88.0},
    "Sugar": {"precip_high": 15.0, "humidity_high": 90.0},
    "Cocoa": {"precip_high": 14.0, "humidity_high": 90.0},
}

HEAT_STRESS_THRESHOLDS = {
    "Coffee": 33.0,
    "Sugar": 38.0,
    "Cocoa": 35.0,
}


def analyze_region(commodity: str, region: dict) -> dict:
    """Analyze a single region's weather and return signal components."""
    thresholds_drought = DROUGHT_THRESHOLDS[commodity]
    thresholds_flood = FLOOD_THRESHOLDS[commodity]
    heat_threshold = HEAT_STRESS_THRESHOLDS[commodity]

    precip_daily = region.get("precipitation_daily_avg", 0.0)
    temp_max = region.get("temperature_max", 0.0)
    temp_avg = region.get("temperature_avg", 0.0)
    humidity = region.get("relative_humidity", 0.0)

    drought_score = 0
    flood_score = 0
    heat_score = 0

    # Drought detection
    if precip_daily < thresholds_drought["precip_low"]:
        drought_score += 2
    if humidity < thresholds_drought["humidity_low"]:
        drought_score += 1
    if temp_avg > thresholds_drought["temp_high"]:
        drought_score += 1

    # Flood / excess rain detection
    if precip_daily > thresholds_flood["precip_high"]:
        flood_score += 2
    if humidity > thresholds_flood["humidity_high"]:
        flood_score += 1

    # Heat stress detection
    if temp_max > heat_threshold:
        heat_score += 2
    elif temp_max > heat_threshold - 3:
        heat_score += 1

    return {
        "drought_score": drought_score,
        "flood_score": flood_score,
        "heat_score": heat_score,
        "precip_daily": precip_daily,
        "temp_max": temp_max,
        "temp_avg": temp_avg,
        "humidity": humidity,
    }


def generate_condition_summary(analysis: dict) -> str:
    """Generate a human-readable condition summary for a region."""
    if analysis["drought_score"] >= 3:
        return "Severe drought conditions"
    elif analysis["drought_score"] >= 2:
        return "Dry conditions, below-average rainfall"
    elif analysis["flood_score"] >= 2:
        return "Heavy rainfall, potential flooding"
    elif analysis["flood_score"] >= 1:
        return "Above-average rainfall"
    elif analysis["heat_score"] >= 2:
        return "Extreme heat stress"
    elif analysis["heat_score"] >= 1:
        return "Elevated temperatures"
    else:
        return "Normal growing conditions"


def generate_commodity_signal(
    commodity: str, regions: list[dict]
) -> tuple[Signal, Confidence, str, str]:
    """
    Generate a composite signal for a commodity across all its growing regions.

    Returns: (signal, confidence, key_driver, rationale)
    """
    analyses = []
    for region in regions:
        analysis = analyze_region(commodity, region)
        analysis["region_name"] = region["region_name"]
        analysis["country"] = region["country"]
        analyses.append(analysis)

    # Aggregate scores across regions
    total_drought = sum(a["drought_score"] for a in analyses)
    total_flood = sum(a["flood_score"] for a in analyses)
    total_heat = sum(a["heat_score"] for a in analyses)

    # Find the most impacted region
    max_drought_region = max(analyses, key=lambda a: a["drought_score"])
    max_flood_region = max(analyses, key=lambda a: a["flood_score"])
    max_heat_region = max(analyses, key=lambda a: a["heat_score"])

    # Determine primary signal
    if total_drought >= 5 or (total_drought >= 3 and total_heat >= 2) or total_heat >= 4:
        # Drought/heat → supply risk → bullish for prices
        signal = Signal.BULLISH

        if total_heat >= total_drought:
            driver_region = max_heat_region
            key_driver = f"Heat stress in {driver_region['region_name']}, {driver_region['country']}"
            rationale = (
                f"Sustained high temperatures ({driver_region['temp_max']:.0f}°C max) threaten "
                f"{commodity.lower()} yields in key growing regions, signaling potential supply tightening."
            )
        else:
            driver_region = max_drought_region
            key_driver = f"Drought conditions in {driver_region['region_name']}, {driver_region['country']}"
            rationale = (
                f"Below-average rainfall ({driver_region['precip_daily']:.1f}mm/day) and low humidity "
                f"({driver_region['humidity']:.0f}%) in {driver_region['region_name']} risk {commodity.lower()} "
                f"production shortfalls."
            )

        max_score = max(total_drought, total_heat)
        confidence = Confidence.HIGH if max_score >= 6 else Confidence.MEDIUM

    elif total_flood >= 4:
        # Excess rain → varies: can be bearish (harvest disruption) or bullish (quality issues)
        # For soft commodities, excess rain during harvest = bearish (damages crop quality)
        signal = Signal.BEARISH
        driver_region = max_flood_region
        key_driver = f"Excess rainfall in {driver_region['region_name']}, {driver_region['country']}"
        rationale = (
            f"Heavy precipitation ({driver_region['precip_daily']:.1f}mm/day avg) risks harvest disruption "
            f"and quality degradation in {driver_region['region_name']}, pressuring near-term prices."
        )
        confidence = Confidence.HIGH if total_flood >= 6 else Confidence.MEDIUM

    elif total_drought >= 3:
        # Moderate drought → mild bullish
        signal = Signal.BULLISH
        driver_region = max_drought_region
        key_driver = f"Dry spell in {driver_region['region_name']}, {driver_region['country']}"
        rationale = (
            f"Drier-than-normal conditions in {driver_region['region_name']} may stress "
            f"{commodity.lower()} crops if prolonged, providing mild upside bias."
        )
        confidence = Confidence.LOW

    elif total_flood >= 2:
        # Moderate excess rain
        signal = Signal.BEARISH
        driver_region = max_flood_region
        key_driver = f"Above-average rainfall in {driver_region['region_name']}, {driver_region['country']}"
        rationale = (
            f"Elevated precipitation levels in {driver_region['region_name']} could impact "
            f"harvest logistics for {commodity.lower()}, slight downward pressure."
        )
        confidence = Confidence.LOW

    else:
        # Normal conditions
        signal = Signal.NEUTRAL
        key_driver = "Normal weather across growing regions"
        rationale = (
            f"Weather conditions across major {commodity.lower()} producing regions are within "
            f"seasonal norms. No significant supply disruption expected."
        )
        confidence = Confidence.MEDIUM

    return signal, confidence, key_driver, rationale
