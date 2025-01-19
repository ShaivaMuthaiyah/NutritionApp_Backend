from flask import Flask, request, jsonify

# Nutrition and Caloric Requirement Function
def calculate_nutrition(age, gender, weight, height, activity_level, goal, diet, allergies):

    weight = float(weight)
    height = float(height)
    age = int(age)

    ideal_body_fat_percentage = [0, 0]

    # Basic BMR (Basal Metabolic Rate) Calculation
    if gender == "male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        if age < 29:
            ideal_body_fat_percentage = [7, 17]
        if age in range(30, 40):
            ideal_body_fat_percentage = [12, 21]
        if age in range(40, 50):
            ideal_body_fat_percentage = [14, 23]
        if age in range(50, 60):
            ideal_body_fat_percentage = [16, 24]
        else:
            ideal_body_fat_percentage = [17, 25]

    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        if age < 29:
            ideal_body_fat_percentage = [16, 24]
        if age in range(30, 40):
            ideal_body_fat_percentage = [17, 25]
        if age in range(40, 50):
            ideal_body_fat_percentage = [19, 28]
        if age in range(50, 60):
            ideal_body_fat_percentage = [22, 31]
        else:
            ideal_body_fat_percentage = [22, 33]
        

    # Adjust BMR based on activity level
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }

    caloric_needs = round(bmr * activity_multipliers.get(activity_level, 1.2))

    if goal == "muscle_building":
        caloric_needs += 250  # Add extra calories for muscle building
        protein_per_kg = 1.6  # Average for muscle building: 1.2 to 2.0 grams per kg
    elif goal == "weight_loss":
        caloric_needs -= 500  # Subtract calories for weight loss
        protein_per_kg = 1.2  # Slightly higher protein for weight loss to preserve muscle
    elif goal == "weight_gain":
        caloric_needs += 500  # Add calories for weight loss
        protein_per_kg = 1.2  # Slightly higher protein for weight loss to preserve muscle
    else:  # maintenance
        protein_per_kg = 0.8  # General recommendation for maintaining weight

    protein = round(protein_per_kg * weight)  # grams of protein per kg of body weight
    fat = round(caloric_needs * 0.25 / 9)  # 25% of calories from fat, 9 cal per gram of fat
    carbs = round((caloric_needs - (protein * 4 + fat * 9)) / 4)  # remaining calories from carbs


    # BMI Calculation
    height_m = height / 100  # convert cm to meters
    bmi = round(weight / (height_m ** 2), 1)
    bmi_category = (
        "Underweight" if bmi < 18.5 else
        "Normal weight" if bmi < 25 else
        "Overweight" if bmi < 30 else "Obese"
    )

    # Ideal Body Weight (Broca Index)
    ideal_body_weight = round(50 + 0.9 * (height - 152), 1) if gender == "male" else round(45.5 + 0.9 * (height - 152), 1)


    # Additional Metrics
    body_fat_percentage = round(1.20 * bmi + 0.23 * age - (16.2 if gender == "male" else 5.4), 1)




    print(({


        "basic_metrics": {
            "bmi": bmi,
            "bmi_category": bmi_category,
            "ideal_body_weight": ideal_body_weight,
            "current_weight": weight,
            "body_fat_percentage": body_fat_percentage,
            "ideal_body_fat_percentage": ideal_body_fat_percentage,
        },

        "caloric_needs": {
            "goal_caloric_needs": caloric_needs,
            "macronutrients": {
                "protein": protein,
                "fat": fat,
                "carbs": carbs
            }
        },

        "recommendations": {
            "water_intake": round(weight * 35 / 1000, 2),  # in liters
            "fiber_intake": round(caloric_needs / 1000 * 14, 1),  # grams per day
            "sugar_intake": 30
        },

        "diet_details": {
            "diet": diet,
            "allergies": allergies
        }

    }))


    return ({


        "basic_metrics": {
            "bmi": bmi,
            "bmi_category": bmi_category,
            "ideal_body_weight": ideal_body_weight,
            "current_weight": weight,
            "body_fat_percentage": body_fat_percentage,
            "ideal_body_fat_percentage": ideal_body_fat_percentage
        },

        "caloric_needs": {
            "goal_caloric_needs": caloric_needs,
            "macronutrients": {
                "protein": protein,
                "fat": fat,
                "carbs": carbs
            }
        },

        "recommendations": {
            "water_intake": round(weight * 35 / 1000, 2),  # in liters
            "fiber_intake": round(caloric_needs / 1000 * 14, 1),  # grams per day
            "sugar_intake": 30
        },

        "diet_details": {
            "diet": diet,
            "allergies": allergies
        }

    })
