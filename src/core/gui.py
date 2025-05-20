import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image
from src.core.utils import resource_path

class WavPatcherGUI:
    def __init__(self, on_browse=None, on_run=None, on_ro_check=None, on_convert=None, on_browse_click2=None):
        self.on_browse = on_browse
        self.on_run = on_run
        self.on_ro_check = on_ro_check
        self.on_convert = on_convert
        self.on_browse_click2 = on_browse_click2

        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.root.title("WavPatcher 0.9.2 (BETA)")
        self.root.iconbitmap(resource_path('img/wavico.ico'))

        self.bg_canvas = tk.Frame(self.root)
        self.bg_canvas.pack()

        self.notebook = ttk.Notebook(self.bg_canvas)
        self.notebook.pack(padx=(8, 4), pady=(8, 4))

        self.tab1 = tk.Frame(self.notebook)
        self.tab2 = tk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="WAV Patcher")
        self.notebook.add(self.tab2, text="32+ Bit Converter")

        self.main_frame = tk.Frame(self.tab1)
        self.main_frame.pack(padx=(8, 4), pady=(8, 4))

        self.sec_frame = tk.Frame(self.main_frame, width=0, height=500)
        self.sec_frame.grid(padx=0, pady=0, row=0, column=1, sticky=tk.N)

        self.text_area = ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            height=30,
            width=56,
            state=tk.DISABLED,
            takefocus=0
        )
        self.text_area.grid(padx=0, pady=0, row=0, column=0)

        self.img = ImageTk.PhotoImage(Image.open(resource_path("img/wp_emboss.png")))
        self.img_label = tk.Label(self.sec_frame, image=self.img)
        self.img_label.grid(row=0, pady=4)

        self.browse_button = tk.Button(
            master=self.sec_frame,
            text="Browse...",
            height=2,
            width=11,
            command=self._on_browse_click
        )
        self.browse_button.grid(padx=4, pady=4, row=1, column=0, sticky=tk.N)

        self.run_button_text = tk.StringVar()
        self.run_button = tk.Button(
            master=self.sec_frame,
            textvariable=self.run_button_text,
            height=2,
            width=11,
            state=tk.DISABLED,
            command=self._on_run_click
        )
        self.run_button.grid(padx=4, pady=4, row=2, column=0, sticky=tk.S)

        self.status_text2 = tk.StringVar()
        self.status_text2.set("")
        self.status_bar2 = tk.Label(self.main_frame, textvariable=self.status_text2, bd=1, relief=tk.GROOVE)
        self.status_bar2.grid(padx=0, pady=0, row=1, column=0, sticky=tk.NW+tk.E)

        self.status_text = tk.StringVar()
        self.status_text.set("")
        self.status_bar = tk.Label(self.main_frame, textvariable=self.status_text, bd=1, relief=tk.GROOVE)
        self.status_bar.grid(padx=0, pady=0, row=2, column=0, sticky=tk.NW+tk.E)

        self.check_var = tk.IntVar()
        self.check_box = tk.Checkbutton(
            self.sec_frame,
            text="Read-only",
            onvalue=1,
            offvalue=0,
            variable=self.check_var,
            command=self._on_ro_check
        )
        self.check_box.grid(pady=8, row=3, column=0, sticky=tk.S)
        self.check_var.set(1)
        self._on_ro_check()

        self.main_frame2 = tk.Frame(self.tab2)
        self.main_frame2.pack(padx=(8, 4), pady=(8, 4))

        self.sec_frame2 = tk.Frame(self.main_frame2, width=0, height=500)
        self.sec_frame2.grid(padx=0, pady=0, row=0, column=1, sticky=tk.N)

        self.text_area2 = ScrolledText(
            self.main_frame2,
            wrap=tk.WORD,
            height=30,
            width=56,
            state=tk.DISABLED,
            takefocus=0
        )
        self.text_area2.grid(padx=0, pady=0, row=0, column=0)

        self.img_label2 = tk.Label(self.sec_frame2, image=self.img)
        self.img_label2.grid(row=0, pady=4)

        self.browse_button2 = tk.Button(
            master=self.sec_frame2,
            text="Browse...",
            height=2,
            width=11,
            command=self._on_browse_click2
        )
        self.browse_button2.grid(padx=4, pady=4, row=1, column=0, sticky=tk.N)

        self.convert_button = tk.Button(
            master=self.sec_frame2,
            text="Convert",
            height=2,
            width=11,
            state=tk.DISABLED,
            command=self._on_convert_click
        )
        self.convert_button.grid(padx=4, pady=4, row=2, column=0, sticky=tk.S)

        self.status_text2_2 = tk.StringVar()
        self.status_text2_2.set("")
        self.status_bar2_2 = tk.Label(self.main_frame2, textvariable=self.status_text2_2, bd=1, relief=tk.GROOVE)
        self.status_bar2_2.grid(padx=0, pady=0, row=1, column=0, sticky=tk.NW+tk.E)

        self.status_text_2 = tk.StringVar()
        self.status_text_2.set("")
        self.status_bar_2 = tk.Label(self.main_frame2, textvariable=self.status_text_2, bd=1, relief=tk.GROOVE)
        self.status_bar_2.grid(padx=0, pady=0, row=2, column=0, sticky=tk.NW+tk.E)

        self.update_text_area(self._get_welcome_text())
        self.update_text_area2(self._get_converter_welcome_text())

        self.selected_directory = ""
        self.selected_directory2 = ""

    def _on_browse_click(self):
        if self.on_browse:
            self.on_browse()

    def _on_run_click(self):
        if self.on_run:
            self.on_run()

    def _on_ro_check(self):
        is_readonly = self.check_var.get() == 1
        self.run_button_text.set("Check" if is_readonly else "Patch")
        if self.on_ro_check:
            self.on_ro_check(is_readonly)
        return is_readonly

    def browse_for_directory(self):
        directory = filedialog.askdirectory(initialdir="/", title="Select Music Folder...")
        if directory:
            self.selected_directory = directory
            self.status_text2.set(directory)
            self.update_text_area(f"WavPatcher 0.9.2b \n\nFolder = {directory}\n\nCalculating total files..\n\n")
        return directory

    def update_text_area(self, text, append=False):
        self.text_area.configure(state=tk.NORMAL)
        if not append:
            self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)

    def update_status(self, text):
        self.status_text.set(text)

    def set_button_states(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.run_button['state'] = state
        self.check_box['state'] = state
        self.browse_button['state'] = state

    def enable_run_button(self, enabled=True):
        self.run_button['state'] = tk.NORMAL if enabled else tk.DISABLED

    def start(self):
        self.root.mainloop()

    def _on_browse_click2(self):
        if hasattr(self, 'on_browse_click2') and self.on_browse_click2:
            self.on_browse_click2()

    def _on_convert_click(self):
        if self.on_convert:
            self.on_convert()

    def browse_for_directory2(self):
        directory = filedialog.askdirectory(initialdir="/", title="Select Music Folder...")
        if directory:
            self.selected_directory2 = directory
            self.status_text2_2.set(directory)
            self.update_text_area2(f"WavPatcher 0.9.2b - 32+ Bit Converter\n\nFolder = {directory}\n\nCalculating total files..\n\n")
        return directory

    def update_text_area2(self, text, append=False):
        self.text_area2.configure(state=tk.NORMAL)
        if not append:
            self.text_area2.delete('1.0', tk.END)
        self.text_area2.insert(tk.END, text)
        self.text_area2.see(tk.END)
        self.text_area2.configure(state=tk.DISABLED)

    def update_status2(self, text):
        self.status_text_2.set(text)

    def enable_convert_button(self, enabled=True):
        self.convert_button['state'] = tk.NORMAL if enabled else tk.DISABLED

    def set_button_states2(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.convert_button['state'] = state
        self.browse_button2['state'] = state

    def _get_welcome_text(self):
        return """\
  _    _            ______     _       _               
 | |  | |           | ___ \   | |     | |  0.9.2 (BETA)            
 | |  | | __ ___   _| |_/ /_ _| |_ ___| |__   ___ _ __ 
 | |/\| |/ _` \ \ / /  __/ _` | __/ __| '_ \ / _ \ '__|
 \  /\  / (_| |\ V /| | | (_| | || (__| | | |  __/ |   
 \/  \/ \__,_| \_/ \_|  \__,_|\__\___|_| |_|\___|_|
========================================================

The purpose of WavPatcher is to replace a WAV_EXTENSIBLE header subchunk sometimes found in WAV files that breaks compatibility on some equipment. This tool does not re-encode audio files but writes a 2-byte integer to invoke standard PCM. As such, this tool will not make non-standard multi-channel files compatible. It is merely intended for 2-channel (stereo) files which have otherwise compatible attributes.

It's advisable to first simulate output by selecting 'Ready-only' to check the status of files.

If you are retroactively patching files, connect your Rekordbox drive and select it via the browse dialogue.

Github: https://github.com/ckbaudio/wavpatcher
"""

    def _get_converter_welcome_text(self):
        return """\
  _    _            ______     _       _               
 | |  | |           | ___ \   | |     | |  0.9.2 (BETA)            
 | |  | | __ ___   _| |_/ /_ _| |_ ___| |__   ___ _ __ 
 | |/\| |/ _` \ \ / /  __/ _` | __/ __| '_ \ / _ \ '__|
 \  /\  / (_| |\ V /| | | (_| | || (__| | | |  __/ |   
 \/  \/ \__,_| \_/ \_|  \__,_|\__\___|_| |_|\___|_|
========================================================

The 32+ Bit Converter tab allows you to find WAV files with bit depth greater than 32 bits and copy them to a "WPPtoconvert" folder.

This is useful for identifying high bit depth files that may not be compatible with certain equipment.

To use:
1. Click "Browse..." to select a directory containing WAV files
2. Click "Convert" to find and copy high bit depth files

The copied files will be placed in a "WPPtoconvert" folder within the selected directory.
"""
