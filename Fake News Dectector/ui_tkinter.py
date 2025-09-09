import subprocess
import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))



def run_node_with_url(url: str) -> str:
	"""Call the existing Node.js CLI with a URL (rules-based path)."""
	cmd = ["node", os.path.join(PROJECT_ROOT, "index.js"), url]
	try:
		completed = subprocess.run(
			cmd,
			cwd=PROJECT_ROOT,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True,
			encoding="utf-8",
			errors="replace",
			check=False,
		)
		return completed.stdout
	except FileNotFoundError:
		return "Error: Node.js not found. Please install Node and ensure 'node' is on PATH."
	except Exception as exc:
		return f"Error running classifier: {exc}"


def parse_basic_output(output: str) -> str:
	"""Minimal formatting: return as-is but try to keep the most relevant lines first."""
	if not output:
		return "(no output)"
	lines = [line.rstrip() for line in output.splitlines() if line.strip()]
	# Prefer lines that contain prediction cues
	priority = [
		"➡️ Predicted:",
		"⚠️ Red flags:",
		"rules conf:",
		"📝 Input:",
	]
	scored = []
	for ln in lines:
		score = sum(1 for key in priority if key in ln)
		scored.append((score, ln))
	scored.sort(key=lambda t: (-t[0], lines.index(t[1])))
	ordered = [ln for _, ln in scored]
	return "\n".join(ordered)


class App(tk.Tk):
	def __init__(self) -> None:
		super().__init__()
		self.title("Fake News Detector - URL Analyzer")
		self.geometry("760x420")

		self._build_widgets()

	def _build_widgets(self) -> None:
		# URL input only
		url_frame = ttk.LabelFrame(self, text="Article URL")
		url_frame.pack(fill=tk.X, padx=12, pady=6)
		self.url_entry = ttk.Entry(url_frame)
		self.url_entry.pack(fill=tk.X, padx=8, pady=8)
		tt = ttk.Label(url_frame, text="Paste a news article URL. The app will scrape and analyze it.")
		tt.pack(side=tk.LEFT, padx=8, pady=(0, 8))

		# Buttons
		btn_frame = ttk.Frame(self)
		btn_frame.pack(fill=tk.X, padx=12, pady=6)
		self.run_btn = ttk.Button(btn_frame, text="Analyze URL", command=self.on_analyze_clicked)
		self.run_btn.pack(side=tk.LEFT, padx=6)

		# Output
		out_frame = ttk.LabelFrame(self, text="Result")
		out_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))
		self.output = tk.Text(out_frame, wrap=tk.WORD, height=14, state=tk.NORMAL)
		self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
		self.output.insert(tk.END, "Ready. Paste a URL and click Analyze.")

	def on_analyze_clicked(self) -> None:
		url = self.url_entry.get().strip()
		if not url:
			messagebox.showwarning("URL required", "Please paste an article URL to analyze.")
			return
		self._run_async(lambda: run_node_with_url(url))

	def _run_async(self, func):
		self.run_btn.configure(state=tk.DISABLED)
		self._set_output("Running...\n")

		def worker():
			try:
				out = func()
			except Exception as exc:  # noqa: BLE001
				out = f"Error: {exc}"
			self.after(0, lambda: self._on_result(out))

		threading.Thread(target=worker, daemon=True).start()

	def _on_result(self, output_text: str) -> None:
		formatted = parse_basic_output(output_text)
		self._set_output(formatted)
		self.run_btn.configure(state=tk.NORMAL)

	def _set_output(self, text: str) -> None:
		self.output.configure(state=tk.NORMAL)
		self.output.delete("1.0", tk.END)
		self.output.insert(tk.END, text)
		self.output.see(tk.END)
		self.output.configure(state=tk.NORMAL)


if __name__ == "__main__":
	app = App()
	app.mainloop()


