# TVYN_Supermarket_Chatbot
A chatbot built using LangChain and LLaMA 3, designed to help users explore available products in a supermarket. It remembers users' disliked products and filters them out from the available product list. It also answers shop-related questions, like store name, location, and global supermarket trends.

💡 Features:
🛒 Product Availability Check
Users can ask “What products are available?” and get real-time listings with quantity and price.

👎 Dislike Preferences
Users can say things like “I dislike milk,” and the chatbot will remember and filter those products from suggestions.

📊 Excel/Sheet Integration
Reads product details (name, quantity, price) from Excel or Google Sheets for dynamic interaction.

🧠 LLaMA 3 (via LangChain)
Uses a local LLaMA 3 model to respond intelligently to user queries, including shop-related and global supermarket trends (non-realtime).

💬 Natural Language Interaction
Friendly chatbot interface where users can type in full questions.

🌐 Global Shop Knowledge
Can answer general supermarket-related knowledge questions using LLaMA 3’s language understanding.

🚫 Offline Mode
No internet/API dependency – runs fully on local models.
