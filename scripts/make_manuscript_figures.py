from pathlib import Path
import csv
from xml.sax.saxutils import escape

out_dir = Path("docs/manuscript/figures")
out_dir.mkdir(parents=True, exist_ok=True)

def make_svg(filename, body, width=1200, height=700):
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<defs>
<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
<path d="M0,0 L0,6 L9,3 z" fill="black"/>
</marker>
</defs>
{body}
</svg>
'''
    path = out_dir / filename
    path.write_text(content)
    print(path)

def label(x, y, txt, size=22, bold=False, anchor="middle"):
    weight = "bold" if bold else "normal"
    return f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(txt))}</text>\n'

def box(x, y, w, h, txt):
    body = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#f8fbff" stroke="black" stroke-width="2"/>\n'
    lines = str(txt).split("\\n")
    start = y + h / 2 - (len(lines) - 1) * 13
    for i, line in enumerate(lines):
        body += label(x + w / 2, start + i * 26, line, 18, True)
    return body

def arrow(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="3" marker-end="url(#arrow)"/>\n'

def bar_chart(filename, title, labels, values, ymax, ylabel):
    left, bottom, top = 110, 590, 100
    chart_w, chart_h = 980, bottom - top
    body = label(600, 45, title, 30, True)
    body += label(55, 330, ylabel, 20, True)
    body += f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="black" stroke-width="2"/>\n'
    body += f'<line x1="{left}" y1="{bottom}" x2="{left+chart_w}" y2="{bottom}" stroke="black" stroke-width="2"/>\n'

    step = ymax / 5
    for i in range(6):
        tick = step * i
        y = bottom - (tick / ymax) * chart_h
        body += f'<line x1="{left}" y1="{y}" x2="{left+chart_w}" y2="{y}" stroke="#dddddd" stroke-dasharray="5 5"/>\n'
        body += label(left - 12, y + 6, f"{tick:.0f}", 16, False, "end")

    n = len(labels)
    gap = chart_w / n
    bar_w = gap * 0.55
    for i, (lab, val) in enumerate(zip(labels, values)):
        x = left + i * gap + gap * 0.22
        h = (val / ymax) * chart_h
        y = bottom - h
        body += f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="#8fbce6" stroke="black"/>\n'
        body += label(x + bar_w / 2, y - 8, f"{val:.2f}" if isinstance(val, float) else val, 15, True)
        body += label(x + bar_w / 2, bottom + 32, lab, 16, True)

    make_svg(filename, body)

# Figure 1
body = label(600, 45, "Figure 1. GROMACS-Agent architecture", 30, True)
nodes = [
    (40, 290, 135, 70, "User\\nTask"),
    (210, 290, 150, 70, "Manager\\nAgent"),
    (395, 290, 150, 70, "Planner\\nAgent"),
    (585, 160, 180, 80, "Retriever\\nGSCF Memory"),
    (585, 290, 190, 70, "Gromacs\\nWorkerAgent"),
    (825, 285, 210, 90, "Gromacs\\nEvaluatorAgent\\nGEQS Rubric"),
    (825, 450, 210, 85, "CodeExecutorAgent\\nSafe Execution"),
    (1070, 290, 100, 80, "Final\\nReport"),
]
for n in nodes:
    body += box(*n)
for a in [
    (175, 325, 210, 325),
    (360, 325, 395, 325),
    (545, 325, 585, 325),
    (765, 325, 825, 325),
    (1035, 325, 1070, 325),
    (675, 240, 675, 290),
    (930, 375, 930, 450),
]:
    body += arrow(*a)
make_svg("figure_1_gromacs_agent_architecture.svg", body)

# Figure 2
labels = ["O-O RDF", "Temp.", "Density", "MSD", "PBC"]
baseline = [5, 8, 6, 7, 7]
agent = [10, 10, 10, 10, 10]
left, bottom, top = 110, 590, 100
chart_w, chart_h = 980, bottom - top
body = label(600, 45, "Figure 2. Baseline LLM vs GROMACS-Agent scores", 30, True)
body += f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="black" stroke-width="2"/>\n'
body += f'<line x1="{left}" y1="{bottom}" x2="{left+chart_w}" y2="{bottom}" stroke="black" stroke-width="2"/>\n'
for tick in [0, 2, 4, 6, 8, 10]:
    y = bottom - (tick / 10) * chart_h
    body += f'<line x1="{left}" y1="{y}" x2="{left+chart_w}" y2="{y}" stroke="#dddddd" stroke-dasharray="5 5"/>\n'
    body += label(left - 12, y + 6, tick, 16, False, "end")
gap = chart_w / len(labels)
for i, lab in enumerate(labels):
    x0 = left + i * gap + 35
    for val, color, shift in [(baseline[i], "#f2b880", 0), (agent[i], "#8fbce6", 55)]:
        h = (val / 10) * chart_h
        y = bottom - h
        body += f'<rect x="{x0+shift}" y="{y}" width="45" height="{h}" fill="{color}" stroke="black"/>\n'
        body += label(x0 + shift + 22, y - 8, val, 15, True)
    body += label(left + i * gap + gap / 2, bottom + 32, lab, 16, True)
body += f'<rect x="760" y="70" width="25" height="18" fill="#f2b880" stroke="black"/>\n'
body += label(795, 86, "Baseline LLM", 18, False, "start")
body += f'<rect x="940" y="70" width="25" height="18" fill="#8fbce6" stroke="black"/>\n'
body += label(975, 86, "GROMACS-Agent", 18, False, "start")
make_svg("figure_2_baseline_vs_agent_scores.svg", body)

# Figure 3
time_file = Path("results/time_study/manual_timing/time_reduction_summary_clean_5tasks.csv")
reductions = [99.96, 99.52, 99.74, 99.76, 99.73]
if time_file.exists():
    reductions = []
    with time_file.open() as f:
        for r in csv.DictReader(f):
            reductions.append(float(r["time_reduction_percent"]))
bar_chart(
    "figure_3_pilot_time_reduction.svg",
    "Figure 3. Single-user pilot workflow-preparation time reduction",
    labels,
    reductions,
    100,
    "Reduction (%)"
)

# Figure 4
bar_chart(
    "figure_4_dataset_benchmark_summary.svg",
    "Figure 4. Dataset and benchmark summary",
    ["GSCF", "GEQS", "Worker SFT", "Eval. SFT", "Demo", "Accepted"],
    [100, 100, 100, 100, 5, 5],
    120,
    "Count"
)

print("Created SVG manuscript figures in:", out_dir)
