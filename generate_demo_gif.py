"""
Generates a modern, high-resolution animated terminal GIF demonstrating
the Self-Healing Data Pipeline in action.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH = 840
HEIGHT = 580
BG_COLOR = (15, 23, 42)        # #0F172A
TITLE_BG = (30, 41, 59)        # #1E293B
BORDER_COLOR = (51, 65, 85)    # #334155

# Text colors
WHITE = (248, 250, 252)
GRAY = (148, 163, 184)
CYAN = (56, 189, 248)
GREEN = (52, 211, 153)
YELLOW = (251, 191, 36)
PURPLE = (129, 140, 248)
RED = (239, 68, 68)

def draw_window_frame(draw, font_small):
    # Terminal outer border
    draw.rounded_rectangle([0, 0, WIDTH - 1, HEIGHT - 1], radius=12, fill=BG_COLOR, outline=BORDER_COLOR, width=2)
    # Title bar
    draw.rounded_rectangle([0, 0, WIDTH - 1, 38], radius=12, fill=TITLE_BG)
    draw.rectangle([0, 26, WIDTH - 1, 38], fill=TITLE_BG)
    draw.line([(0, 38), (WIDTH - 1, 38)], fill=BORDER_COLOR, width=1)
    
    # Window action buttons (Red, Yellow, Green)
    draw.ellipse([16, 12, 28, 24], fill=(239, 68, 68))
    draw.ellipse([34, 12, 46, 24], fill=(245, 158, 11))
    draw.ellipse([52, 12, 64, 24], fill=(16, 185, 129))
    
    # Title
    title = "🩺 Self-Healing Pipeline Agent — zsh / pwsh"
    draw.text((WIDTH // 2 - 140, 10), title, fill=GRAY, font=font_small)

def create_demo_animation(output_path="assets/demo.gif"):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        font = ImageFont.truetype("consola.ttf", 15)
        font_small = ImageFont.truetype("consola.ttf", 13)
        font_bold = ImageFont.truetype("consolab.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
        font_small = font
        font_bold = font

    # Sequence of terminal lines with their color and timing
    # (text, color, is_bold)
    script_steps = [
        # Frame 1: Initial shell
        [
            ("PS C:\\pipeline> python run_cli.py", CYAN, True),
        ],
        # Frame 2: Banner
        [
            ("PS C:\\pipeline> python run_cli.py", CYAN, True),
            ("", WHITE, False),
            ("╔═══════════════════════════════════════════════════════════════╗", PURPLE, False),
            ("║           🔧 Self-Healing Data Pipeline Agent 🔧              ║", WHITE, True),
            ("║   Autonomous Data Quality Engineering Powered by Grok (xAI)   ║", PURPLE, False),
            ("╚═══════════════════════════════════════════════════════════════╝", PURPLE, False),
        ],
        # Frame 3: User types 'hi dataset'
        [
            ("PS C:\\pipeline> python run_cli.py", CYAN, True),
            ("", WHITE, False),
            ("╔═══════════════════════════════════════════════════════════════╗", PURPLE, False),
            ("║           🔧 Self-Healing Data Pipeline Agent 🔧              ║", WHITE, True),
            ("║   Autonomous Data Quality Engineering Powered by Grok (xAI)   ║", PURPLE, False),
            ("╚═══════════════════════════════════════════════════════════════╝", PURPLE, False),
            ("", WHITE, False),
            ("🔧 Pipeline Agent: hi dataset", CYAN, True),
            ("👋 Hello! I'm your Self-Healing Pipeline Agent!", GREEN, False),
            ("📂 Loading dataset: tests/fixtures/dirty_types.csv", GRAY, False),
        ],
        # Frame 4: Loaded data table with errors
        [
            ("PS C:\\pipeline> python run_cli.py", CYAN, True),
            ("", WHITE, False),
            ("╔═══════════════════════════════════════════════════════════════╗", PURPLE, False),
            ("║           🔧 Self-Healing Data Pipeline Agent 🔧              ║", WHITE, True),
            ("║   Autonomous Data Quality Engineering Powered by Grok (xAI)   ║", PURPLE, False),
            ("╚═══════════════════════════════════════════════════════════════╝", PURPLE, False),
            ("", WHITE, False),
            ("🔧 Pipeline Agent: hi dataset", CYAN, True),
            ("👋 Hello! I'm your Self-Healing Pipeline Agent!", GREEN, False),
            ("✅ Loaded: dirty_types.csv (5 rows x 4 columns)", GREEN, False),
            ("", WHITE, False),
            ("  order_id  │ customer_name │ amount  │ order_date", GRAY, True),
            ("  ──────────┼───────────────┼─────────┼───────────", GRAY, False),
            ("  1         │ Alice         │ $100.50 │ 2024-01-15", YELLOW, False),
            ("  2         │ Bob           │ $200.00 │ 2024-01-16", YELLOW, False),
            ("  3         │ Charlie       │ $50.75  │ 2024-02-01", YELLOW, False),
        ],
        # Frame 5: User triggers 'datapipeline'
        [
            ("PS C:\\pipeline> python run_cli.py", CYAN, True),
            ("╔═══════════════════════════════════════════════════════════════╗", PURPLE, False),
            ("║           🔧 Self-Healing Data Pipeline Agent 🔧              ║", WHITE, True),
            ("╚═══════════════════════════════════════════════════════════════╝", PURPLE, False),
            ("✅ Loaded: dirty_types.csv (5 rows x 4 columns)", GREEN, False),
            ("  1 │ Alice   │ $100.50 │ 2024-01-15 (Currency Format Anomaly)", YELLOW, False),
            ("  2 │ Bob     │ $200.00 │ 2024-01-16 (Currency Format Anomaly)", YELLOW, False),
            ("", WHITE, False),
            ("🔧 Pipeline Agent: datapipeline", CYAN, True),
            ("🔄 Healing Attempt 1/3 — Validating schema against expected constraints...", GRAY, False),
            ("⚠️ [type_mismatch] column 'amount' expected float, found strings: ['$100.50']", RED, True),
        ],
        # Frame 6: Grok AI diagnosis
        [
            ("PS C:\\pipeline> python run_cli.py", CYAN, True),
            ("🔧 Pipeline Agent: datapipeline", CYAN, True),
            ("🔄 Healing Attempt 1/3", GRAY, False),
            ("⚠️ [type_mismatch] column 'amount' expected float, found strings: ['$100.50']", RED, True),
            ("", WHITE, False),
            ("🤖 Diagnosing Root Cause with Grok (xAI)...", PURPLE, True),
            ("🩺 Root Cause: 'amount' has upstream currency symbols blocking float cast", WHITE, False),
            ("   Confidence: 85% | Source: llm:grok-3", GRAY, False),
            ("💡 Proposed Fix: {'action': 'cast_type', 'column': 'amount', 'type': 'float'}", GREEN, True),
            ("🛡️ Policy Check: 'cast_type' is classified as SAFE -> Auto-applying...", CYAN, False),
        ],
        # Frame 7: Healing success and clean data table
        [
            ("🔧 Pipeline Agent: datapipeline", CYAN, True),
            ("⚠️ [type_mismatch] column 'amount' expected float, found strings: ['$100.50']", RED, False),
            ("🤖 Grok (xAI) Diagnosis: Currency symbols blocking float parsing", PURPLE, False),
            ("💡 Proposed Fix: {'action': 'cast_type', 'column': 'amount', 'type': 'float'}", GREEN, False),
            ("🛠️ Applying Fix: Strip '$' and convert 'amount' to float64...", CYAN, False),
            ("───────────────────────────────────────────────────────────────", GRAY, False),
            ("🔄 Healing Attempt 2/3 — Re-validating dataset...", GRAY, False),
            ("✅ All validations passed! 100% compliant with expected schema.", GREEN, True),
            ("⚡ Ingestion: 5 rows successfully loaded into DuckDB warehouse!", GREEN, True),
            ("", WHITE, False),
            ("  order_id  │ customer_name │ amount  │ order_date", GRAY, True),
            ("  ──────────┼───────────────┼─────────┼───────────", GRAY, False),
            ("  1         │ Alice         │ 100.50  │ 2024-01-15", GREEN, False),
            ("  2         │ Bob           │ 200.00  │ 2024-01-16", GREEN, False),
            ("  3         │ Charlie       │ 50.75   │ 2024-02-01", GREEN, False),
            ("  4         │ Diana         │ 300.25  │ 2024-02-14", GREEN, False),
            ("  5         │ Eve           │ 75.00   │ 2024-03-01", GREEN, False),
            ("", WHITE, False),
            ("✨ Pipeline Status: SUCCESS (0 errors remaining)", GREEN, True),
        ],
    ]

    durations = [1200, 1400, 1600, 2000, 2200, 2800, 4000]
    frames = []

    for step_lines in script_steps:
        img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)
        draw_window_frame(draw, font_small)
        
        y = 55
        for line_text, color, is_bold in step_lines:
            f = font_bold if is_bold else font
            draw.text((28, y), line_text, fill=color, font=f)
            y += 24
            
        frames.append(img)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"✅ Generated demo GIF: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    create_demo_animation("assets/demo.gif")
