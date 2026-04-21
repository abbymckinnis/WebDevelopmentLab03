import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="AI Food Generator", page_icon="🍽️")
st.title("AI Food Generator 🍽️")
st.write("Use live food API data and Gemini to create fun food content.")

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# Gemini setup
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    st.error("There was a problem setting up Gemini. Check your API key in Streamlit secrets.")
    st.stop()


def get_categories():
    try:
        response = requests.get(f"{BASE_URL}/categories.php", timeout=10)
        response.raise_for_status()
        data = response.json()
        return sorted([item["strCategory"] for item in data["categories"]])
    except Exception:
        return []


def get_areas():
    try:
        response = requests.get(f"{BASE_URL}/list.php?a=list", timeout=10)
        response.raise_for_status()
        data = response.json()
        return sorted([item["strArea"] for item in data["meals"] if item["strArea"]])
    except Exception:
        return []


def get_meals_by_category(category):
    try:
        response = requests.get(f"{BASE_URL}/filter.php?c={category}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["meals"] if data["meals"] else []
    except Exception:
        return []


def get_meals_by_area(area):
    try:
        response = requests.get(f"{BASE_URL}/filter.php?a={area}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["meals"] if data["meals"] else []
    except Exception:
        return []


def search_meals(name):
    try:
        response = requests.get(f"{BASE_URL}/search.php?s={name}", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["meals"] is None:
            return []
        return [
            {
                "idMeal": meal["idMeal"],
                "strMeal": meal["strMeal"],
                "strMealThumb": meal["strMealThumb"]
            }
            for meal in data["meals"]
        ]
    except Exception:
        return []


def get_meal_details(meal_id):
    try:
        response = requests.get(f"{BASE_URL}/lookup.php?i={meal_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["meals"]:
            return data["meals"][0]
        return None
    except Exception:
        return None


def intersect_meals(list1, list2):
    ids2 = {meal["idMeal"] for meal in list2}
    return [meal for meal in list1 if meal["idMeal"] in ids2]


categories = get_categories()
areas = get_areas()

col1, col2, col3 = st.columns(3)

with col1:
    selected_category = st.selectbox("Choose a category", ["All"] + categories)

with col2:
    selected_area = st.selectbox("Choose a region", ["All"] + areas)

with col3:
    content_type = st.selectbox(
        "Choose AI content",
        ["Food Travel Guide", "Chef Review", "Fun Food Facts", "Menu Spotlight"]
    )

tone = st.selectbox(
    "Choose a tone",
    ["Exciting", "Friendly", "Fancy", "Student-Friendly"]
)

search_text = st.text_input("Search meal name (optional)")

meals = []

if selected_category != "All":
    meals = get_meals_by_category(selected_category)

if selected_area != "All":
    area_meals = get_meals_by_area(selected_area)
    if meals:
        meals = intersect_meals(meals, area_meals)
    else:
        meals = area_meals

if search_text.strip():
    search_results = search_meals(search_text.strip())
    if meals:
        meals = intersect_meals(meals, search_results)
    else:
        meals = search_results

if selected_category == "All" and selected_area == "All" and not search_text.strip():
    st.warning("Please choose at least one filter or type a search.")
else:
    if not meals:
        st.error("No meals matched your choices.")
    else:
        meal_names = [meal["strMeal"] for meal in meals[:15]]
        selected_meal_name = st.selectbox("Choose a meal for the AI to focus on", meal_names)

        selected_meal = next(
            (meal for meal in meals if meal["strMeal"] == selected_meal_name),
            None
        )

        if selected_meal:
            details = get_meal_details(selected_meal["idMeal"])

            if details:
                st.image(details["strMealThumb"], width=300)
                st.write(f"**Meal Name:** {details['strMeal']}")
                st.write(f"**Category:** {details['strCategory']}")
                st.write(f"**Region:** {details['strArea']}")

                if st.button("Generate AI Food Content"):
                    try:
                        prompt = f"""
You are a creative food writer.

Use the meal data below to create a {tone.lower()} {content_type.lower()}.

Meal Data:
Meal Name: {details['strMeal']}
Category: {details['strCategory']}
Region: {details['strArea']}
Instructions: {details['strInstructions'][:1200]}

Requirements:
- Make the response detailed and interesting.
- Focus on the food, flavor, culture, and cooking experience.
- Use the API data provided above.
- Do not invent facts that are not supported by the meal data.
- Keep the writing clear and fun to read.
"""
                        response = model.generate_content(prompt)

                        st.subheader("Gemini Output")
                        st.write(response.text)

                    except Exception:
                        st.error("Sorry, something went wrong while generating content. Please try again.")
