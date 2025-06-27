# 📚 AI Study Material Generator (Flask + LangGraph + Groq)

This project generates AI-powered, structured study material based on user-entered topics using **LangChain**, **LangGraph**, and **Groq's LLaMA 3 API**. 

The generated content includes:
- ✅ Relevant Subtopics  
- ✅ Key Concepts  
- ✅ Descriptions  
- ✅ Summaries  
- ✅ Multiple-Choice Quizzes  

The project provides a simple web interface built with Flask to interact with the system.

---

## 🚀 Features

- Generate study material for any academic topic
- AI-generated subtopics and key concepts
- Educational descriptions and concise summaries
- Interactive quiz generation
- User-friendly web interface
- Server-side storage to handle large data outputs

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Flask** - Web Application
- **LangChain** & **LangGraph** - Workflow orchestration
- **Groq API** - LLaMA 3 based AI content generation
- **HTML/Jinja2** - Frontend templates

---

## 📂 Project Structure

├── app.py # Flask application
├── your_module_file.py # StudyMaterialGenerator logic (replace with your filename)
├── templates/ # HTML templates
│ ├── home.html
│ ├── topic_input.html
│ └── result.html
├── .env # Environment variables (Groq API Key)
├── requirements.txt # Python dependencies
└── README.md # Project documentation



---

## 🔧 Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ai-study-material-generator.git
cd ai-study-material-generator
2️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Add Environment Variables
Create a .env file in the project root:

ini
Copy
Edit
GROQ_API_KEY=your_actual_groq_api_key_here
4️⃣ Run the Application
bash
Copy
Edit
python app.py
Open your browser and visit:

cpp
Copy
Edit
http://127.0.0.1:5000
🖥️ Usage Workflow
Visit the Home Page for app introduction

Click Get Started

Enter your desired topic

The system generates subtopics, key concepts, descriptions, summaries, and quizzes

View and interact with the generated study material
