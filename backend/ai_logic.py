import numpy as np

def calculate_calories(weight, height, age, gender, activity_level, goal):
    """
    Calculate daily calories using Mifflin-St Jeor Equation + Goal adjustment
    activity_level: 1=low, 2=moderate, 3=high
    goal: 'lose', 'maintain', 'gain'
    """
    # Basal Metabolic Rate (BMR)
    if gender.lower() == "male":
        bmr = 10*weight + 6.25*height*30.48 - 5*age + 5
    else:
        bmr = 10*weight + 6.25*height*30.48 - 5*age - 161

    # Activity multiplier
    activity_multiplier = {1: 1.2, 2: 1.5, 3: 1.75}[activity_level]
    calories = bmr * activity_multiplier

    # Goal adjustment
    if goal.lower() == "lose":
        calories -= 500
    elif goal.lower() == "gain":
        calories += 500

    return int(calories)
