import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
from translator import JejemonTranslator
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os

class JejemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jejemon Translator")
        self.translator = JejemonTranslator()
        self.mode = None
        self.bg_color = "#393E46"
        self.root.geometry("500x700")
        self._build_main_menu()

    def _clear_window(self):
        if hasattr(self, 'bg_canvas') and hasattr(self, 'bg_gif_id'):
            try:
                self.root.after_cancel(self._gif_after_id)
            except Exception:
                pass
        for widget in self.root.winfo_children():
            widget.destroy()

    def _build_main_menu(self):
        self._clear_window()
        self.mode = None
        self.output_var = tk.StringVar()
        self.input_var = tk.StringVar()
        self.bg_color = "#f8f6f2"
        self.root.geometry("1200x700")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#f8f6f6', foreground='#222', focuscolor='')
        style.map('TButton',
            background=[('active', '#b6e388'), ('pressed', '#a0c97c')],
            relief=[('pressed', 'sunken'), ('!pressed', 'flat')],
            foreground=[('active', '#222'), ('pressed', '#222')]
        )
        style.configure('Hover.TButton', background='#b6e388', foreground='#222')
        # Set PNG background for main menu
        from PIL import Image, ImageTk
        bg_path = os.path.join("multimedia", "background.png")
        target_w, target_h = 1200, 700
        try:
            bg_img = Image.open(bg_path)
            orig_w, orig_h = bg_img.size
            # 'Cover' strategy: scale so the image fills the window, cropping as needed
            scale = max(target_w / orig_w, target_h / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)
            # Crop to window size, centered
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            right = left + target_w
            bottom = top + target_h
            bg_img = bg_img.crop((left, top, right, bottom))
            self.bg_img_tk = ImageTk.PhotoImage(bg_img)
        except Exception as e:
            self.bg_img_tk = None
        self.bg_canvas = tk.Canvas(self.root, width=1200, height=700, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0)
        if self.bg_img_tk:
            self.bg_canvas.create_image(0, 0, anchor='nw', image=self.bg_img_tk)
        else:
            self.bg_canvas.create_rectangle(0, 0, 1200, 700, fill=self.bg_color, outline="")
        btn_frame = tk.Frame(self.root, bg='')
        btn_frame.pack(expand=True)

        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#f8f6f6', foreground='#222', focuscolor='')
        style.configure('Hover.TButton', background='#b6e388', foreground='#222')

        self.btn_to_jejemon = ttk.Button(btn_frame, text="Normalize to Jejemon", width=22, command=self._set_to_jejemon, style='TButton')
        self.btn_to_jejemon.grid(row=0, column=0, padx=4)

        self.btn_to_normal = ttk.Button(btn_frame, text="Jejemon to Normalize", width=22, command=self._set_to_normal, style='TButton')
        self.btn_to_normal.grid(row=0, column=1, padx=4)

        self.btn_exit = ttk.Button(btn_frame, text="Exit Program", width=16, command=self.root.quit, style='TButton')
        self.btn_exit.grid(row=0, column=2, padx=4)

        for btn in [self.btn_to_jejemon, self.btn_to_normal, self.btn_exit]:
            btn.bind("<Enter>", lambda e, b=btn: b.configure(style='Hover.TButton'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(style='TButton'))

    def _set_to_jejemon(self):
        self.mode = 'to_jejemon'
        self._build_translate_view()

    def _set_to_normal(self):
        self.mode = 'to_normal'
        self._build_translate_view()

    def _get_font_and_wrapped_lines(self, text, max_img_size=500, min_font_size=6, max_font_size=120, canvas_height=500, line_height_multiplier=1.0):
        from PIL import ImageFont
        import textwrap
        font_name_candidates = ["arialn.ttf", "arial.ttf"]
        font_path = None
        for font_name in font_name_candidates:
            try:
                _ = ImageFont.truetype(font_name, 40)
                font_path = font_name
                break
            except:
                continue
        def wrap_lines(lines, font, max_width):
            wrapped = []
            for line in lines:
                while True:
                    line_width = font.getbbox(line)[2] - font.getbbox(line)[0]
                    if line_width <= max_width:
                        wrapped.append(line)
                        break
                    avg_char_width = font.getbbox('A')[2] - font.getbbox('A')[0]
                    if avg_char_width == 0:
                        avg_char_width = 10
                    chars_per_line = max(1, max_width // avg_char_width)
                    wrapped.extend(textwrap.wrap(line, width=chars_per_line, break_long_words=True, replace_whitespace=False))
                    break
            return wrapped
        font_size = max_font_size
        lines = text.split('\n')
        margin = 30
        max_width = max_img_size - 2 * margin
        max_height = canvas_height - 2 * margin
        while font_size >= min_font_size:
            try:
                if font_path:
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    font = ImageFont.load_default()
                wrapped_lines = wrap_lines(lines, font, max_width)
                line_height = font.getbbox('A')[3] - font.getbbox('A')[1] + int(font_size * 0.3)
                adj_line_height = int(line_height * line_height_multiplier)
                total_text_height = adj_line_height * len(wrapped_lines)
                all_fit = True
                for line in wrapped_lines:
                    if font.getbbox(line)[2] - font.getbbox(line)[0] > max_width:
                        all_fit = False
                        break
                if all_fit and total_text_height <= max_height:
                    break
                font_size -= 2
            except Exception:
                font_size -= 2
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
        wrapped_lines = wrap_lines(lines, font, max_width)
        line_height = font.getbbox('A')[3] - font.getbbox('A')[1] + int(font_size * 0.3)
        adj_line_height = int(line_height * line_height_multiplier)
        total_text_height = adj_line_height * len(wrapped_lines)
        max_text_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in wrapped_lines]) if wrapped_lines else 0
        return font, wrapped_lines, font_size, line_height, adj_line_height, total_text_height, max_text_width, margin

    def _build_translate_view(self):
        self._clear_window()
        self.bg_color = "#393E46"
        self.root.geometry("1366x768")
        self.root.configure(bg="#393E46")
        style = ttk.Style()
        style.theme_use('clam')
        # Custom button styles for visibility
        style.configure('Green.TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#b6e388', foreground='#222', focuscolor='')
        style.map('Green.TButton',
            background=[('active', '#a0c97c'), ('pressed', '#8fc46c')],
            foreground=[('active', '#222'), ('pressed', '#222')]
        )
        style.configure('White.TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#fff', foreground='#222', focuscolor='')
        style.map('White.TButton',
            background=[('active', '#e0e0e0'), ('pressed', '#cccccc')],
            foreground=[('active', '#222'), ('pressed', '#222')]
        )
        # Main container frame for vertical layout
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        # Output Canvas (large, but not full height)
        output_frame = tk.Frame(main_frame, bg=self.bg_color, bd=0, highlightthickness=0)
        output_frame.pack(pady=(20, 5), padx=100, fill=tk.X)
        self.output_canvas = tk.Canvas(
            output_frame,
            width=1000,
            height=420,
            bg="#F2F2F2",
            highlightthickness=0,
            relief="flat"
        )
        self.output_canvas.pack()
        self._draw_output_canvas(self.output_var.get())
        self.output_frame = output_frame
        # Color selector with fixed label background
        color_selector_frame = tk.Frame(main_frame, bg=self.bg_color)
        color_selector_frame.pack(pady=(0, 8))
        # Fixed label background frame
        label_bg_frame = tk.Frame(color_selector_frame, bg="#393E46")
        label_bg_frame.pack(side=tk.LEFT)
        tk.Label(label_bg_frame, text="Background color:", bg="#393E46", fg="#fff").pack()
        # Color buttons
        for color in ["#b6e388", "#ffffff", "#f8f6f2"]:
            border = tk.Frame(color_selector_frame, bg="black", padx=1, pady=1)
            border.pack(side=tk.LEFT, padx=2)
            tk.Button(border, bg=color, width=2, height=1, command=lambda c=color: self._change_bg_color(c), relief='flat', bd=0).pack()
        self.color_frame = color_selector_frame
        # Input entry
        self.input_entry = tk.Entry(main_frame, textvariable=self.input_var, font=("Arial", 14), width=80, relief="solid", bd=2)
        self.input_entry.pack(pady=8)
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(pady=10)
        self.btn_translate = ttk.Button(btn_frame, text="Translate", width=18, command=self._translate, style='Green.TButton')
        self.btn_translate.grid(row=0, column=0, padx=10)
        self.btn_save = ttk.Button(btn_frame, text="Save", width=12, command=self._save_text, style='White.TButton')
        self.btn_save.grid(row=0, column=1, padx=10)
        self.btn_back = ttk.Button(btn_frame, text="Back to Main Menu", width=22, command=self._build_main_menu, style='White.TButton')
        self.btn_back.grid(row=0, column=2, padx=10)
        # Removed hover effects

    def _draw_output_canvas(self, text):
        if hasattr(self, 'output_canvas'):
            self.output_canvas.delete("all")
            if not text:
                return
            import textwrap
            import tkinter.font as tkFont
            canvas_width = int(self.output_canvas['width'])
            canvas_height = int(self.output_canvas['height'])
            margin = 30  # Left and right margin in pixels
            min_font_size = 8
            max_font_size = 32
            font_family = "Arial"
            # Try from big to small font size until it fits
            for font_size in range(max_font_size, min_font_size - 1, -1):
                font = tkFont.Font(family=font_family, size=font_size, weight="bold")
                usable_width = canvas_width - 2 * margin
                # Estimate max chars per line for wrapping
                avg_char_width = font.measure('A') if font.measure('A') > 0 else font_size * 0.6
                max_chars_per_line = max(1, int(usable_width // avg_char_width))
                lines = []
                for paragraph in text.split('\n'):
                    lines.extend(textwrap.wrap(paragraph, width=max_chars_per_line))
                    if paragraph != text.split('\n')[-1]:
                        lines.append("")  # Add blank line for paragraph breaks
                # Check if all lines fit in width
                fits_width = all(font.measure(line) <= usable_width for line in lines)
                line_height = font.metrics("linespace") + 4
                total_text_height = len(lines) * line_height
                fits_height = total_text_height <= (canvas_height - 2 * 10)  # 10px top/bottom margin
                if fits_width and fits_height:
                    break
            # Center vertically
            y = (canvas_height - total_text_height) // 2
            for line in lines:
                self.output_canvas.create_text(
                    canvas_width // 2, y, text=line, font=(font_family, font_size, "bold"), fill="#222", anchor="n"
                )
                y += line_height

    def _update_output_text(self, text):
        self._draw_output_canvas(text)

    def _clear_placeholder(self):
        if self.input_text.get("1.0", "end-1c") == "Type or paste your text here...":
            self.input_text.delete("1.0", "end")

    def _change_bg_color(self, color):
        self.bg_color = color
        if hasattr(self, 'output_canvas'):
            self.output_canvas.config(bg=color)
        if hasattr(self, 'output_frame'):
            self.output_frame.config(bg=color)
        if hasattr(self, 'color_frame'):
            self.color_frame.config(bg=color)

    def _translate(self):
        input_text = self.input_var.get()
        if not input_text.strip():
            messagebox.showwarning("Input Required", "Please enter text to translate.")
            return
        if self.mode == 'to_jejemon':
            result = self.translator.jejemonize(input_text)
        else:
            result = self.translator.normalize(input_text)
        self.output_var.set(result)
        self._update_output_text(result)

    def _save_text(self):
        text = self.output_var.get()
        if not text.strip():
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if file_path:
            try:
                self._save_text_as_image(text, file_path)
            except Exception as e:
                print(f"Failed to save image: {e}")

    def _save_text_as_image(self, text, file_path):
        # Always save as 400x400 image, regardless of canvas size
        from PIL import Image, ImageDraw, ImageFont
        img_size = 400
        img = Image.new('RGB', (img_size, img_size), color=self.bg_color)
        draw = ImageDraw.Draw(img)
        font_size = 24
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        import textwrap
        lines = textwrap.wrap(text, width=22)
        total_text_height = len(lines) * (font_size + 8)
        y = (img_size - total_text_height) // 2
        for line in lines:
            w, h = draw.textsize(line, font=font)
            x = (img_size - w) // 2
            draw.text((x, y), line, font=font, fill="#222")
            y += font_size + 8
        img.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    gui = JejemonGUI(root)
    root.mainloop() 