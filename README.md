# 🤖 Multi-Domain Question-Answering Chatbot 🚀  

Welcome to the **Multi-Domain Q&A Chatbot**! This chatbot provides an intuitive way to upload files, extract knowledge, and ask questions, all while maintaining a user-friendly experience.  

---

## ✨ Features  

1. **👤 User Profile Management**:  
   - Collects the user's **name** and **email** to create a personalized JSON file.  
   - Stores user information for better interaction and future use.  

2. **📂 File Uploads**:  
   - Supports file uploads in **three domains** (specific domains, e.g., Finance, Healthcare, Education).  
   - Processes and extracts data from the uploaded files.  

3. **🧠 ChromaDB Vector Storage**:  
   - Converts file data into embeddings and saves it in a **ChromaDB** database.  
   - Enables fast and efficient knowledge retrieval for Q&A.  

4. **❓ Smart Question Answering**:  
   - Users can ask questions related to the uploaded files.  
   - Provides detailed answers, including **page numbers** and **file names** for reference.  

5. **📜 General Chat Capabilities**:  
   - Engages with users in a friendly manner when questions are unrelated to the files (e.g., "Hi!" or "Good morning!").  
   - Responds with `"I don't know the answer to that based on the document."` if no context is available.  

---

## 🛠️ How It Works  

1. **User Onboarding**:  
   - The chatbot takes the user's **name** and **email** and saves it in a JSON file for personalization.  

2. **File Upload & Processing**:  
   - Users upload files in the supported domains.  
   - The chatbot processes the files, extracts information, and stores embeddings in a ChromaDB database.  

3. **Ask Questions**:  
   - Users ask questions about the uploaded files.  
   - The chatbot retrieves relevant information from the database and provides detailed answers with references (page number and file name).  

4. **General Chat**:  
   - For non-file-related questions, the chatbot engages in polite conversation or provides a fallback response.

---

## 📦 Installation  

1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/your-username/multi-domain-chatbot.git
   cd multi-domain-chatbot
   ```

2. **Install Dependencies**:  
   Ensure you have Python installed, then run:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up ChromaDB**:  
   - Install and configure ChromaDB as your vector storage solution.  

4. **Run the Chatbot**:  
   ```bash
   python app.py
   ```

---

## 💻 Example Usage  

1. **Step 1**: Provide your name and email.  
   ```
   User: John.
   email: john@gmail.com
   ```

2. **Step 2**: Upload files.  
   ```
   User: Upload a file (e.g., finance_report.pdf).
   Chatbot: Your file 'finance_report.pdf' has been processed and stored.
   ```

3. **Step 3**: Ask questions.  
   ```
   User: What is the revenue in Q3?
   Chatbot: The revenue in Q3 is $1,000,000 (Page 5, finance_report.pdf).
   ```

4. **Step 4**: General conversation.  
   ```
   User: Good morning!
   Chatbot: Good morning! How can I assist you today?
   ```

---

## 🎯 Key Benefits  

- 🔍 **Accurate References**: Answers include **page numbers** and **file names** for transparency.  
- 🌐 **Multi-Domain Support**: Handles files from multiple domains seamlessly.  
- ⚡ **Fast Retrieval**: Leverages ChromaDB for quick and accurate knowledge extraction.  
- 🤝 **User-Friendly**: Saves user details for personalization and remembers preferences.  

---

## 🤝 Contributions  

We welcome contributions! To get started:  
1. Fork the repository 🍴  
2. Create a new branch 🚀  
3. Submit a pull request 📬  

---
