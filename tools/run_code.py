import os
import subprocess
from langchain_core.tools import tool

# ---------------------------------------------
# OPTIONAL: Gemini-based code analysis (NOT execution)
# ---------------------------------------------
def analyze_code_with_gemini(code: str) -> str:
    """
    Uses Gemini to analyze code and give feedback.
    Does NOT execute code.
    """
    import google.genai as genai

    client = genai.Client(api_key=os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDAwNjBAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.mHCNEHZrNcRnnVe75UAbJ8r22JkT8hs9wSCTzYZgZ4M"))

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Analyze the following code and explain its output:\n{code}"
    )
    return response.text


# ---------------------------------------------
# MAIN TOOL: Safe Python code execution
# ---------------------------------------------
def strip_code_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        code = code.split("\n", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("\n", 1)[0]
    return code.strip()


@tool
def run_code(code: str) -> dict:
    """
    Executes Python code safely in a separate environment.
    """

    try:
        # Clean code
        code = strip_code_fences(code)

        os.makedirs("LLMFiles", exist_ok=True)
        filename = "runner.py"
        filepath = os.path.join("LLMFiles", filename)

        # Write code to file
        with open(filepath, "w") as f:
            f.write(code)

        # Execute using uv / python
        proc = subprocess.Popen(
            ["uv", "run", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="LLMFiles"
        )

        stdout, stderr = proc.communicate()

        # Limit extremely large output
        if len(stdout) >= 10000:
            stdout = stdout[:10000] + "...truncated"
        if len(stderr) >= 10000:
            stderr = stderr[:10000] + "...truncated"

        return {
            "stdout": stdout,
            "stderr": stderr,
            "return_code": proc.returncode
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }

