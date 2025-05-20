from pathlib import Path
import threading

class WavProcessor:
    def __init__(self, status_callback=None, progress_callback=None):
        self.status_callback = status_callback
        self.progress_callback = progress_callback
        self.processed_files = 0
        self.extensible_files = 0

    def count_total_files(self, directory):
        """Count the total number of WAV files in the directory"""
        total_files = 0
        for _ in Path(directory).rglob('*.wav'):
            total_files += 1
        return total_files

    def process_files(self, directory, simulate=True):
        """Process all WAV files in the directory"""
        # Reset counters
        self.processed_files = 0
        self.extensible_files = 0

        # Count total files
        total_files = self.count_total_files(directory)

        if total_files == 0:
            if self.status_callback:
                self.status_callback("No *.wav files could be found!")
            return 0, 0

        # Determine read/write mode
        rwmode = "rb" if simulate else "rb+"

        # Process each file
        for path in Path(directory).rglob('*.wav'):
            with open(path, rwmode) as f:
                self.processed_files += 1
                f.seek(20, 0)
                format_id = f.read(2)
                bint = int.from_bytes(format_id, byteorder='little', signed=False)

                if bint == 65534:  # Extensible flag
                    self.extensible_files += 1
                    if self.status_callback:
                        self.status_callback(f"\next_flag in: {path.name}")

                    if not simulate:
                        f.seek(-2, 1)
                        f.write(b'\x01\x00')

                # Update progress
                if self.progress_callback:
                    progress = self.processed_files / total_files * 100
                    progress_rounded = round(progress, 1)
                    self.progress_callback(
                        f"{progress_rounded}% : {self.processed_files}/{total_files} (ext: {self.extensible_files})"
                    )

        # Final status update
        if self.status_callback:
            self.status_callback("\n\n~~~~~~~~DONE~~~~~~~ \n\n")
            if self.extensible_files == 0:
                self.status_callback("No extensible flags detected")

        return self.processed_files, self.extensible_files

    def start_processing_thread(self, directory, simulate=True, completion_callback=None):
        """Start processing in a separate thread"""
        def process_and_notify():
            result = self.process_files(directory, simulate)
            if completion_callback:
                completion_callback(result)

        thread = threading.Thread(target=process_and_notify)
        thread.start()
        return thread
