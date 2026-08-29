"""acuvi main entry point.

Pipeline: microphone -> FFT (piano-key frequency bins) -> color mapping -> LED strip / on-screen display.

Audio capture runs in its own process (see audioIn.py) and streams raw PCM chunks through a
multiprocessing queue. The main process keeps a rolling buffer of the most recent audio,
runs it through two independent analysis passes at different time scales (a slower one for
the overall spectrum, a faster one for transient/high-frequency detail), maps the result to
colors, and pushes it out to either a physical LED strip or an on-screen grid for
testing/development.

Run with: python acuvi.py
"""

import time as tm

import numba
import numpy as np
from multiprocess import Process, Queue
import multiprocess

import audioIn
import audioWorker
from sharedFunctions import *

# 0 = physical LED strip (via USB SPI), 1 = on-screen Tkinter display (see rgbDisplay.py)
MODE = 0

# Audio/processing settings. The pipeline is tuned around these values - changing them
# may require re-tuning the visualization parameters in data.csv.
RATE = 44100                        # audio sample rate (Hz)
RATE_INTENSITY = 147                # analysis chunks per second for the main (slow) pass
RATE_FREQUENCY = 147                # analysis chunks per second used for frequency mapping
CHUNKSIZE = RATE / RATE_INTENSITY   # samples per audio chunk
NUM_PIXELS = 200                    # number of frequency bins produced by the FFT stage
ARRAY_SIZE = 50                     # length (in chunks) of the rolling audio history buffer

NUM_LEDS = 71                       # number of physical LEDs actually driven in mode 0


@numba.jit(nopython=True)
def transformVis(smol_visualization, fast_visualization, visualization):
    """Downmix the full-resolution frequency visualization onto the physical LED layout
    (71 LEDs arranged as an outer ring, a middle ring, and an inner ring), blending in a
    separately-computed fast/high-frequency pass for the inner ring so treble transients
    stay responsive even though the outer/middle rings use a slower, smoother analysis pass.
    """
    # Inner ring (LEDs 54-69): highs, using the fast-pass visualization.
    for j in range(16):
        for k in range(3):
            for l in range(50):
                if l >= 20:
                    smol_visualization[54 + j][k] += (1 / 20) * float(fast_visualization[80 + l][k]) * float(l) / 20
                else:
                    smol_visualization[54 + j][k] += (1 / 20) * float(fast_visualization[80 + l][k])

    # Middle ring (LEDs 31-52): mids.
    for j in range(22):
        for k in range(3):
            for l in range(70):
                if l < 10:
                    smol_visualization[31 + j][k] += (1 / 5) * float(visualization[30 + l][k]) * float(l - 10) / 10
                elif 20 <= l < 50:
                    smol_visualization[31 + j][k] += (1 / 5) * float(visualization[30 + l][k])
                elif l > 50:
                    smol_visualization[31 + j][k] += (1 / 5) * float(visualization[30 + l][k]) * float(70 - l) / 10

    # Outer ring (LEDs 1-27): lows.
    for j in range(27):
        for k in range(3):
            for l in range(60):
                if l < 40:
                    smol_visualization[1 + j][k] += (1 / 10) * float(visualization[l][k])
                else:
                    smol_visualization[1 + j][k] += (1 / 10) * float(visualization[l][k]) * float(60 - l) / 20

    return smol_visualization


def init_output(mode):
    """Initialize whichever output device the configured mode needs and return a handle
    (a NeoPixel strip object for mode 0, an RGB_display object for mode 1)."""
    if mode == 0:
        # Imported here rather than at module level: importing these before the SPI device
        # is otherwise touched can trip a libusb access bug on some setups.
        import board
        import neopixel_spi as neopixel

        spi = board.SPI()
        return neopixel.NeoPixel_SPI(spi, NUM_LEDS, brightness=1, pixel_order=neopixel.GRB, auto_write=False)
    else:
        import rgbDisplay

        display = rgbDisplay.RGB_display(12, 4)
        display.createRgbDisplay()
        return display


def render_leds(pixels, visualization, fast_visualization):
    """Compute one frame for the physical LED strip and push it out."""
    smol_visualization = np.zeros((NUM_LEDS, 3), dtype=float)
    smol_visualization = transformVis(smol_visualization, fast_visualization, visualization)

    for i in range(NUM_LEDS):
        hex_val = rgb_to_hex(smol_visualization[i][0], smol_visualization[i][1], smol_visualization[i][2])
        pixels[i] = int(hex_val, 16)
    pixels.show()


def render_display(display, visualization, fast_visualization):
    """Compute one frame for the on-screen Tkinter display and push it out."""
    smol_visualization = np.zeros((48, 3), dtype=float)

    for i in range(5):
        for j in range(11):
            for k in range(3):
                smol_visualization[24 + j][k] += float(visualization[3 * 12 + i * 12 + j][k]) / 2
    for i in range(5):
        for j in range(11):
            for k in range(3):
                smol_visualization[12 + j][k] += float(fast_visualization[3 * 12 + i * 12 + j][k]) / 2
    for i in range(3):
        for j in range(11):
            for k in range(3):
                smol_visualization[36 + j][k] += float(visualization[i * 12 + j][k])
    for i in range(4):
        for j in range(11):
            for k in range(3):
                smol_visualization[j][k] += float(visualization[8 * 12 + i + j * 4][k])

    hex_display_vals = np.array([rgb_to_hex_display(0, 0, 0) for _ in range(48)])
    for i in range(48):
        if i < NUM_PIXELS:
            hex_display_vals[i] = rgb_to_hex_display(
                int(smol_visualization[i][0]), int(smol_visualization[i][1]), int(smol_visualization[i][2])
            )
    display.colorSquares(hex_display_vals)
    display.update()


def main():
    multiprocess.freeze_support()  # required on Windows for multiprocessing to work correctly

    # Queues used to pass raw audio chunks between the audio-capture process and this one.
    audio_in_queue = Queue()
    audio_out_queue = Queue()

    # Two independent analysis pipelines: a normal-speed one and a "fast" one used to keep
    # transients (e.g. percussive highs) responsive even though the main pass is smoothed.
    audio_processor = audioWorker.audioWorkerino(RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS)
    fast_audio_processor = audioWorker.audioWorkerino(RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS)

    audio_in = audioIn.AudioIn(RATE, RATE_INTENSITY, audio_in_queue, audio_out_queue)
    audio_in_worker = Process(target=audio_in.audioInWorker, args=())
    audio_in_worker.start()

    output_device = init_output(MODE)

    # Rolling buffer of recent raw audio samples, used as the input window for the FFT.
    last_audiosamples = np.zeros((int(CHUNKSIZE * ARRAY_SIZE),))
    list_init = False
    rotary_idx = 0

    try:
        while True:
            # Wait for the audio process to produce at least one chunk.
            while audio_in_queue.empty():
                tm.sleep(0.0005)

            # Fill the rolling buffer before doing any real analysis.
            while not list_init:
                while audio_in_queue.empty():
                    tm.sleep(0.0005)
                byte_data = audio_in_queue.get()
                np_data = np.frombuffer(byte_data, dtype=np.int16)
                last_audiosamples[: int((ARRAY_SIZE - 1) * CHUNKSIZE)] = last_audiosamples[int(CHUNKSIZE):]
                last_audiosamples[int((ARRAY_SIZE - 1) * CHUNKSIZE):] = np_data
                rotary_idx += 1
                if rotary_idx == (ARRAY_SIZE - 1):
                    list_init = True

            # Drain any chunks that arrived since the last frame. If more than one is
            # waiting, we've fallen behind real-time audio capture.
            chunks_read = 0
            while not audio_in_queue.empty():
                chunks_read += 1
                byte_data = audio_in_queue.get()
                np_data = np.frombuffer(byte_data, dtype=np.int16)
                last_audiosamples[: int((ARRAY_SIZE - 1) * CHUNKSIZE)] = last_audiosamples[int(CHUNKSIZE):]
                last_audiosamples[int((ARRAY_SIZE - 1) * CHUNKSIZE):] = np_data
            if chunks_read > 1:
                print("overrun: fell behind by", chunks_read - 1, "chunk(s)")

            # Slow pass over the full history window, fast pass over just the most recent samples.
            visualization = audio_processor.audioWorker(last_audiosamples[int((ARRAY_SIZE - 50) * CHUNKSIZE):])
            fast_visualization = fast_audio_processor.audioWorker(last_audiosamples[int((ARRAY_SIZE - 10) * CHUNKSIZE):])

            if MODE == 0:
                render_leds(output_device, visualization, fast_visualization)
            else:
                render_display(output_device, visualization, fast_visualization)

    except KeyboardInterrupt:
        audio_in.terminate()


if __name__ == '__main__':
    multiprocess.freeze_support()
    main()
