from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pathlib import Path
import subprocess
import json
import html

BASE = Path(__file__).resolve().parent
RUNS = BASE / "agent" / "outputs" / "agent_runs"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GROMACS-Agent</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f8f9fb;
            color: #222;
        }}
        .box {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }}
        h1 {{
            color: #184e77;
        }}
        textarea {{
            width: 100%;
            height: 100px;
            font-size: 16px;
            padding: 12px;
        }}
        button {{
            background: #1d6f9f;
            color: white;
            border: none;
            padding: 12px 22px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
        }}
        pre {{
            background: #f1f3f5;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        .score {{
            font-size: 20px;
            font-weight: bold;
            color: #2b9348;
        }}
    </style>
</head>
<body>
    <div class="box">
        <h1>GROMACS-Agent</h1>
        <p>Retrieval-augmented LLM-style agent for automated GROMACS workflow generation, evaluation, and correction.</p>
        <form method="POST">
            <label><b>Enter GROMACS workflow task:</b></label><br><br>
            <textarea name="task">{task}</textarea><br><br>
            <button type="submit">Run GROMACS-Agent</button>
        </form>
    </div>

    {result}
</body>
</html>
"""

def latest_run():
    if not RUNS.exists():
        return None
    runs = sorted(RUNS.glob("*"), key=lambda p: p.stat().st_mtime)
    return runs[-1] if runs else None

def run_agent(task):
    before = set(RUNS.glob("*")) if RUNS.exists() else set()

    subprocess.run(
        ["python3", "agent/gromacs_agent.py", "--task", task],
        cwd=BASE,
        check=True
    )

    after = set(RUNS.glob("*"))
    new_runs = sorted(after - before, key=lambda p: p.stat().st_mtime)

    if new_runs:
        return new_runs[-1]
    return latest_run()

def render_result(run_dir):
    if run_dir is None:
        return ""

    final_workflow = (run_dir / "final_workflow.md").read_text() if (run_dir / "final_workflow.md").exists() else ""
    final_eval = json.loads((run_dir / "final_evaluation.json").read_text()) if (run_dir / "final_evaluation.json").exists() else {}
    retrieved = json.loads((run_dir / "retrieved_examples.json").read_text()) if (run_dir / "retrieved_examples.json").exists() else []

    retrieved_ids = [r.get("id", "unknown") for r in retrieved]

    return f"""
    <div class="box">
        <h2>Agent Result</h2>
        <p><b>Run folder:</b> {html.escape(str(run_dir))}</p>
        <p><b>Retrieved GSCF examples:</b> {html.escape(", ".join(retrieved_ids))}</p>
        <p class="score">Final evaluator score: {html.escape(str(final_eval.get("score", "NA")))} / 10</p>
        <p><b>Decision:</b> {html.escape(str(final_eval.get("decision", "NA")))}</p>
    </div>

    <div class="box">
        <h2>Final Workflow</h2>
        <pre>{html.escape(final_workflow)}</pre>
    </div>

    <div class="box">
        <h2>Final Evaluation JSON</h2>
        <pre>{html.escape(json.dumps(final_eval, indent=2))}</pre>
    </div>
    """

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        page = HTML_TEMPLATE.format(task="Generate a GROMACS workflow to calculate O-O RDF of pure water at 300 K", result="")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(page.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        data = parse_qs(body)
        task = data.get("task", [""])[0].strip()

        if not task:
            result = "<div class='box'><b>Please enter a task.</b></div>"
        else:
            try:
                run_dir = run_agent(task)
                result = render_result(run_dir)
            except Exception as e:
                result = f"<div class='box'><h2>Error</h2><pre>{html.escape(str(e))}</pre></div>"

        page = HTML_TEMPLATE.format(task=html.escape(task), result=result)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(page.encode())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 7860), Handler)
    print("GROMACS-Agent UI running at http://127.0.0.1:7860")
    server.serve_forever()
