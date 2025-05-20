import sys
from src.core.gui import WavPatcherGUI
from src.core.wav_processor import WavProcessor

class WavPatcherApp:
    def __init__(self):
        # Create the WAV processor
        self.processor = WavProcessor(
            status_callback=self._on_status_update,
            progress_callback=self._on_progress_update
        )

        # Create the GUI
        self.gui = WavPatcherGUI(
            on_browse=self._on_browse,
            on_run=self._on_run,
            on_ro_check=self._on_ro_check
        )

        # Initialize state
        self.selected_directory = ""
        self.simulate_mode = True

    def _on_browse(self):
        """Handle browse button click"""
        directory = self.gui.browse_for_directory()
        if directory:
            self.selected_directory = directory
            total_files = self.processor.count_total_files(directory)

            if total_files == 0:
                self.gui.update_text_area("No *.wav files could be found!", append=True)
                self.gui.enable_run_button(False)
            else:
                self.gui.update_text_area(f"{total_files} *.wav files will be scanned.", append=True)
                self.gui.enable_run_button(True)

    def _on_run(self):
        """Handle run button click"""
        if self.selected_directory:
            self.gui.set_button_states(False)
            self.processor.start_processing_thread(
                self.selected_directory,
                self.simulate_mode,
                completion_callback=self._on_processing_complete
            )

    def _on_processing_complete(self, result):
        """Handle completion of processing"""
        self.gui.set_button_states(True)

    def _on_ro_check(self, is_readonly):
        """Handle read-only checkbox change"""
        self.simulate_mode = is_readonly

    def _on_status_update(self, message):
        """Handle status updates from the processor"""
        self.gui.update_text_area(message, append=True)

    def _on_progress_update(self, message):
        """Handle progress updates from the processor"""
        self.gui.update_status(message)

    def run(self):
        """Run the application"""
        self.gui.start()
        sys.exit()
