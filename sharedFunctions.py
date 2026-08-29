"""Small utility functions shared across the acuvi audio/visualization pipeline."""


def clamp(value):
    """Clamp a numeric value to the valid 8-bit color range [0, 255]."""
    if value < 0:
        return 0
    if value > 255:
        return 255
    return int(value)


def rgb_to_hex(r, g, b):
    """Convert an RGB triple to the '0xRRGGBB' string format expected by the LED strip driver."""
    return '0x{:02x}{:02x}{:02x}'.format(clamp(r), clamp(g), clamp(b))


def rgb_to_hex_display(r, g, b):
    """Convert an RGB triple to the '#RRGGBB' string format expected by Tkinter (rgbDisplay.py)."""
    return "#%02x%02x%02x" % (clamp(r), clamp(g), clamp(b))


def val(value, max_value, threshold):
    """Clamp `value` to `max_value` from above and snap it to 1 if it falls below `threshold`."""
    if value > max_value:
        value = max_value
    if value < threshold:
        return 1
    return value


# Data format notes:
#
# vis_sample: a 1D array of length n (one entry per LED/pixel) containing the hexadecimal
#             RGB color for that pixel. Index i is the color of pixel i. For 2D LED layouts
#             (e.g. a grid), pixel 0 is the top-left and pixel n-1 is the bottom-right.
#
# visualization: a 2D array of vis_samples over time - i.e. a sequence of frames, each one
#                a vis_sample, produced once per audio processing step.
