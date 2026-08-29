# acuvi

A real-time, music-synchronized LED/light visualizer.

## Backstory

acuvi started as a hobby project by two university students who wanted to
practice their Python skills. The idea was a shared annoyance: at most events, the automated visualization is only loosely reacting to the volume. Not being satisfied with that, we wanted to build a system that treats sound as a spectrum of frequencies changing every fraction of a second. acuvi listens to live audio, breaks it down into a frequency spectrum mapped
onto musical (piano-key) intervals and turns that into a color and brightness pattern that follows the music in real time, smoothed just enough to look appealing to the eye.

## How it works

```
microphone --> FFT (piano-key frequency bins) --> color mapping --> LED strip / on-screen display
```

1. **Audio capture** (`audioIn.py`) runs in its own process and streams raw audio chunks
   from the system's audio input into a queue, using PyAudio.
2. **Frequency analysis** (`fftWorker.py`) runs an FFT on a rolling window of recent audio
   and buckets the result by musical note (piano key).
   Output is normalized against a rolling average of recent volume.
3. **Color mapping** (`visualizer.py`) maps each frequency bin to an RGB color based on its
   position in the spectrum, and applies temporal smoothing (configurable rise/fall rates). gain/exponent curve and independent
   low/high scaling let you shape the response.
4. **Output** (`acuvi.py`) downmixes the full-resolution spectrum onto the physical LED
   layout (an outer/middle/inner ring arrangement) or an on-screen grid, and pushes a new
   frame out at 147 Hz.
5. **Live tuning** (`server.py`) is a small Dash web UI with sliders for brightness,
   smoothing, and gain. It writes to `data.csv`, which the visualizer reloads periodically so you can adjust the look live.

Two passes run per frame: One over a longer audio window for the overall spectrum, and another one over just the most recent samples so percussive highs stay responsive even with heavier smoothing on the main pass.

## Hardware modes

`acuvi.py` supports two output modes, set via the `MODE` constant at the top of the file:

- `MODE = 0` - drives a physical LED strip over SPI (via `board` / `neopixel_spi`),
  originally run on a Raspberry Pi / Jetson Nano.
- `MODE = 1` - renders to an on-screen grid of colored squares (`rgbDisplay.py`) using
  Tkinter, useful for development without any LED hardware attached.

## Running it

```bash
pip install -r requirements.txt
```

If you're using the physical LED output (`MODE = 0`), also install the SPI/LED
dependencies listed (commented out) at the bottom of `requirements.txt` - these are
platform-specific.

Start the visualizer:

```bash
python acuvi.py
```

By default it listens on audio input device index 11 (see `audioIn.py`) - you'll likely
need to change this to match your system's microphone/line-in device index.

Optionally, start the live tuning UI in a separate terminal:

```bash
python server.py
```

Then open `http://localhost:8008/dash/` to adjust brightness, smoothing, and gain while
acuvi is running.

## Project layout

| File | Responsibility |
|---|---|
| `acuvi.py` | Main entry point: audio buffering, LED-layout downmixing, output loop |
| `audioIn.py` | Live audio capture (PyAudio), runs in its own process |
| `audioWorker.py` | Combines the FFT and color-mapping steps for one audio chunk |
| `fftWorker.py` | FFT + mapping of frequencies onto piano-key bins, with normalization |
| `visualizer.py` | Frequency-to-color mapping and temporal smoothing |
| `rgbDisplay.py` | Tkinter-based on-screen LED stand-in for development |
| `server.py` | Dash/Flask UI for live-tuning visualization parameters |
| `sharedFunctions.py` | Small shared helpers (color conversion, clamping) |
| `data.csv` | Current tunable parameters (brightness, smoothing, gain), shared between `visualizer.py` and `server.py` |
