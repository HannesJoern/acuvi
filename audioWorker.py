"""Combines FFT analysis and color visualization into a single per-chunk processing step."""

import numpy as np

import fftWorker
import visualizer


class audioWorkerino:
    """Runs one audio chunk through the FFT stage and then the visualization stage."""

    def __init__(self, RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS):
        self.RATE = RATE
        self.RATE_INTENSITY = RATE_INTENSITY
        self.RATE_FREQUENCY = RATE_FREQUENCY
        self.NUM_PIXELS = NUM_PIXELS

        self.visual_processor = visualizer.Visualizer(RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS)
        self.fft_processor = fftWorker.fftWorkerino(RATE, RATE_FREQUENCY, NUM_PIXELS)

    def audioWorker(self, waveform):
        """Take a raw audio waveform chunk and return one frame of RGB pixel values."""
        frequency_dist = self.fft_processor.fftWorker(waveform)
        visualization = self.visual_processor.visualize(waveform, frequency_dist)
        return visualization
