<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt" alt="PyQt6" />
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/NLP-Powered-FF6F61?style=for-the-badge" alt="NLP" />
</p>

<h1 align="center">🧠 Z32 Nexus — Language Acquisition Accelerator</h1>

<p align="center">
  <strong>Desktop app for accelerated language learning</strong><br/>
  <em>Flashcards, grammar drills, analytics, CEFR analysis, and text-to-speech</em>
</p>

---

## 📖 About

**Z32 Nexus** is a PyQt6 desktop application designed to accelerate language acquisition through evidence-based learning techniques. It combines flashcard systems, grammar drills, journaling, analytics, CEFR-level analysis, text-to-speech, and mnemonic generation into a single powerful tool.

---

> **🖥️ Desktop Application:** Z32 Nexus is a local Python GUI application — not a web app. It requires **Python 3.10+** and the dependencies listed in `requirements.txt`. Just `pip install -r requirements.txt && python main.py` to get started.

---

## ✨ Features

- 📚 **Vocabulary System** — Smart flashcard engine with spaced repetition
- ✍️ **Grammar Drills** — Interactive grammar exercises with instant feedback
- 📓 **Learning Journal** — Track thoughts, progress, and reflections
- 📊 **Analytics Dashboard** — Visualize learning progress and patterns
- 🎯 **CEFR Analyzer** — Assess your text against CEFR levels (A1-C2)
- 🔊 **Text-to-Speech** — Hear pronunciations via pyttsx3
- 🌐 **Auto Translation** — Powered by deep-translator
- 🧩 **Mnemonic Engine** — Generate memory aids for vocabulary
- 📖 **Word Families** — Explore related words and collocations
- 🔒 **Single Instance** — Prevents multiple app instances via file locking
- 💾 **Persistent** — SQLAlchemy + SQLite for all data

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **GUI** | PyQt6 |
| **Database** | SQLAlchemy + SQLite |
| **Translation** | deep-translator |
| **TTS** | pyttsx3 |
| **Audio** | pygame |
| **Images** | Pillow |
| **Migrations** | Alembic |
| **Locking** | fasteners |

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/khaledwho0-ops/z32-nexus.git
cd z32-nexus

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 📁 Project Structure

```
z32-nexus/
├── main.py              # Application entry point
├── database.py          # SQLAlchemy models & database layer
├── workers.py           # Background worker threads
├── ui/
│   ├── main_window.py   # Main application window
│   ├── vocab_tab.py     # Vocabulary learning tab
│   ├── journal_tab.py   # Journal tab
│   ├── analytics_tab.py # Analytics dashboard
│   ├── grammar_drill.py # Grammar exercises
│   ├── flashcard_widget.py  # Flashcard component
│   ├── expert_tools.py  # Advanced analysis tools
│   └── styles.py        # Qt stylesheets
└── utils/
    ├── cefr_analyzer.py     # CEFR level assessment
    ├── vocab_processor.py   # Vocabulary processing
    ├── mnemonic_engine.py   # Memory aid generation
    ├── word_family.py       # Word family trees
    ├── collocations.py      # Collocation finder
    ├── study_optimizer.py   # Study scheduling
    └── config_manager.py    # Configuration
```

---

<p align="center">
  Built with ❤️ by <strong>Khalid Sayed</strong>
</p>
