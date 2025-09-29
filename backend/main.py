import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fpdf import FPDF

app = FastAPI()

# ==== FRONTEND CONFIG ====
frontend_path = os.path.join(os.path.dirname(__file__), "dist")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend assets
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

@app.get("/")
def serve_react():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# ==== MODELS ====
class UserData(BaseModel):
    name: str
    weight: float  # in kg
    height: float  # in cm
    age: int
    gender: str
    activity_level: int
    goal: str

# ==== HELPERS ====
def calculate_calories(weight, height, age, gender, activity_level, goal):
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    factors = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
    calories = bmr * factors.get(activity_level, 1.2)

    if goal.lower() == "lose":
        calories *= 0.85
    elif goal.lower() == "gain":
        calories *= 1.15

    protein = round((0.3 * calories) / 4)  # g
    fat = round((0.25 * calories) / 9)     # g
    carbs = round((0.45 * calories) / 4)   # g
    water = round(weight * 0.04, 1)        # liters

    return {
        "calories": round(calories),
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "water_intake_liters": water
    }

def generate_meal_plan(goal):
    if goal.lower() == "lose":
        return {
            "Breakfast": ["Oats porridge (small portion)", "Banana", "Almonds (5 pcs)"],
            "Mid-morning": ["Green tea", "Apple"],
            "Lunch": ["Brown rice (1 cup)", "Dal", "Vegetable curry", "Curd"],
            "Snack": ["Buttermilk", "Roasted chickpeas"],
            "Dinner": ["2 Roti", "Vegetable soup", "Salad"]
        }
    elif goal.lower() == "gain":
        return {
            "Breakfast": ["Oats + milk", "Banana", "Peanut butter toast"],
            "Mid-morning": ["Milkshake", "Nuts (10-12 pcs)"],
            "Lunch": ["Brown rice (2 cups)", "Paneer curry", "Dal", "Curd"],
            "Snack": ["Smoothie", "Boiled eggs / Chickpeas"],
            "Dinner": ["3 Roti", "Vegetable curry", "Salad"]
        }
    else:
        return {
            "Breakfast": ["Oats porridge", "Banana", "Almonds (7 pcs)"],
            "Mid-morning": ["Green tea", "Seasonal fruit"],
            "Lunch": ["Brown rice (1.5 cups)", "Dal", "Vegetable curry", "Curd"],
            "Snack": ["Buttermilk", "Chickpeas (moderate)"],
            "Dinner": ["2 Roti", "Vegetable soup", "Salad"]
        }

def get_steps_goal(activity_level):
    steps_map = {1: 5000, 2: 7000, 3: 10000, 4: 12000, 5: 15000}
    return steps_map.get(activity_level, 8000)

def generate_pdf(user, diet_plan):
    pdf_dir = os.path.join(os.path.dirname(__file__), "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_file = f"{user['name']}_report.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_file)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Health AI Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Name: {user['name']}", ln=True)
    pdf.cell(200, 10, f"Calories: {diet_plan['calories']} kcal", ln=True)
    pdf.cell(200, 10, f"Protein: {diet_plan['protein']} g", ln=True)
    pdf.cell(200, 10, f"Fat: {diet_plan['fat']} g", ln=True)
    pdf.cell(200, 10, f"Carbs: {diet_plan['carbs']} g", ln=True)
    pdf.cell(200, 10, f"Water: {diet_plan['water_intake_liters']} L", ln=True)
    pdf.cell(200, 10, f"Steps Goal: {diet_plan['steps_goal']} steps", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Diet Plan:", ln=True)
    for meal, items in diet_plan["meals"].items():
        pdf.multi_cell(0, 10, f"{meal}: {', '.join(items)}")

    pdf.output(pdf_path)
    return pdf_file

# ==== API ====
@app.post("/calculate")
def calculate(data: UserData):
    plan = calculate_calories(data.weight, data.height, data.age, data.gender, data.activity_level, data.goal)
    plan["meals"] = generate_meal_plan(data.goal)
    plan["steps_goal"] = get_steps_goal(data.activity_level)

    pdf_file = generate_pdf(data.dict(), plan)

    return {"diet_plan": plan, "pdf_file": pdf_file}

# Serve PDFs
app.mount("/pdfs", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "pdfs")), name="pdfs")
