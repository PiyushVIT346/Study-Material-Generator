📚 AI Study Material Generator (Flask + LangGraph + Groq)
This project generates comprehensive AI-powered study materials based on user-entered topics. It uses LangChain, LangGraph, and Groq's LLaMA 3 API to generate:

✅ Relevant subtopics
✅ Key concepts for each subtopic
✅ Descriptive explanations
✅ Concise summaries
✅ Multiple-choice quizzes

The Flask web app provides a simple interface to generate and view these study materials.

🚀 Features
Generate structured study material for any topic

Subtopics, key concepts, descriptions, summaries, and quizzes included

Clean web interface with:

Home page with project details

Topic input page

Result page with full material display

Server-side storage to handle large data (avoids session size limits)

Uses powerful LLM via Groq API for content generation

🛠️ Tech Stack
Python 3.8+

Flask (Web app framework)

LangChain + LangGraph (Workflow orchestration)

Groq API (LLaMA 3 based language generation)

HTML/CSS (Jinja2) for templating

📂 Project Structure
bash
Copy
Edit
├── app.py                  # Flask application
├── your_module_file.py     # StudyMaterialGenerator class (replace with actual filename)
├── templates/              # HTML templates
│   ├── home.html
│   ├── topic_input.html
│   └── result.html
├── .env                    # Groq API Key (Do not share publicly)
├── requirements.txt        # Required dependencies
└── README.md
🔧 Setup Instructions
1️⃣ Clone the Repository
bash
Copy
Edit
git clone https://github.com/your-username/ai-study-material-generator.git
cd ai-study-material-generator
2️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Configure Environment Variables
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
Visit http://127.0.0.1:5000 in your browser.

🖥️ Usage Workflow
Home page explains the project

Click Get Started

Enter your desired topic

Wait while AI generates study materials

View subtopics, key concepts, descriptions, summaries, and quizzes

⚡ Example
Input Topic: Machine Learning
Output: Subtopics like Supervised Learning, Unsupervised Learning, each with key concepts, detailed descriptions, concise summaries, and interactive quizzes.

📦 Requirements
Python 3.8+

Groq API Access

Internet connection for LLM API calls

🛡️ Important Notes
The project uses in-memory storage for temporary data. Restarting the server clears stored materials.

For production, integrate a database or Redis for persistent storage.

Keep your .env file secure and never expose your API keys publicly.

