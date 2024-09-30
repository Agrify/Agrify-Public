EMISSION_FACTORS = {
    "Nigeria": {
        "Transportation": 0.14,  # kgCO2/km
        "Electricity": 0.439,  # kgCO2/kWh
        "Diet": 1.25,  # kgCO2/meal, 2.5kgco2/kg
        "Waste": 0.1  # kgCO2/kg
    }
}

def calc_carbon(distance, electricity, meals, waste, country):
    # Normalize inputs
    if distance > 0:
        distance = distance * 365  # Convert daily distance to yearly
    if electricity > 0:
        electricity = electricity * 12  # Convert monthly electricity to yearly
    if meals > 0:
        meals = meals * 365  # Convert daily meals to yearly
    if waste > 0:
        waste = waste * 52  # Convert weekly waste to yearly

    # Calculate carbon emissions
    transportation_emissions = EMISSION_FACTORS[country]["Transportation"] * distance
    electricity_emissions = EMISSION_FACTORS[country]["Electricity"] * electricity
    diet_emissions = EMISSION_FACTORS[country]["Diet"] * meals
    waste_emissions = EMISSION_FACTORS[country]["Waste"] * waste

    # Convert emissions to tonnes and round off to 2 decimal points
    transportation_emissions = round(transportation_emissions / 1000, 2)
    electricity_emissions = round(electricity_emissions / 1000, 2)
    diet_emissions = round(diet_emissions / 1000, 2)
    waste_emissions = round(waste_emissions / 1000, 2)

    # Calculate total emissions
    total_emissions = round(
        transportation_emissions + electricity_emissions + diet_emissions + waste_emissions, 2
    )

    data = {
        "transportation_emissions": transportation_emissions,
        "electricity_emissions" : electricity_emissions,
        "diet_emissions": diet_emissions,
        "waste_emissions": waste_emissions,
        "total_emissions": total_emissions

    }

    return data