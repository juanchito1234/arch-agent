# Architecture Recommendation Agent

A Streamlit application that uses a Groq LLM to generate software architecture recommendations (including interactive Mermaid diagrams).

## Prerequisites

- **Python 3.10+**
- **Git** (optional, for cloning the repo)
- A **Groq API key** (sign up at https://groq.com/).

## Setup

1. **Clone the repository** (or open the existing folder):
   ```bash
   git clone <repo-url>
   cd arch-agent
   ```

2. **Create a virtual environment** and activate it:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(If a `requirements.txt` file is not present, install the core packages manually:)*
   ```bash
   pip install streamlit groq diagram
   ```

4. **Configure the Groq API key**:
   - Create a `.env` file in the project root (or set the environment variable directly) with the line:
     ```
     GROQ_API_KEY=your_api_key_here
     ```
   - Or you can paste the key in the sidebar of the app.

## Running the Application

From the project root, start the Streamlit app:
```bash
.venv\Scripts\streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501` (or the URL shown in the console).

## Usage

- Enter your project context or user stories in the chat input box.
- The assistant will generate architecture recommendations, optionally with Mermaid diagrams.
- Use the sidebar to switch models, adjust tokens, temperature, or start a new conversation.

## Development

- The code is organized into several modules:
  - `app.py` – Streamlit UI and session handling.
  - `agent/` – LLM wrapper and prompt definitions.
  - `chat/` – Persistence of conversation history.
  - `diagram/` – Rendering and parsing of Mermaid diagrams.
- To modify the behavior, edit the corresponding Python files and reload the Streamlit page.

## License

This project is provided for educational purposes. Feel free to adapt and extend it.
