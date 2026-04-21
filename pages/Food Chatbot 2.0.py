import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="Food Data Chatbot", page_icon="🤖")
st.title("Food Data Chatbot 🤖")
st.write("Chat with Gemini using live meal data from TheMealDB API.")

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

if "food_messages" not in st.session_state:
    st.session_state.food_messages = [
        {
            "role": "assistant",
            "content": "Hi! Load a meal first, then ask me questions about its ingredients, cooking style, or food culture."
        }
    ]

if "meal_context" not in st.session_state:
    st.session_state.meal_context = ""

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    st.error("There was a problem setting up Gemini. Check your API key in Streamlit secrets.")
    st.stop()


def search_meals(name):
    try:
        response = requests.get(f"{BASE_URL}/search.php?s={name}", timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["meals"] is None:
            return []
        return data["meals"]
    except Exception:
        return []


def get_ingredients_text(meal):
    ingredients = []

    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():
            if measure and measure.strip():
                ingredients.append(f"{measure.strip()} {ingredient.strip()}")
            else:
                ingredients.append(ingredient.strip())

    return ", ".join(ingredients) if ingredients else "No ingredients listed."


meal_search = st.text_input("Search for a meal to load into the chatbot", "Arrabiata")

if st.button("Load Meal Data"):
    try:
        results = search_meals(meal_search.strip())

        if not results:
            st.error("No meal found. Try a different search.")
        else:
            meal = results[0]
            ingredients_text = get_ingredients_text(meal)

            st.session_state.meal_context = f"""
Meal Name: {meal.get('strMeal', 'Unknown')}
Category: {meal.get('strCategory', 'Unknown')}
Region: {meal.get('strArea', 'Unknown')}
Instructions: {meal.get('strInstructions', 'Unknown')}
Ingredients: {ingredients_text}
"""

            st.session_state.food_messages = [
                {
                    "role": "assistant",
                    "content": f"I loaded {meal.get('strMeal', 'this meal')} for us. Ask me anything about it."
                }
            ]

            st.success(f"Loaded meal data for {meal.get('strMeal', 'Unknown')}")
            st.image(meal.get("strMealThumb", ""), width=300)
            st.write("**Current Meal Context:**")
            st.write(st.session_state.meal_context)

    except Exception:
        st.error("Something went wrong while loading the meal data.")

for message in st.session_state.food_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask a question about the loaded meal")

if user_input:
    st.session_state.food_messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    try:
        if st.session_state.meal_context == "":
            bot_reply = "Please load a meal first so I have food data to use."
        else:
            conversation_text = ""
            for message in st.session_state.food_messages:
                conversation_text += f"{message['role']}: {message['content']}\n"

            prompt = f"""
You are a helpful food chatbot.

Use the meal data below to answer the user's question.
Stay focused on this meal, its ingredients, cooking method, region, and food culture.
If the answer is not directly in the data, say that clearly and give a careful, reasonable response.
Do not make up unsupported facts.

Meal Data:
{st.session_state.meal_context}

Conversation so far:
{conversation_text}

Respond to the user's latest message.
"""
            response = model.generate_content(prompt)
            bot_reply = response.text

    except Exception:
        bot_reply = "Sorry, something went wrong while generating a response. Please try again."

    st.session_state.food_messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.write(bot_reply)
