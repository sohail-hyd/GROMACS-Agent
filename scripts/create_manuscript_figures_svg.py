import csv
from pathlib import Path

FIG = Path("figures")
FIG.mkdir(exist_ok=True)

def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))

def save_svg(path, content):
    path.write_text(content)
    print("Created:", path)

def bar_chart(path, labels, values, title, ylabel, ymax=10):
    width, height = 1000, 520
    left, right, top, bottom = 90, 40, 70, 110
    plot_w = width - left - right
    plot_h = height - top - bottom
    bar_w = plot_w / len(labels) * 0.65
    gap = plot_w / len(labels)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    svg.append('<rect width="100%" height="100%" fill="white"/>')
    svg.append(f'<text x="{width/2}" y="35" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>')
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="black"/>')
    svg.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="black"/>')
    svg.append(f'<text x="25" y="{top+plot_h/2}" transform="rotate(-90 25,{top+plot_h/2})" text-anchor="middle" font-size="16" font-family="Arial">{ylabel}</text>')

    for tick in range(0, int(ymax)+1, 2):
        y = top + plot_h - (tick / ymax) * plot_h
        svg.append(f'<line x1="{left-5}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="black"/>')
        svg.append(f'<text x="{left-10}" y="{y+5:.1f}" text-anchor="end" font-size="13" font-family="Arial">{tick}</text>')

    for i, (lab, val) in enumerate(zip(labels, values)):
        x = left + i * gap + (gap - bar_w) / 2
        h = (val / ymax) * plot_h
        y = top + plot_h - h
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="#4f81bd"/>')
        svg.append(f'<text x="{x+bar_w/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="13" font-family="Arial">{val:g}</text>')
        svg.append(f'<text x="{x+bar_w/2:.1f}" y="{top+plot_h+20}" text-anchor="end" font-size="12" font-family="Arial" transform="rotate(-45 {x+bar_w/2:.1f},{top+plot_h+20})">{lab}</text>')

    svg.append('</svg>')
    save_svg(path, "\n".join(svg))

def grouped_bar_chart(path, labels, values1, values2, title, ylabel, legend1, legend2, ymax=10):
    width, height = 1000, 540
    left, right, top, bottom = 90, 40, 80, 120
    plot_w = width - left - right
    plot_h = height - top - bottom
    gap = plot_w / len(labels)
    bar_w = gap * 0.28

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    svg.append('<rect width="100%" height="100%" fill="white"/>')
    svg.append(f'<text x="{width/2}" y="35" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>')
    svg.append(f'<rect x="{width-250}" y="55" width="18" height="18" fill="#4f81bd"/><text x="{width-225}" y="69" font-size="14" font-family="Arial">{legend1}</text>')
    svg.append(f'<rect x="{width-250}" y="80" width="18" height="18" fill="#c0504d"/><text x="{width-225}" y="94" font-size="14" font-family="Arial">{legend2}</text>')
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="black"/>')
    svg.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="black"/>')
    svg.append(f'<text x="25" y="{top+plot_h/2}" transform="rotate(-90 25,{top+plot_h/2})" text-anchor="middle" font-size="16" font-family="Arial">{ylabel}</text>')

    for tick in range(0, int(ymax)+1, 2):
        y = top + plot_h - (tick / ymax) * plot_h
        svg.append(f'<line x1="{left-5}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="black"/>')
        svg.append(f'<text x="{left-10}" y="{y+5:.1f}" text-anchor="end" font-size="13" font-family="Arial">{tick}</text>')

    for i, lab in enumerate(labels):
        center = left + i * gap + gap / 2
        for offset, val, color in [(-bar_w/2, values1[i], "#4f81bd"), (bar_w/2, values2[i], "#c0504d")]:
            x = center + offset - bar_w / 2
            h = (val / ymax) * plot_h
            y = top + plot_h - h
            svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{color}"/>')
            svg.append(f'<text x="{x+bar_w/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="12" font-family="Arial">{val:g}</text>')
        svg.append(f'<text x="{center:.1f}" y="{top+plot_h+22}" text-anchor="end" font-size="12" font-family="Arial" transform="rotate(-45 {center:.1f},{top+plot_h+22})">{lab}</text>')

    svg.append('</svg>')
    save_svg(path, "\n".join(svg))

def line_chart(path, labels, y1, y2, title, ylabel, legend1, legend2, ymax=10):
    width, height = 1000, 540
    left, right, top, bottom = 90, 40, 80, 120
    plot_w = width - left - right
    plot_h = height - top - bottom
    step = plot_w / max(1, len(labels)-1)

    def pt(i, v):
        x = left + i * step
        y = top + plot_h - (v / ymax) * plot_h
        return x, y

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    svg.append('<rect width="100%" height="100%" fill="white"/>')
    svg.append(f'<text x="{width/2}" y="35" text-anchor="middle" font-size="22" font-family="Arial">{title}</text>')
    svg.append(f'<rect x="{width-250}" y="55" width="18" height="18" fill="#4f81bd"/><text x="{width-225}" y="69" font-size="14" font-family="Arial">{legend1}</text>')
    svg.append(f'<rect x="{width-250}" y="80" width="18" height="18" fill="#c0504d"/><text x="{width-225}" y="94" font-size="14" font-family="Arial">{legend2}</text>')
    svg.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="black"/>')
    svg.append(f'<line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="black"/>')
    svg.append(f'<text x="25" y="{top+plot_h/2}" transform="rotate(-90 25,{top+plot_h/2})" text-anchor="middle" font-size="16" font-family="Arial">{ylabel}</text>')

    for tick in range(0, int(ymax)+1, 2):
        y = top + plot_h - (tick / ymax) * plot_h
        svg.append(f'<line x1="{left-5}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="black"/>')
        svg.append(f'<text x="{left-10}" y="{y+5:.1f}" text-anchor="end" font-size="13" font-family="Arial">{tick}</text>')

    for vals, color, dash in [(y1, "#4f81bd", ""), (y2, "#c0504d", " stroke-dasharray='6 4'")]:
        points = " ".join(f"{pt(i,v)[0]:.1f},{pt(i,v)[1]:.1f}" for i, v in enumerate(vals))
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"{dash}/>')
        for i, v in enumerate(vals):
            x, y = pt(i, v)
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')

    for i, lab in enumerate(labels):
        x, _ = pt(i, 0)
        svg.append(f'<text x="{x:.1f}" y="{top+plot_h+22}" text-anchor="end" font-size="12" font-family="Arial" transform="rotate(-45 {x:.1f},{top+plot_h+22})">{lab}</text>')

    svg.append('</svg>')
    save_svg(path, "\n".join(svg))

baseline = read_csv("results/tables/table_2_gscf_baseline_scores.csv")
task_ids = [r["task_id"] for r in baseline]
scores = [float(r["evaluator_score"]) for r in baseline]
bar_chart(FIG / "figure_1_gscf_baseline_scores.svg", task_ids, scores, "Manual LLM Baseline Performance on GSCF Workflow Tasks", "Evaluator score / 10")

geqs = read_csv("results/tables/table_3_geqs_evaluator_accuracy.csv")
geqs_ids = [r["task_id"] for r in geqs]
expert_scores = [float(r["expert_score"]) for r in geqs]
evaluator_scores = [float(r["evaluator_score"]) for r in geqs]
line_chart(FIG / "figure_2_geqs_expert_vs_evaluator.svg", geqs_ids, expert_scores, evaluator_scores, "Evaluator Agreement with Expert Scores on GEQS Error Cases", "Score / 10", "Expert score", "Evaluator score")

corr = read_csv("results/tables/table_4_correction_loop_improvement.csv")
corr_ids = [r["task_id"] for r in corr]
baseline_scores = [float(r["baseline_score"]) for r in corr]
best_scores = [float(r["best_corrected_score"]) for r in corr]
grouped_bar_chart(FIG / "figure_3_correction_loop_improvement.svg", corr_ids, baseline_scores, best_scores, "Evaluator-Guided Correction Improves Weaker Workflows", "Evaluator score / 10", "Baseline", "Best corrected")

abs_errors = [float(r["absolute_error"]) for r in geqs]
bar_chart(FIG / "figure_4_geqs_absolute_error.svg", geqs_ids, abs_errors, "Absolute Error Between Expert and Evaluator Scores", "Absolute error", ymax=1)

print("SVG manuscript figures complete.")
