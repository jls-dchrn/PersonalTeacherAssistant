# 🧑‍🏫 Personal Teacher Assistant

---
Persional Teacher Assistant (PTA) is a LLM assistat designed to adapt to each person's **learning pace**.
It will help you either learn a subject or complete your homework by giving you **useful hints**.
The **more you use** PTA, the **more relevant** its teaching methods will become.
What make PTA special is that the assistant analyse how you react to the subject you're learning, as well as your previous interactions, to find the  **best way to teach you**. 


---
### Context

This project was developped by *Jules Duchiron*, *Nikolaj Meineche*, *Hayato Kimura*, and *Takumi Fujimoto*, students of **Keio University** as a project for the **Machine Intelligence** class.

It was recently updated by *Jules Duchiron* recently, changing the frontend to **Gradio**.

---

## 📁 Project Structure



.
├── `pyproject.toml`  
├── `README.md`              
└── `src/`  
&emsp; └── `personalteacherassistant/`  
&emsp;&emsp;├── `app.py`: Front app with Gradio  
&emsp;&emsp;├── `auth.py`: Authentication system  
&emsp;&emsp;├── `cost.py`: Cost tracker per interaction  
&emsp;&emsp;└── `model.py`: Interaction with the LLM  


---

## 🔧 Installation

1. **Clone this repository**

```bash
git clone https://github.com/jls-dchrn/PersonalTeacherAssistant.git
cd PersonalTeacherAssistant
```

2. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  
```

3. **Install dependencies**

```bash
pip install -e .
```


---

## 🔑 Environment Setup

Create a `.env` file at the root of the project with your OpenAI API key:

```dotenv
OPENAI_API_KEY=enter_your_key
```

---

## 🧠 Run the Assistant

Run the library directly:
```bash
pta
```
Or use the full path:

```bash
python3 -m src.personalteacherassistant.app
```

Visit the local URL printed in the terminal [http://127.0.0.1:7860] and log in using your created account.

---



## 📄 License

MIT License — you're free to use, modify, and distribute under the terms of the license.


