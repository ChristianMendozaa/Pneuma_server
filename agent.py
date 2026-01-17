import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


from e2b_code_interpreter import Sandbox

# We will use a custom approach instead of the standard agent to ensure strict JSON output 
# and handle the specific flow of "Download -> Analyze -> Return Data"

def analyze_data(message: str, csv_url: str) -> dict:
    
    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0
    )

    # 1. Plan and Generate Code step
    # We ask the LLM to generate Python code that:
    # 1. Loads the CSV from the URL
    # 2. Performs the analysis requested
    # 3. Prints the result as a JSON string
    
    system_prompt = """You are a Data Analysis Agent. You have access to a python environment.
    The user will provide a CSV URL and a query.
    
    Your goal is to write a Python script that:
    1. Loads the data using pandas from the provided URL.
    2. Performs the analysis to answer the user's question.
    3. Prepares the data for visualization if applicable.
    4. PRINTS the final result as a strict JSON object (and NOTHING else).

    The JSON output must have this structure:
    {{
        "text": "Analysis summary or answer to the question",
        "charts": [
            {{
                "type": "bar" | "line" | "pie" | "area",
                "title": "Descriptive Chart Title",
                "xLabel": "Label for X Axis (e.g. Year)",
                "yLabel": "Label for Y Axis (e.g. Total Sales)",
                "data": [{{"x_col": "val", "y_col": 10}}, ...],
                "xKey": "key_for_x_axis",
                "yKey": "key_for_y_axis"
            }},
            ...
        ]
    }}
    
    If no charts are needed, set "charts" to [].
    
    IMPORTANT TIPS:
    - When aggregating data (e.g., groupby, sum), the result might be a pandas Series.
    - `Series.to_dict()` DOES NOT accept `orient='records'`.
    - ALWAYS convert Series to DataFrame using `.reset_index()` (preferred) or `.to_frame()` BEFORE converting to dict for charts.
    - Example: `df.groupby('col').sum()['val'].reset_index().to_dict(orient='records')`

    CHART SELECTION RULES:
    1. If the X-axis represents TIME (Years, Months, Days, Dates) AND there are more than 15 data points -> MUST use "line" or "area" chart. Bar charts are bad for long time series.
    2. If the data is Categorical or there are few time points (<= 15) -> Use "bar" chart.
    3. Use "pie" only for part-to-whole comparisons with few categories (< 8).
    
    IMPORTANT: The Python script must print ONLY the JSON string to stdout at the end.
    Do not generate images (png/jpg). We need raw data for the frontend to render.
    """

    user_prompt = f"""
    CSV URL: {csv_url}
    User Query: {message}
    
    Write the python code to solve this.
    """

    # We use a simple chain here to get the code, then execute it.
    # A full agent loop might be better for error correction, but for speed/simplicity:
    # We'll use the E2B Code Interpreter directly with the LLM's generated code.

    code_generation_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])

    chain = code_generation_prompt | llm
    
    # Get the code from LLM
    # We might need to instruct it to put code in a markdown block or just raw text.
    # Let's ask for raw python code or parse it.
    
    response = chain.invoke({})
    code = response.content
    
    # Clean up code blocks if present
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()

    print(f"Executing code:\n{code}")

    # Execute in E2B
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)
        
        if execution.error:
            return {
                "text": f"Error executing analysis code: {execution.error.name}: {execution.error.value}\nTraceback: {execution.error.traceback}",
                "charts": []
            }
        
        # Capture stdout (print statements)
        output = "".join(execution.logs.stdout)
        
        if not output:
             return {
                "text": "The analysis ran but produced no output. Please check if the code prints the JSON.",
                "charts": []
            }

        try:
            # Attempt to parse the JSON output from the script
            result = json.loads(output)
            return result
        except json.JSONDecodeError:
             return {
                "text": f"Failed to parse analysis results. Raw output: {output}",
                "charts": []
            }
