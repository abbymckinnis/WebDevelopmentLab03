import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Food API Explorer", page_icon="🍽️")

st.title("Food API Explorer :)")
st.write("Explore meal data using TheMealDB API.")

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

##############################################################################################################################

def get_categories():
    try:
        response = requests.get(f"{BASE_URL}/categories.php", timeout=10)
        response.raise_for_status()
        data = response.json()
        return sorted([item["strCategory"] for item in data["categories"]])
    except Exception:
        return []

##############################################################################################################################

def get_areas():
    try:
        response = requests.get(f"{BASE_URL}/list.php?a=list", timeout=10)
        response.raise_for_status()
        data = response.json()
        return sorted([item["strArea"] for item in data["meals"] if item["strArea"]])
    except Exception:
        return []

##############################################################################################################################

def get_meals_by_category(category):
    try:
        response = requests.get(f"{BASE_URL}/filter.php?c={category}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["meals"] if data["meals"] else []
    except Exception:
        return []

##############################################################################################################################

def get_meals_by_area(area):
    try:
        response = requests.get(f"{BASE_URL}/filter.php?a={area}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["meals"] if data["meals"] else []
    except Exception:
        return []

##############################################################################################################################

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

##############################################################################################################################

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

##############################################################################################################################

def intersect_meals(list1, list2):
    ids2 = {meal["idMeal"] for meal in list2}
    return [meal for meal in list1 if meal["idMeal"] in ids2]

##############################################################################################################################

categories = get_categories()
areas = get_areas()

col1, col2, col3 = st.columns(3)

with col1:
    selected_category = st.selectbox("Choose a category", ["All"] + categories)

with col2:
    selected_area = st.selectbox("Choose a region", ["All"] + areas)

with col3:
    max_results = st.slider("Number of meals to show", 3, 15, 6)

search_text = st.text_input("Search meal name (optional)")

##############################################################################################################################

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

##############################################################################################################################

if selected_category == "All" and selected_area == "All" and not search_text.strip():
    st.warning("Please choose at least one filter or type a search.")
else:
    if not meals:
        st.error("No meals matched your choices.")
    else:
        st.success(f"Found {len(meals)} matching meals.")
        meals_to_show = meals[:max_results]

        st.subheader("Meal Gallery")
        cols = st.columns(3)

        for index, meal in enumerate(meals_to_show):
            with cols[index % 3]:
                st.image(meal["strMealThumb"], caption=meal["strMeal"], use_container_width=True)

        st.subheader("Meal Name Length Chart")

        chart_data = pd.DataFrame({
            "Meal": [meal["strMeal"] for meal in meals_to_show],
            "Name Length": [len(meal["strMeal"]) for meal in meals_to_show]
        }).set_index("Meal")

        st.bar_chart(chart_data)

        ##############################################################################################################################

        st.subheader("Meal Details")

        meal_names = [meal["strMeal"] for meal in meals_to_show]

        selected_meal_name = st.selectbox("Choose a meal to learn more", meal_names)

        selected_meal = next(
            (meal for meal in meals_to_show if meal["strMeal"] == selected_meal_name),
            None
        )

        if selected_meal:
            details = get_meal_details(selected_meal["idMeal"])

            if details:
                st.image(details["strMealThumb"], width=350)
                st.write(f"**Meal Name:** {details['strMeal']}")
                st.write(f"**Category:** {details['strCategory']}")
                st.write(f"**Region:** {details['strArea']}")
                st.write(f"**Instructions:** {details['strInstructions'][:500]}...")
