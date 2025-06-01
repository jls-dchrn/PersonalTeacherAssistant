# 🧑‍🏫 Personal Teacher Assistant

A secure, modular, and extendable local assistant powered by LLMs (OpenAI or compatible) using a web interface built with **Gradio**.  
This assistant includes authentication, session management, and can be easily extended with features like cost tracking and personalized prompts.

---

## 🚀 Features

- 🔐 Secure user login with hashed passwords (bcrypt)
- 🧠 LLM backend (OpenAI GPT or compatible API)
- 💬 Chat interface with memory (Gradio UI)
- ✅ Clean modular architecture (auth, model, app)
- 📊 Optional: Track cost per user/message

---

## 📁 Project Structure

```

.
├── pyproject.toml               # Project dependencies & metadata
├── README.md                    # You are here
└── src/
└── personalteacherassistant/
├── app.py              # Main app (Gradio UI)
├── auth.py             # Authentication system (bcrypt + session)
├── cost.py             # (Optional) Cost tracker per interaction
└── model.py            # GPT wrapper class

```

---

## ⚙️ Requirements

- Python 3.8+
- `pip` or `poetry`
- OpenAI API key (or compatible endpoint)

---

## 🔧 Installation

1. **Clone the repo**

```bash
git clone https://github.com/your-username/personal-teacher-assistant.git
cd personal-teacher-assistant
```

2. **Create a virtual environment (optional but recommended)**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

Using `pip`:

```bash
pip install -e .
```

Or using `poetry`:

```bash
poetry install
```

---

## 🔑 Environment Setup

Create a `.env` file at the root of the project with your OpenAI API key:

```dotenv
OPENAI_API_KEY=sk-your-key-here
```

---

## 🧠 Run the Assistant

```bash
python src/personalteacherassistant/app.py
```

Visit the local URL printed in the terminal [http://127.0.0.1:7860] and log in using your created account.

---

## ✏️ Customization

* **Model customization**: change the OpenAI model in `model.py`
* **UI/logic separation**: extend `app.py` or wrap into a class-based Gradio app
* **Add cost tracking**: extend `cost.py` and integrate with message hooks

---

## 📦 Packaging (pyproject.toml)

To install this project as a Python package:

```bash
pip install -e .
```

---

## 📄 License

MIT License — you're free to use, modify, and distribute under the terms of the license.

---

## 🤝 Contributing

PRs welcome! This project is modular and meant to be extended (roles, admin UI, analytics, vector memory...).

---
