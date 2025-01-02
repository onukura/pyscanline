import os

import imageio
import numpy as np
import pytest
from PIL import Image

from pyscanline.core import (
    convert_frames_to_gif,
    flatten_frames,
    scanline,
    scanline_gif,
)


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "L"])
def test_scanline_single_image(mode):
    """
    Test the `scanline` function on a single static image of various modes (RGB, RGBA, L).
    """
    # 1) Create a small in-memory image
    width, height = 50, 40
    if mode == "RGB":
        color = (255, 0, 0)  # Red
    elif mode == "RGBA":
        color = (0, 255, 0, 128)  # Semi-transparent green
    else:
        color = 128  # Gray for "L"

    img = Image.new(mode, (width, height), color)

    # 2) Call `scanline()` with default parameters (or set some custom ones)
    result = scanline(img)

    # 3) Check the result is a Pillow Image
    assert isinstance(result, Image.Image), "scanline() should return a Pillow Image"

    # 4) Ensure output size matches
    #    (Note: the final code might alter size due to internal logic,
    #     but here we expect the same dimension if we haven't changed default n_scanlines)
    #    Actually, scanline() does resize to n_scanlines in height. If 'mode == L', it converts internally, etc.
    #    We'll just check result is an image of some nonzero size.
    assert result.width > 0 and result.height > 0, "scanline() produced an invalid size"

    # 5) Optionally check final mode is "RGBA" (since the code typically ends in RGBA)
    assert (
        result.mode == "RGBA"
    ), "Expected the result to be in RGBA mode after scanline"


def test_scanline_gif(tmp_path):
    """
    Test the `scanline_gif` function using a small multi-frame GIF created in memory.
    """
    # 1) Create a couple of frames (RGBA)
    frame0 = Image.new("RGBA", (32, 32), (255, 0, 0, 255))  # Red
    frame1 = Image.new("RGBA", (32, 32), (0, 255, 0, 128))  # Semi-transparent green

    # 2) Convert frames to NumPy arrays, then save as a temporary GIF
    frames_np = [np.array(frame0), np.array(frame1)]
    gif_path = str(tmp_path / "test_input.gif")
    imageio.mimsave(gif_path, frames_np, duration=0.1)  # type: ignore # 2-frame GIF

    # 3) Call `scanline_gif` on that GIF
    frames, durations = scanline_gif(
        gif=gif_path,
        width=64,
        height=64,
        scale=1.0,
        fps=5,
        delay=None,  # use fps=5 => duration=0.2 seconds
        # You can pass additional scanline kwargs, e.g.:
        # opacities=(1.0, 0.6, 0.0, 0.0, 0.6, 1.0),
    )

    # 4) Check frames & durations
    assert len(frames) == 2, "Should return 2 processed frames"
    assert len(durations) == 2, "Should have 2 durations"
    for fr in frames:
        assert (
            fr.width > 0 and fr.height > 0
        ), "Output frames should have valid dimensions"

    # 5) Optionally save the processed frames as a new GIF to inspect manually
    out_gif_path = str(tmp_path / "test_output.gif")
    convert_frames_to_gif(frames, out_gif_path)
    assert os.path.exists(out_gif_path), "Output GIF file was not created"


def test_flatten_frames():
    """
    Test flatten_frames on a small sequence of images
    to ensure alpha-compositing is happening correctly.
    """
    # Create 2 frames RGBA
    f1 = Image.new("RGBA", (20, 20), (255, 0, 0, 255))  # solid red
    f2 = Image.new("RGBA", (20, 20), (0, 0, 255, 128))  # semi-trans blue

    flattened = flatten_frames([f1, f2])
    assert isinstance(
        flattened, Image.Image
    ), "flatten_frames should return a PIL.Image"

    # flattened should be 20x20, RGBA
    assert flattened.size == (20, 20)
    assert flattened.mode == "RGBA"

    # Optionally, we can check a pixel's RGBA value to see if it's alpha-composited as expected
    px = flattened.getpixel((10, 10))
    # This should be something in between red & blue depending on alpha.
    # For a 128 alpha on blue over 255 alpha red => a blend of red & blue
    # We won't do exact numeric check here, just see if it differs from pure red or pure blue
    # But you can add a more rigorous test if desired.
    assert px != (255, 0, 0, 255) and px != (
        0,
        0,
        255,
        128,
    ), "Pixel should be composited color, not raw."


def test_convert_frames_to_gif(tmp_path):
    """
    Test the helper function convert_frames_to_gif with 2 or more frames.
    """
    f1 = Image.new("RGBA", (16, 16), (255, 0, 0, 255))
    f2 = Image.new("RGBA", (16, 16), (0, 255, 0, 255))

    out_path = str(tmp_path / "converted.gif")
    convert_frames_to_gif([f1, f2], out_path)

    # Check the file is created
    assert os.path.isfile(
        out_path
    ), "convert_frames_to_gif did not create an output file"

    # Check that we can read it back as a GIF with 2 frames
    read_back = imageio.mimread(out_path)
    assert len(read_back) >= 2, "Output GIF should have at least 2 frames"
