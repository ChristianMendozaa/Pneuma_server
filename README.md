# Pneuma Intelligence - Backend Server

![FastAPI](https://img.shields.io/badge/FastAPI-0.95-009688?style=for-the-badge&logo=fastapi) ![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python) ![LangChain](https://img.shields.io/badge/LangChain-Integration-green?style=for-the-badge) ![E2B](https://img.shields.io/badge/E2B-Sandboxed_Execution-orange?style=for-the-badge) ![Groq](https://img.shields.io/badge/Groq-LPU_Inference-f55036?style=for-the-badge)

The powerful reasoning engine behind **Pneuma Intelligence**. This FastAPI server orchestrates an AI agent capable of writing and executing Python code to analyze data and generate visualizations.

## 🔗 Links
- **Live Demo**: [https://pneuma-frontend.vercel.app/]
- **Frontend Repository**: [https://github.com/ChristianMendozaa/Pneuma_frontend]
- **Server Repository**: [https://github.com/ChristianMendozaa/Pneuma_server]

## 🏗 Architecture & Workflow

1.  **Request Handling**: Receives user query and CSV URL from the Frontend.
2.  **Agent Reasoning**: Uses **LangChain** and **Groq (Llama 3.3)** to plan a data analysis strategy.
3.  **Code Generation**: The LLM writes a Python script using `pandas` to load the data, perform analysis, and structure the output.
4.  **Secure Execution**: The generated code is executed inside an **E2B Sandbox**. This limits the agent's access, ensuring safety and isolating the execution environment.
5.  **Output Parsing**: The script prints a JSON string containing the textual analysis and chart configurations, which the server parses and returns to the client.

## 🚀 Explainers: Why this Stack?

*   **E2B (Code Interpreter)**: Essential for safety. Allowing an LLM to generate and run code on a main server is a security risk. E2B provides ephemeral, cloud-based sandboxes where the code can run in isolation, access the internet to download the CSV, and then shut down immediately.
*   **Groq**: Chosen for speed. Data analysis requires complex chain-of-thought prompting. Groq's LPU inference engine delivers responses from Llama 3 models at record speeds, making the "chat" feel real-time even with code execution in the loop.
*   **FastAPI**: Provides a high-performance, async-ready Python web framework that easily handles concurrent requests and integrates well with the AI ecosystem.

## 🛠 Tech Stack

*   **Framework**: FastAPI
*   **LLM**: Meta Llama 3.3 (via Groq API)
*   **Orchestration**: LangChain
*   **Code Execution**: E2B Code Interpreter SDK
*   **Data Processing**: Pandas
*   **Environment Management**: Python venv / pip

## ✨ Key Features

*   **🐍 Python Code Interpretation**: Real-time generation and execution of Python code.
*   **🛡️ Sandboxed Security**: No local code execution; everything runs in a secure E2B container.
*   **📈 Smart Visualization**: Automatically determines the best chart type (Line vs Bar) based on data characteristics (time-series length, cardinality).
*   **⚡ High-Speed Inference**: Powered by Groq for near-instant reasoning.

## ⚙️ Setup & Installation

1.  **Clone the repository**:
    ```bash
    git clone [repo-url]
    cd Server_Pneuma
    ```

2.  **Create Virtual Environment**:
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file:
    ```env
    GROQ_API_KEY=your_groq_api_key
    E2B_API_KEY=your_e2b_api_key
    ```

5.  **Run the Server**:
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

## 💡 Challenges & Lessons Learned

*   **Prompt Engineering for JSON**: Getting the LLM to output *strict* JSON that can be parsed by the frontend was tricky. We solved this by using a robust system prompt with detailed JSON schema definitions and explicit instructions to avoid markdown formatting in the final output.
*   **Handling Pandas Objects**: The agent initially tried to serialize Pandas Series directly to JSON, which caused errors. We updated the system prompts to enforce converting all data aggregations to DataFrames and using `orient='records'` for consistent consumption by the frontend.
*   **Legacy Library Interfaces**: We encountered issues with `e2b_code_interpreter` where older patterns (`CodeInterpreter(api_key=...)`) were deprecated. We had to migrate to `Sandbox.create()` to align with the latest SDK best practices.