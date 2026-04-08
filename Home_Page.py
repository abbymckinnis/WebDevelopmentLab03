import streamlit as st


# Title of App
st.title("Web Development Lab03")

# Assignment Data 
# TODO: Fill out your team number, section, and team members

st.header("CS 1301")
st.subheader("Team 15, Web Development - Section B")
st.subheader("Abby McKinnis, Alexander LaBarre")
st.image("images/food.png", width=200)


# Introduction
# TODO: Write a quick description for all of your pages in this lab below, in the form:
#       1. **Page Name**: Description
#       2. **Page Name**: Description
#       3. **Page Name**: Description
#       4. **Page Name**: Description

st.write("""
Welcome to our Streamlit Web Development Lab03 app! You can navigate between the pages using the sidebar to the left. The following pages are:

1. **Food API Explorer**: 
         This app lets you search and filter meals by category, region, or 
         keyword using TheMealDB API. It displays results, provides 
         recipe details, and shows a chart of meal name lengths.
2. **AI Recipe Chatbot**:
         This app acts as a culinary assistant named "Gourmet Guide AI". It uses 
         generative AI to answer your cooking questions while remembering your conversation history.

""")

