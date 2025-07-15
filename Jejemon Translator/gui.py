import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
from translator import JejemonTranslator
from PIL import Image, ImageDraw, ImageFont
import os

class JejemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jejemon Translator")
        self.translator = JejemonTranslator()
        self.mode = None
        self.bg_color = "#f8f6f2"
        self.root.geometry("800x500")
        self._build_main_menu()

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _build_main_menu(self):
        self._clear_window()
        self.mode = None
        self.output_var = tk.StringVar()
        self.input_var = tk.StringVar()
        self.bg_color = "#f8f6f2"
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#f8f6f6', foreground='#222', focuscolor='')
        style.map('TButton',
            background=[('active', '#b6e388'), ('pressed', '#a0c97c')],
            relief=[('pressed', 'sunken'), ('!pressed', 'flat')],
            foreground=[('active', '#222'), ('pressed', '#222')]
        )
        style.configure('Hover.TButton', background='#b6e388', foreground='#222')
        try:
            gif_path = os.path.join("multimedia", "RESUME POWERPOINT.gif")
            self.gif_img = Image.open(gif_path)
            self.gif_frames = []
            self.gif_sizes = []
            frame_idx = 0
            try:
                while True:
                    if frame_idx % 2 == 0:
                        frame = self.gif_img.copy().resize((800, 500))
                        self.gif_frames.append(ImageTk.PhotoImage(frame))
                        self.gif_sizes.append(frame.size)
                    frame_idx += 1
                    self.gif_img.seek(frame_idx)
            except EOFError:
                pass
        except Exception as e:
            self.gif_frames = []
        self.bg_canvas = tk.Canvas(self.root, width=800, height=500, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        if self.gif_frames:
            self.bg_gif_id = self.bg_canvas.create_image(0, 0, anchor='nw', image=self.gif_frames[0])
            def animate_bg_gif(idx=0):
                if self.gif_frames:
                    self.bg_canvas.itemconfig(self.bg_gif_id, image=self.gif_frames[idx])
                    self.root.after(80, animate_bg_gif, (idx+1)%len(self.gif_frames))
            animate_bg_gif()
        else:
            self.bg_canvas.create_rectangle(0, 0, 800, 500, fill=self.bg_color, outline="")
        btn_frame = tk.Frame(self.root, bg='')
        btn_frame.pack(expand=True)
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='#f8f6f6', foreground='#222', focuscolor='')
        style.configure('Hover.TButton', background='#b6e388', foreground='#222')
        self.btn_to_jejemon = ttk.Button(btn_frame, text="Normalize to Jejemon", width=18, command=self._set_to_jejemon, style='TButton')
        self.btn_to_jejemon.grid(row=0, column=0, padx=4)
        self.btn_to_normal = ttk.Button(btn_frame, text="Jejemon to Normalize", width=18, command=self._set_to_normal, style='TButton')
        self.btn_to_normal.grid(row=0, column=1, padx=4)
        self.btn_exit = ttk.Button(btn_frame, text="Exit Program", width=12, command=self.root.quit, style='TButton')
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
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=8, borderwidth=0, relief='flat', background='', foreground='#222', focuscolor='')
        style.map('TButton',
            background=[('active', '#b6e388'), ('pressed', '#a0c97c')],
            relief=[('pressed', 'sunken'), ('!pressed', 'flat')],
            foreground=[('active', '#222'), ('pressed', '#222')]
        )
        style.configure('Hover.TButton', background='#b6e388', foreground='#222')
        canvas_frame = tk.Frame(self.root, bg=self.bg_color, bd=0, highlightbackground="#b6e388", highlightthickness=2)
        canvas_frame.pack(pady=(10, 5), padx=10)
        self.output_canvas = tk.Canvas(
            canvas_frame,
            width=500,
            height=500,
            bg=self.bg_color,
            highlightthickness=0,
            relief="flat"
        )
        self.output_canvas.pack()
        color_frame = tk.Frame(self.root, bg=self.bg_color)
        color_frame.pack(pady=(0, 4))
        tk.Label(color_frame, text="Background color:", bg=self.bg_color).pack(side=tk.LEFT)
        tk.Button(color_frame, bg="#b6e388", width=2, command=lambda: self._change_bg_color("#b6e388"), relief='flat', bd=1, highlightbackground="#b6e388").pack(side=tk.LEFT, padx=2)
        tk.Button(color_frame, bg="#ffffff", width=2, command=lambda: self._change_bg_color("#ffffff"), relief='flat', bd=1, highlightbackground="#b6e388").pack(side=tk.LEFT, padx=2)
        tk.Button(color_frame, bg="#f8f6f2", width=2, command=lambda: self._change_bg_color("#f8f6f2"), relief='flat', bd=1, highlightbackground="#b6e388").pack(side=tk.LEFT, padx=2)
        self.input_entry = tk.Entry(self.root, textvariable=self.input_var, font=("Arial", 14), width=40, relief="solid", bd=2, highlightbackground="#b6e388", highlightthickness=2)
        self.input_entry.pack(pady=4)
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=4)
        self.btn_translate = ttk.Button(btn_frame, text="Translate", width=15, command=self._translate, style='TButton')
        self.btn_translate.grid(row=0, column=0, padx=5)
        self.btn_save = ttk.Button(btn_frame, text="Save", width=10, command=self._save_text, style='TButton')
        self.btn_save.grid(row=0, column=1, padx=5)
        self.btn_back = ttk.Button(btn_frame, text="Back to Main Menu", width=20, command=self._build_main_menu, style='TButton')
        self.btn_back.grid(row=0, column=2, padx=5)
        for btn in [self.btn_translate, self.btn_save, self.btn_back]:
            btn.bind("<Enter>", lambda e, b=btn: b.configure(style='Hover.TButton'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(style='TButton'))
        self._draw_output_canvas()

    def _draw_output_canvas(self):
        if hasattr(self, 'output_canvas'):
            self.output_canvas.delete("all")
            text = self.output_var.get()
            if not text.strip():
                return
            font, wrapped_lines, font_size, line_height, preview_line_height, preview_total_text_height, max_text_width, margin = self._get_font_and_wrapped_lines(
                text, max_img_size=500, min_font_size=6, max_font_size=120, canvas_height=500, line_height_multiplier=1.3)
            try:
                from tkinter import font as tkfont
                font_name = "Arial"
                tk_font = tkfont.Font(family=font_name, size=font_size)
            except Exception:
                tk_font = ("Arial", font_size)
            y = (500 - preview_total_text_height) // 2
            if y < margin:
                y = margin
            for line in wrapped_lines:
                text_width = tk_font.measure(line) if hasattr(tk_font, 'measure') else 10 * len(line)
                x = (500 - text_width) // 2
                self.output_canvas.create_text(x, y, text=line, font=tk_font, fill="#000000", anchor="nw")
                y += preview_line_height

    def _change_bg_color(self, color):
        self.bg_color = color
        if hasattr(self, 'output_canvas'):
            self.output_canvas.config(bg=color)
            self._draw_output_canvas()
        elif hasattr(self, 'output_label'):
            self.output_label.config(bg=color)
            pass

    def _translate(self):
        text = self.input_var.get().strip()
        if not text:
            self.output_var.set("Please enter some text.")
            if hasattr(self, 'output_canvas'):
                self._draw_output_canvas()
            return
        if self.mode == 'to_jejemon':
            normalized = self.translator.normalize(text)
            jejemonized = self.translator.jejemonize(normalized)
            self.output_var.set(jejemonized)
        elif self.mode == 'to_normal':
            normalized = self.translator.normalize(text)
            self.output_var.set(normalized)
        else:
            self.output_var.set("Invalid mode.")
        if hasattr(self, 'output_canvas'):
            self._draw_output_canvas()

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
        from PIL import ImageFont
        import textwrap
        img_width = 1000
        img_height = 1000
        min_font_size = 6
        max_font_size = 200
        font, wrapped_lines, font_size, line_height, save_line_height, total_text_height, max_text_width, margin = self._get_font_and_wrapped_lines(
            text, max_img_size=img_width, min_font_size=min_font_size, max_font_size=max_font_size, canvas_height=img_height, line_height_multiplier=1.0)
        bg = self.bg_color
        if bg.startswith('#'):
            bg_rgb = tuple(int(bg[i:i+2], 16) for i in (1, 3, 5))
        else:
            bg_rgb = (248, 246, 242)
        img = Image.new('RGB', (img_width, img_height), bg_rgb)
        draw = ImageDraw.Draw(img)
        y = (img_height - total_text_height) // 2
        if y < margin:
            y = margin
        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (img_width - w) // 2
            if x < margin:
                x = margin
            draw.text((x, y), line, fill=(0, 0, 0), font=font)
            y += save_line_height
        img.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    gui = JejemonGUI(root)
    root.mainloop() 