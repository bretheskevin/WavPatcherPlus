#!/usr/bin/env python3
"""
WavPatcher - A tool to fix WAV_EXTENSIBLE header subchunks in WAV files
"""

from app import WavPatcherApp

if __name__ == "__main__":
    app = WavPatcherApp()
    app.run()
