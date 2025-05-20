import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image
from src.core.utils import resource_path

class WavPatcherGUI:
    def __init__(self, on_browse=None, on_run=None, on_ro_check=None):
        # Store callback functions
        self.on_browse = on_browse
        self.on_run = on_run
        self.on_ro_check = on_ro_check
        
        # Initialize main window
        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.root.title("WavPatcher 0.9.2 (BETA)")
        self.root.iconbitmap(resource_path('img/wavico.ico'))
        
        # Create frames
        self.bg_canvas = tk.Frame(self.root)
        self.bg_canvas.pack()
        
        self.main_frame = tk.Frame(self.bg_canvas)
        self.main_frame.pack(padx=(8, 4), pady=(8, 4))
        
        self.sec_frame = tk.Frame(self.main_frame, width=0, height=500)
        self.sec_frame.grid(padx=0, pady=0, row=0, column=1, sticky=tk.N)
        
        # Create text area
        self.text_area = ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            height=30,
            width=56,
            state=tk.DISABLED,
            takefocus=0
        )
        self.text_area.grid(padx=0, pady=0, row=0, column=0)
        
        # Load and display logo
        self.img = ImageTk.PhotoImage(Image.open(resource_path("img/wp_emboss.png")))
        self.img_label = tk.Label(self.sec_frame, image=self.img)
        self.img_label.grid(row=0, pady=4)
        
        # Create buttons
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
        
        # Create status bars
        self.status_text2 = tk.StringVar()
        self.status_text2.set("")
        self.status_bar2 = tk.Label(self.main_frame, textvariable=self.status_text2, bd=1, relief=tk.GROOVE)
        self.status_bar2.grid(padx=0, pady=0, row=1, column=0, sticky=tk.NW+tk.E)
        
        self.status_text = tk.StringVar()
        self.status_text.set("")
        self.status_bar = tk.Label(self.main_frame, textvariable=self.status_text, bd=1, relief=tk.GROOVE)
        self.status_bar.grid(padx=0, pady=0, row=2, column=0, sticky=tk.NW+tk.E)
        
        # Create checkbox
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
        
        # Initialize with welcome text
        self.update_text_area(self._get_welcome_text())
        
        # Selected directory
        self.selected_directory = ""
    
    def _on_browse_click(self):
        """Handle browse button click"""
        if self.on_browse:
            self.on_browse()
    
    def _on_run_click(self):
        """Handle run button click"""
        if self.on_run:
            self.on_run()
    
    def _on_ro_check(self):
        """Handle read-only checkbox change"""
        is_readonly = self.check_var.get() == 1
        self.run_button_text.set("Check" if is_readonly else "Patch")
        if self.on_ro_check:
            self.on_ro_check(is_readonly)
        return is_readonly
    
    def browse_for_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory(initialdir="/", title="Select Music Folder...")
        if directory:
            self.selected_directory = directory
            self.status_text2.set(directory)
            self.update_text_area(f"WavPatcher 0.9.2b \n\nFolder = {directory}\n\nCalculating total files..\n\n")
        return directory
    
    def update_text_area(self, text, append=False):
        """Update the text area with the given text"""
        self.text_area.configure(state=tk.NORMAL)
        if not append:
            self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state=tk.DISABLED)
    
    def update_status(self, text):
        """Update the status bar text"""
        self.status_text.set(text)
    
    def set_button_states(self, enabled):
        """Enable or disable buttons"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.run_button['state'] = state
        self.check_box['state'] = state
        self.browse_button['state'] = state
    
    def enable_run_button(self, enabled=True):
        """Enable or disable the run button"""
        self.run_button['state'] = tk.NORMAL if enabled else tk.DISABLED
    
    def start(self):
        """Start the GUI main loop"""
        self.root.mainloop()
    
    def _get_welcome_text(self):
        """Return the welcome text"""
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
