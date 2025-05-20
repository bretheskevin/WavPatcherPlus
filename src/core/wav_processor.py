from pathlib import Path
import threading
import os
import shutil

class WavProcessor:
    def __init__(self, status_callback=None, progress_callback=None):
        self.status_callback = status_callback
        self.progress_callback = progress_callback
        self.processed_files = 0
        self.extensible_files = 0
        self.high_bit_depth_files = 0

    def count_total_files(self, directory):
        total_files = 0
        for _ in Path(directory).rglob('*.wav'):
            total_files += 1
        return total_files

    def process_files(self, directory, simulate=True):
        self.processed_files = 0
        self.extensible_files = 0
        self.high_bit_depth_files = 0

        total_files = self.count_total_files(directory)

        if total_files == 0:
            if self.status_callback:
                self.status_callback("No *.wav files could be found!")
            return 0, 0

        rwmode = "rb" if simulate else "rb+"

        for path in Path(directory).rglob('*.wav'):
            try:
                with open(path, rwmode) as f:
                    self.processed_files += 1
                    f.seek(20, 0)
                    format_id = f.read(2)
                    bint = int.from_bytes(format_id, byteorder='little', signed=False)

                    if bint == 65534:
                        self.extensible_files += 1
                        if self.status_callback:
                            self.status_callback(f"\next_flag in: {path.name}")

                        if not simulate:
                            f.seek(-2, 1)
                            f.write(b'\x01\x00')

                    if self.progress_callback:
                        progress = self.processed_files / total_files * 100
                        progress_rounded = round(progress, 1)
                        self.progress_callback(
                            f"{progress_rounded}% : {self.processed_files}/{total_files} (ext: {self.extensible_files})"
                        )
            except PermissionError:
                if self.status_callback:
                    self.status_callback(f"\nERROR: Cannot access file (in use by another process): {path.name}")

        if self.status_callback:
            self.status_callback("\n\n~~~~~~~~DONE~~~~~~~ \n\n")
            if self.extensible_files == 0:
                self.status_callback("No extensible flags detected")

        return self.processed_files, self.extensible_files

    def start_processing_thread(self, directory, simulate=True, completion_callback=None):
        def process_and_notify():
            result = self.process_files(directory, simulate)
            if completion_callback:
                completion_callback(result)

        thread = threading.Thread(target=process_and_notify)
        thread.start()
        return thread

    def find_high_bit_depth_files(self, directory):
        self.processed_files = 0
        self.high_bit_depth_files = 0

        total_files = self.count_total_files(directory)

        if total_files == 0:
            if self.status_callback:
                self.status_callback("No *.wav files could be found!")
            return 0, 0

        output_dir = os.path.join(directory, "WPPtoconvert")
        output_dir_created = False

        for path in Path(directory).rglob('*.wav'):
            try:
                with open(path, "rb") as f:
                    self.processed_files += 1

                    f.seek(12)

                    while True:
                        chunk_id = f.read(4)
                        if not chunk_id:
                            break

                        if chunk_id == b'fmt ':
                            chunk_size = int.from_bytes(f.read(4), byteorder='little', signed=False)
                            format_type = int.from_bytes(f.read(2), byteorder='little', signed=False)
                            channels = int.from_bytes(f.read(2), byteorder='little', signed=False)
                            sample_rate = int.from_bytes(f.read(4), byteorder='little', signed=False)
                            byte_rate = int.from_bytes(f.read(4), byteorder='little', signed=False)
                            block_align = int.from_bytes(f.read(2), byteorder='little', signed=False)
                            bits_per_sample = int.from_bytes(f.read(2), byteorder='little', signed=False)

                            if bits_per_sample >= 32:
                                self.high_bit_depth_files += 1
                                if self.status_callback:
                                    self.status_callback(f"\nHigh bit depth ({bits_per_sample} bits) in: {path.name}")

                                if not output_dir_created:
                                    try:
                                        if not os.path.exists(output_dir):
                                            os.makedirs(output_dir)
                                            if self.status_callback:
                                                self.status_callback(f"\nCreated output directory: {output_dir}")
                                        output_dir_created = True
                                    except PermissionError:
                                        if self.status_callback:
                                            self.status_callback(f"\nERROR: Cannot create directory (permission denied): {output_dir}")
                                        continue

                                output_path = os.path.join(output_dir, path.name)
                                try:
                                    shutil.copy2(path, output_path)
                                    if self.status_callback:
                                        self.status_callback(f"\nCopied to: {output_path}")
                                except PermissionError:
                                    # Check if the file was actually copied despite the error
                                    if os.path.exists(output_path):
                                        if self.status_callback:
                                            self.status_callback(f"\nFile was copied successfully despite being in use: {path.name}")
                                    else:
                                        if self.status_callback:
                                            self.status_callback(f"\nERROR: Cannot copy file (in use by another process): {path.name}")

                            break
                        else:
                            chunk_size = int.from_bytes(f.read(4), byteorder='little', signed=False)
                            f.seek(chunk_size, 1)

                    if self.progress_callback:
                        progress = self.processed_files / total_files * 100
                        progress_rounded = round(progress, 1)
                        self.progress_callback(
                            f"{progress_rounded}% : {self.processed_files}/{total_files} (high bit: {self.high_bit_depth_files})"
                        )
            except PermissionError:
                if self.status_callback:
                    self.status_callback(f"\nERROR: Cannot access file (in use by another process): {path.name}")

        if self.status_callback:
            self.status_callback("\n\n~~~~~~~~DONE~~~~~~~ \n\n")
            if self.high_bit_depth_files == 0:
                self.status_callback("No high bit depth files detected")

        return self.processed_files, self.high_bit_depth_files

    def start_high_bit_depth_thread(self, directory, completion_callback=None):
        def process_and_notify():
            result = self.find_high_bit_depth_files(directory)
            if completion_callback:
                completion_callback(result)

        thread = threading.Thread(target=process_and_notify)
        thread.start()
        return thread
