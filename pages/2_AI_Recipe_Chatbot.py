import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Recipe Chatbot", page_icon="🤖")

st.title("AI Recipe Chatbot 👨‍🍳")

if st.button("Clear Chat"):
    st.session_state.messages = [{"role": "assistant", "content": """
        Hey there, Foodie! I'm Gourmet Guide AI, your go-to expert for all things 
        culinary. Whether you need recipe advice, ingredient substitutions, or just 
        someone to talk to about the world of cooking, I've got you covered!"""
                                  }]
    st.rerun()

##############################################################################################################################

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": """
        Hey there, Foodie! I'm Gourmet Guide AI, your go-to expert for all things 
        culinary. Whether you need recipe advice, ingredient substitutions, or just 
        someone to talk to about the world of cooking, I've got you covered!"""
                                  }]


##############################################################################################################################

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-3-flash-preview")
except Exception:
    st.error("There was a problem setting up the chatbot. Check your API key in Streamlit secrets.")
    st.stop()

##############################################################################################################################

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"], avatar="😋"):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message(message["role"], avatar="images/chef.png"):
            st.write(message["content"])

##############################################################################################################################

user_input = st.chat_input("Ask a question about food, meals, or cooking")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="😋"):
        st.write(user_input)

    try:
        conversation_text = ""
        for message in st.session_state.messages:
            conversation_text += f"{message['role']}: {message['content']}\n"

        prompt = f"""
        You are a helpful food and recipe chatbot.
        Keep the conversation focused on meals, recipes, cooking, ingredients, and kitchen advice.
        Remember the previous conversation when responding.

        Conversation so far:
        {conversation_text}

        Respond to the user's latest message.
        """

        response = model.generate_content(prompt)
        bot_reply = response.text

    except Exception:
        bot_reply = "Sorry, something went wrong while generating a response. Please try again."

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant", avatar="images/chef.png"):
        st.write(bot_reply)

##############################################################################################################################



