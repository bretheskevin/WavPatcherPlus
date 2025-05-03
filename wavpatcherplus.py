import audioop
import os
import sys
import threading
import wave
from pathlib import Path
from tkinter import *
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText

def resource_path(relative):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath('.')
    return os.path.join(base, relative)

if sys.platform.startswith('win'):
    ffmpeg_exe = resource_path('ffmpeg/win/ffmpeg.exe')
    ffprobe_exe = resource_path('ffmpeg/win/ffprobe.exe')
elif sys.platform == 'darwin':
    ffmpeg_exe = resource_path('ffmpeg/mac/ffmpeg')
    ffprobe_exe = resource_path('ffmpeg/mac/ffprobe')
else:
    ffmpeg_exe = resource_path('ffmpeg/linux/ffmpeg')
    ffprobe_exe = resource_path('ffmpeg/linux/ffprobe')

os.environ['PATH'] = os.path.dirname(ffmpeg_exe) + os.pathsep + os.environ.get('PATH', '')
os.environ['FFMPEG_BINARY'] = ffmpeg_exe
os.environ['FFPROBE_BINARY'] = ffprobe_exe

from pydub import AudioSegment
from pydub.utils import mediainfo

AudioSegment.converter = ffmpeg_exe
AudioSegment.ffmpeg = ffmpeg_exe
AudioSegment.ffprobe = ffprobe_exe

class WavPatcherApp:
    VERSION = '1.0.0'

    def __init__(self, root):
        self.root = root
        root.title('WavPatcherPlus ' + self.VERSION)
        root.resizable(0, 0)
        root.iconbitmap(resource_path('img/wavico.ico'))
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=BOTH, expand=True)
        self.tab_patch = Frame(self.notebook)
        self.notebook.add(self.tab_patch, text='Patch')
        self.build_patch_tab()
        self.tab_downsample = Frame(self.notebook)
        self.notebook.add(self.tab_downsample, text='Downsample')
        self.build_downsample_tab()

    def build_patch_tab(self):
        frame = self.tab_patch
        self.st_patch = ScrolledText(frame, wrap=WORD, height=30, width=56, state=DISABLED)
        self.st_patch.grid(row=0, column=0, rowspan=4, padx=4, pady=4)
        sec = Frame(frame)
        sec.grid(row=0, column=1, padx=4, pady=4, sticky=N)
        Button(sec, text='Browse...', width=12, height=2, command=self.browse_patch).grid(row=1, pady=4)
        self.btn_patch_txt = StringVar()
        self.btn_patch = Button(sec, textvariable=self.btn_patch_txt, width=12, height=2, state=DISABLED, command=lambda: threading.Thread(target=self.run_patch).start())
        self.btn_patch.grid(row=2, pady=4)
        self.chkpatch = IntVar(value=1)
        Checkbutton(sec, text='Read-only', variable=self.chkpatch, onvalue=1, offvalue=0, command=self.update_patch_mode).grid(row=3, pady=8)
        sf = Frame(frame)
        sf.grid(row=4, column=0, columnspan=2, sticky=NW+E)
        self.loc_patch = StringVar()
        Label(sf, textvariable=self.loc_patch, bd=1, relief=GROOVE).pack(fill=X)
        self.prog_patch = StringVar()
        Label(sf, textvariable=self.prog_patch, bd=1, relief=GROOVE).pack(fill=X)
        self.update_patch_mode()
        self.log_patch_intro()

    def build_downsample_tab(self):
        frame = self.tab_downsample
        self.st_conv = ScrolledText(frame, wrap=WORD, height=30, width=56, state=DISABLED)
        self.st_conv.grid(row=0, column=0, rowspan=6, padx=4, pady=4)
        sec = Frame(frame)
        sec.grid(row=0, column=1, padx=4, pady=4, sticky=N)
        Button(sec, text='Browse...', width=12, height=2, command=self.browse_downsample).grid(row=1, pady=4)
        self.btn_conv_txt = StringVar()
        self.btn_conv = Button(sec, textvariable=self.btn_conv_txt, width=12, height=2, state=DISABLED, command=lambda: threading.Thread(target=self.run_downsample).start())
        self.btn_conv.grid(row=2, pady=4)
        self.chkconv = IntVar(value=1)
        Checkbutton(sec, text='Read-only', variable=self.chkconv, onvalue=1, offvalue=0, command=self.update_downsample_mode).grid(row=3, pady=8)
        sf = Frame(frame)
        sf.grid(row=6, column=0, columnspan=2, sticky=NW+E)
        self.loc_downsample = StringVar()
        Label(sf, textvariable=self.loc_downsample, bd=1, relief=GROOVE).pack(fill=X)
        self.prog_conv = StringVar()
        Label(sf, textvariable=self.prog_conv, bd=1, relief=GROOVE).pack(fill=X)
        self.update_downsample_mode()

    def update_patch_mode(self):
        self.sim_patch = bool(self.chkpatch.get())
        self.btn_patch_txt.set('Check' if self.sim_patch else 'Patch')

    def browse_patch(self):
        self.BrowseLoc = filedialog.askdirectory(title='Select Music Folder...')
        if not self.BrowseLoc:
            return
        self.log_patch(f"Folder = {self.BrowseLoc}\nCalculating total files..")
        total = sum(1 for _ in Path(self.BrowseLoc).rglob('*.wav'))
        self.loc_patch.set(self.BrowseLoc)
        if total == 0:
            self.btn_patch.config(state=DISABLED)
            self.log_patch('No *.wav files could be found!')
        else:
            self.btn_patch.config(state=NORMAL)
            self.log_patch(f"{total} *.wav files will be scanned.")

    def run_patch(self):
        self.btn_patch.config(state=DISABLED)
        total = sum(1 for _ in Path(self.BrowseLoc).rglob('*.wav'))
        i, ext = 0, 0
        mode = 'rb' if self.sim_patch else 'rb+'
        for p in Path(self.BrowseLoc).rglob('*.wav'):
            with open(p, mode) as f:
                i += 1
                f.seek(20)
                if int.from_bytes(f.read(2), 'little') == 65534:
                    ext += 1
                    self.root.after(0, lambda p=p: self.log_patch(f"ext_flag in: {p.name}"))
                    if not self.sim_patch:
                        f.seek(-2, 1)
                        f.write(b'\x01\x00')
            self.root.after(0, lambda i=i, ext=ext: self.prog_patch.set(f"{round(i/total*100,1)}% : {i}/{total} (ext: {ext})"))
        self.root.after(0, lambda: self.log_patch('\n~~~~~~~~DONE~~~~~~~'))
        if ext == 0:
            self.root.after(0, lambda: self.log_patch('No extensible flags detected'))
        self.root.after(0, lambda: self.btn_patch.config(state=NORMAL))

    def log_patch_intro(self):
        hdr = (
               "  _    _            ______     _       _               \n"
               " | |  | |           | ___ \\   | |     | |  " + self.VERSION + "            \n"
               " | |  | | __ ___   _| |_/ /_ _| |_ ___| |__   ___ _ __ \n"
               " | |/\\| |/ _` \\ \\ / /  __/ _` | __/ __| '_ \\ / _ \\ '__|\n"
               " \\  /\\  / (_| |\\ V /| | | (_| | || (__| | | |  __/ |   \n"
               "  \\/  \\/ \\__,_| \\_/ \\_|  \\__,_|\\__\\___|_| |_|\\___|_|   \n"
               " ____  _           \n"
               "|  _ \\| |_   _ ___ \n"
               "| |_) | | | | / __|\n"
               "|  __/| | |_| \\__ \\\n"
               "|_|   |_|\\__,_|___/\n"
               "========================================================\n"
       )
        self.st_patch.config(state=NORMAL)
        self.st_patch.insert(END, hdr + "Select 'Read-only' to simulate or uncheck to patch.\n")
        self.st_patch.config(state=DISABLED)

    def log_patch(self, msg):
        self.st_patch.config(state=NORMAL)
        self.st_patch.insert(END, msg + "\n")
        self.st_patch.see(END)
        self.st_patch.config(state=DISABLED)

    def update_downsample_mode(self):
        self.sim_conv = bool(self.chkconv.get())
        self.btn_conv_txt.set('Check' if self.sim_conv else 'Downsample')

    def browse_downsample(self):
        self.DownsampleLoc = filedialog.askdirectory(title='Select Audio Folder...')
        if not self.DownsampleLoc:
            return
        self.st_conv.config(state=NORMAL)
        self.st_conv.delete('1.0', END)
        self.st_conv.config(state=DISABLED)
        threading.Thread(target=self._scan_downsample_folder, daemon=True).start()

    def _scan_downsample_folder(self):
        self.files_to_downsample = []
        base = Path(self.DownsampleLoc)
        total = sum(1 for _ in base.rglob('*') if _.suffix.lower() in ['.wav','.mp3'])
        processed = 0
        for p in base.rglob('*.wav'):
            try:
                with wave.open(str(p), 'rb') as wf:
                    if wf.getframerate() == 48000:
                        self.files_to_downsample.append(p)
                        self.root.after(0, lambda p=p: self.log_conv(f"Found WAV: {p.name}"))
            except:
                pass
            processed += 1
            self.root.after(0, lambda processed=processed, total=total: self.prog_conv.set(f"Scanning: {processed}/{total}"))
        for p in base.rglob('*.mp3'):
            try:
                audio = AudioSegment.from_file(str(p))
                if audio.frame_rate == 48000:
                    self.files_to_downsample.append(p)
                    self.root.after(0, lambda p=p: self.log_conv(f"Found MP3: {p.name}"))
            except:
                pass
            processed += 1
            self.root.after(0, lambda processed=processed, total=total: self.prog_conv.set(f"Scanning: {processed}/{total}"))
        self.root.after(0, self._on_scan_complete)

    def _on_scan_complete(self):
        if self.files_to_downsample:
            self.btn_conv.config(state=NORMAL)
            self.log_conv(f"Total files to process: {len(self.files_to_downsample)}")
        else:
            self.log_conv('No 48 kHz WAV or MP3 files found!')

    def run_downsample(self):
        self.btn_conv.config(state=DISABLED)
        c = 0
        total = len(self.files_to_downsample)
        for p in self.files_to_downsample:
            try:
                rel = os.path.relpath(p.parent, self.DownsampleLoc)
                dest_dir = os.path.join(self.DownsampleLoc, 'WPPdownsample', rel)
                os.makedirs(dest_dir, exist_ok=True)
                if p.suffix.lower() == '.wav':
                    with wave.open(str(p), 'rb') as wf:
                        data = wf.readframes(wf.getnframes())
                        out, _ = audioop.ratecv(data, wf.getsampwidth(), wf.getnchannels(), 48000, 44100, None)
                    if not self.sim_conv:
                        dp = os.path.join(dest_dir, p.name)
                        with wave.open(dp, 'wb') as w2:
                            w2.setnchannels(wf.getnchannels())
                            w2.setsampwidth(wf.getsampwidth())
                            w2.setframerate(44100)
                            w2.writeframes(out)
                elif p.suffix.lower() == '.mp3':
                    audio = AudioSegment.from_file(str(p))
                    audio_44100 = audio.set_frame_rate(44100)
                    if not self.sim_conv:
                        dp = os.path.join(dest_dir, p.name)
                        info = mediainfo(str(p))
                        br = info.get('bit_rate')
                        if br:
                            kb = int(br) // 1000
                            bitrate_arg = f"{kb}k"
                            audio_44100.export(dp, format='mp3', bitrate=bitrate_arg)
                        else:
                            audio_44100.export(dp, format='mp3')
                c += 1
                self.root.after(0, lambda c=c, total=total, rel=rel, p=p: self.log_conv(f"Processed: {rel}/{p.name} ({c}/{total})"))
            except Exception as e:
                self.root.after(0, lambda p=p, e=e: self.log_conv(f"Error processing {p.name}: {e}"))
        self.root.after(0, lambda: self.log_conv('Completed.'))
        self.root.after(0, lambda: self.btn_conv.config(state=NORMAL))

    def log_conv(self, msg):
        self.st_conv.config(state=NORMAL)
        self.st_conv.insert(END, msg + "\n")
        self.st_conv.see(END)
        self.st_conv.config(state=DISABLED)

if __name__ == '__main__':
    root = Tk()
    app = WavPatcherApp(root)
    root.mainloop()
    sys.exit()
