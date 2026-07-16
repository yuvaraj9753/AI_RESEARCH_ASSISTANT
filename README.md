# 🔬 AI Research Assistant

An AI-powered Research Assistant that automates the research process using Large Language Models (LLMs). The application searches the web for relevant information, extracts key insights, generates a structured research report, provides source citations, and supports contextual follow-up questions.

This project demonstrates the practical implementation of Generative AI, AI Agents, Prompt Engineering, LLM orchestration, and intelligent research automation.

---

# ✨ Features

- 🌐 AI-powered Web Search using Tavily API
- 🤖 Research Analysis using Groq (Llama 3.3 70B)
- 📊 Automatic Key Insight Extraction
- 📝 AI-generated Research Summary
- 📖 Structured Research Report
  - Introduction
  - Key Points
  - Conclusion
- 🔗 Source Citations
- 🧭 Related Research Topics
- 💬 Context-Aware Follow-up Chat
- ⚙️ Research Type Selection
  - General
  - Technical
  - Academic
  - Market
- 🔍 Research Depth Selection
  - Quick
  - Standard
  - Deep
- 📈 Research Statistics
  - Sources Used
  - Research Type
  - Research Depth
  - Time Taken
  - LLM Model
  - Confidence Score

---

# 🏗️ Architecture

```
                      User
                        │
                        ▼
               Streamlit Frontend
                        │
                        ▼
        Research Configuration
 (Topic + Research Type + Research Depth)
                        │
                        ▼
              Tavily Web Search
                        │
                        ▼
            Retrieved Web Content
                        │
                        ▼
      Research Agent (Groq Llama 3.3)
                        │
                        ▼
        Insights + Research Summary
                        │
                        ▼
     Summarizer Agent (Groq Llama 3.3)
                        │
                        ▼
      Introduction
      Key Points
      Conclusion
      Related Topics
                        │
                        ▼
             Streamlit Interface
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
   Source Citations            Follow-up Chat
```

---

# ⚙️ Workflow

### Step 1
Enter a research topic.

### Step 2
Select:

- Research Type
- Research Depth

### Step 3
The application searches the web using the Tavily Search API.

### Step 4
The Research Agent analyzes the retrieved information.

### Step 5
The LLM extracts:

- Key Insights
- Research Summary

### Step 6
The Summarizer Agent generates:

- Introduction
- Key Points
- Conclusion
- Related Topics

### Step 7
The application displays:

- Research Statistics
- Structured Research Report
- Source Citations

### Step 8
Users can ask contextual follow-up questions based on the generated research.

---

# 🛠️ Tech Stack

### Programming Language

- Python

### Frontend

- Streamlit

### LLM

- Groq API
- Llama 3.3 70B Versatile

### Web Search

- Tavily Search API

### AI Technologies

- Large Language Models (LLMs)
- AI Agents
- Prompt Engineering
- Research Summarization

### Utilities

- python-dotenv

---

# 📁 Project Structure

```
AI_RESEARCH_ASSISTANT/

│
├── agents/
│   ├── researcher.py
│   ├── summarizer.py
│   └── chat.py
│
├── prompts/
│   ├── research_prompt.py
│   ├── summary_prompt.py
│   └── chat_prompt.py
│
├── services/
│   ├── groq_service.py
│   └── search_service.py
│
├── utils/
│   └── helpers.py
│
├── app.py
├── requirements.txt
├── .env
└── README.md
```

---

# 🔍 Research Types

| Type | Description |
|------|-------------|
| General | Easy-to-understand explanation |
| Technical | Architecture, Working, Advantages, Limitations |
| Academic | Formal research-oriented explanation |
| Market | Industry trends, business applications, and market insights |

---

# 📚 Research Depth

| Depth | Web Sources |
|--------|------------|
| Quick | 3 Sources |
| Standard | 5 Sources |
| Deep | 10 Sources |

---

# 📈 Research Statistics

The application automatically tracks:

- Research Type
- Research Depth
- Sources Used
- Time Taken
- LLM Model
- Confidence Score

---

# 💬 Follow-up Chat

The assistant supports contextual follow-up questions using the generated research report, allowing users to explore the topic further without performing a new search.

---

# 🚀 Future Improvements

- Multi-Agent Workflow
- Multi-LLM Support
- Research History
- Authentication
- Semantic Scholar Integration
- arXiv Integration
- Interactive Visualizations
- Research Comparison
- Export to DOCX
- Save Research Sessions

---

# 🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Large Language Models (LLMs)
- AI Agents
- Prompt Engineering
- AI-powered Web Search
- Research Automation
- Information Extraction
- AI Summarization
- Context-Aware Question Answering
- Streamlit Application Development

---

# 👨‍💻 Author

**Yuvaraj Kushwaha**

B.Tech Computer Science Engineering

Aspiring AI Engineer | Generative AI Engineer | LLM Application Developer

---

## ⭐ If you found this project useful, consider giving it a Star!