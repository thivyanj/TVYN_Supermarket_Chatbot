import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama

# Constants
PRODUCT_FILE = "products.xlsx"
DISLIKES_FILE = "user_dislikes.json"
CHAT_LOG_FILE = "chat_log.txt"

# Load Products from Excel
def load_products():
    if os.path.exists(PRODUCT_FILE):
        df = pd.read_excel(PRODUCT_FILE)
        return df.fillna("").to_dict(orient="records")
    return []

# Load Dislikes from file
def load_dislikes():
    if os.path.exists(DISLIKES_FILE):
        with open(DISLIKES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Save Dislikes to file
def save_dislikes(data):
    with open(DISLIKES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# Save Chat Logs to file
def log_chat(user, bot):
    with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}]\n🧑 User: {user}\n🤖 Bot: {bot}\n\n")

# Analyze popular products based on chat logs
def get_most_asked():
    if not os.path.exists(CHAT_LOG_FILE):
        return []
    with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    keywords = {}
    for line in lines:
        if "User:" in line:
            for word in line.split():
                word = word.strip().lower().strip(".,!?")
                if len(word) > 3 and word.isalpha():
                    keywords[word] = keywords.get(word, 0) + 1
    return sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]

# Chatbot response based on user input
def answer_query(user_input, product_data, dislikes):
    lowered = user_input.lower()

    # Handle dislikes
    if "i don't like" in lowered or "i do not like" in lowered:
        disliked_items = [w.strip() for w in lowered.replace("i don't like", "").replace("i do not like", "").split(",")]
        for item in disliked_items:
            if item:
                dislikes[item] = True
        save_dislikes(dislikes)
        return f"Got it! I'll remember you don't like {', '.join(disliked_items)}."

    # Handle product availability queries
    if "available" in lowered or "what products" in lowered or "show products" in lowered:
        # Filter out disliked products
        available_products = [p for p in product_data if p["Product Name"].lower() not in dislikes]
        if available_products:
            response = "Currently available products:\n"
            for p in available_products:
                response += f"- {p['Product Name']} | Quantity: {p['Quantity']} | Price: {p['Price']}\n"
            return response
        else:
            return "No products available currently."

    if "how many" in lowered:
        total = sum(int(p["Quantity"]) for p in product_data if str(p["Quantity"]).isdigit())
        return f"We have approximately {total} products in stock."

    return "Hello! I'm TVYN Assistant. Please ask about available products or tell me what you dislike."

# Streamlit UI Setup
st.set_page_config(page_title="TVYN Supermarket Chatbot", page_icon="🛒")
st.title("🛒 TVYN Supermarket Chatbot")
st.markdown("Ask about available products, or say what you dislike (e.g., 'I dislike milk').")

input_txt = st.text_input("Your message")

# Load data from Excel and Dislikes file
products = load_products()
dislikes = load_dislikes()

# Initialize session state for memory (multi-turn conversation)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# LangChain setup with LLaMA
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful supermarket assistant named TVYN."),
    ("user", "user query:{query}")
])
llm = Ollama(model="llama3")  # Use the LLaMA model
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Handle user input and generate response using LLaMA
if input_txt:
    # Get the response from the LangChain chain
    response = answer_query(input_txt, products, dislikes)

    # Append to chat history
    st.session_state.chat_history.append(("user", input_txt))
    st.session_state.chat_history.append(("bot", response))

    # Log the conversation to file
    log_chat(input_txt, response)

# Display chat history
for sender, msg in st.session_state.chat_history:
    with st.chat_message(name=sender):
        st.markdown(msg)

# Show popular product words based on chat history
if st.button("📊 Show Most Asked Items"):
    popular = get_most_asked()
    st.write("Top keywords from users:")
    for word, count in popular:
        st.write(f"{word.capitalize()} ({count} times)")

# Option to download chat logs
with st.sidebar:
    st.subheader("🗂 Download Logs")
    if os.path.exists(CHAT_LOG_FILE):
        with open(CHAT_LOG_FILE, "r", encoding="utf-8") as f:
            chat_content = f.read()
        st.download_button("Download Chat (.txt)", chat_content, file_name="chat_log.txt")

# Optional: Avatar setup for chatbot is skipped for simplicity, can be added via Streamlit's chat layout.
