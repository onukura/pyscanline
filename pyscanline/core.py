import imageio
import matplotlib.colors as mcolors
import numpy as np
from PIL import Image, ImageOps


def scanline(
    image: str | Image.Image,
    n_scanlines: int = 90,
    scanline_col: tuple[str, str, str, str] = (
        "black",
        "darkslategrey",
        "#b4eeb4",
        "paleturquoise",
    ),
    opacities: tuple[float, float, float, float, float, float] = (
        1.0,
        0.6,
        0.0,
        0.0,
        0.6,
        1.0,
    ),
    normalise: bool = False,
    border_size: int = 1,
    border_intensity: int = 255,
    frame_size: int = 10,
    vertical_filter: str = "point",
    horizontal_filter: str = "triangle",
    add_noise: bool = False,
    noise_type: str = "gaussian",
    print_details: bool = False,
) -> Image.Image:
    """
    A "scanline" effect similar to the Wand-based version, but implemented with
    PIL, NumPy, and matplotlib. This version avoids the Pillow fill-type error
    by correctly handling grayscale borders.

    Parameters
    ----------
    image: str | Image.Image,
        The input image path or PIL.Image object.
    n_scanlines : int
        The number of vertical scanlines (image height).
    scanline_col : tuple of str
        Colors for the colormap (dark -> light).
    opacities : tuple of float
        Alpha values for black lines (0=transparent, 1=opaque).
    normalise : bool
        Whether to normalize the grayscale image (simple min-max approach here).
    border_size : int
        Inner border width in 'scanlines' units (added as pure grayscale).
    border_intensity : int
        Brightness of inner border (0=black, 255=white).
    frame_size : int
        Outer frame size as a percentage of the final image dimension.
    vertical_filter : str
        Filter name for vertical resizing in Pillow.
    horizontal_filter : str
        Filter name for horizontal resizing in Pillow.
    add_noise : bool
        Whether to add noise. (This demo uses a simple gaussian noise if True).
    noise_type : str
        Type of noise (only "gaussian" is demonstrated).
    print_details : bool
        Whether to print details of the final image.

    Returns
    -------
    PIL.Image.Image
        The final image (RGBA) after applying the scanline effect.
    """

    # 1) Map our custom filter strings to PIL's resample flags
    filter_map = {
        "point": Image.Resampling.NEAREST,
        "triangle": Image.Resampling.BILINEAR,
    }
    v_filter = filter_map.get(vertical_filter.lower(), Image.Resampling.NEAREST)
    h_filter = filter_map.get(horizontal_filter.lower(), Image.Resampling.BILINEAR)

    # 2) Read the image using PIL
    if isinstance(image, str):
        img = Image.open(image).convert("RGB")
    else:
        img = image.convert("RGB")

    orig_w, orig_h = img.size

    # 3) Resize to height=n_scanlines while preserving aspect ratio
    if orig_h > 0:
        new_w = int(orig_w / orig_h * n_scanlines)
    else:
        new_w = 1
    img = img.resize((new_w, n_scanlines), resample=v_filter)

    # 4) Convert to grayscale ("L" mode)
    img_gray = ImageOps.grayscale(img)

    # (Optional) Normalize
    img_arr = np.array(img_gray, dtype=np.float32)
    if normalise:
        min_val = img_arr.min()
        max_val = img_arr.max()
        if max_val > min_val:
            img_arr = 255.0 * (img_arr - min_val) / (max_val - min_val)
    img_gray = Image.fromarray(img_arr.astype(np.uint8), mode="L")

    # 5) Add inner border (grayscale mode => fill must be int 0..255)
    if border_size > 0:
        shade = int(max(0, min(255, border_intensity)))
        img_gray = ImageOps.expand(img_gray, border=border_size, fill=shade)

    w, h = img_gray.size

    # 6) Apply a matplotlib colormap to the grayscale pixels
    cmap = mcolors.LinearSegmentedColormap.from_list("scanline_cmap", scanline_col)
    data = np.array(img_gray, dtype=np.uint8)
    norm_data = data / 255.0
    mapped_rgba = cmap(norm_data)  # shape => (h, w, 4)
    mapped_rgba_255 = (mapped_rgba * 255).astype(np.uint8)
    color_img = Image.fromarray(mapped_rgba_255, mode="RGBA")

    # 7) (Optional) add gaussian noise
    if add_noise and noise_type == "gaussian":
        arr_col = np.array(color_img, dtype=np.float32)
        noise = np.random.normal(loc=0.0, scale=15.0, size=arr_col.shape[:2])
        for ch in range(3):
            arr_col[..., ch] = np.clip(arr_col[..., ch] + noise, 0, 255)
        color_img = Image.fromarray(arr_col.astype(np.uint8), "RGBA")

    # 8) Resize (vertical first, then horizontal)
    l = len(opacities)
    color_img = color_img.resize(
        (color_img.width, color_img.height * l), resample=v_filter
    )
    color_img = color_img.resize(
        (color_img.width * l, color_img.height), resample=h_filter
    )

    final_w, final_h = color_img.size

    # 9) Create a scanline layer with black + varying alpha
    sl_list = [int(255.0 * a) for a in opacities]
    sl_arr = np.zeros((final_h, final_w, 4), dtype=np.uint8)
    for row in range(final_h):
        alpha_val = sl_list[row % l]
        sl_arr[row, :, 0] = 0  # R=0
        sl_arr[row, :, 1] = 0  # G=0
        sl_arr[row, :, 2] = 0  # B=0
        sl_arr[row, :, 3] = alpha_val

    scanline_layer = Image.fromarray(sl_arr, mode="RGBA")

    # 10) Composite the scanline layer over the color image
    base = color_img.convert("RGBA")
    overlay = scanline_layer.convert("RGBA")
    color_img = Image.alpha_composite(base, overlay)

    # 11) Add an outer frame (always black)
    frame_px = round(((n_scanlines * l) / 100.0) * frame_size)
    if frame_px > 0:
        color_img = ImageOps.expand(color_img, border=frame_px, fill=(0, 0, 0, 255))

    if print_details:
        w_out, h_out = color_img.size
        ar = h_out / w_out if w_out != 0 else 0
        print(f"Output width:  {w_out}")
        print(f"Output height: {h_out}")
        print(f"Aspect ratio (H/W): {ar:.3f}")

    return color_img


def flatten_frames(
    frames: list[Image.Image],
    background: tuple[float, float, float, float] = (0, 0, 0, 0),
) -> Image.Image:
    """
    Cumulative alpha-composite for a list of frames[0..i].

    Parameters
    ----------
    frames : list of PIL.Image
        Each frame must be RGBA or converted to RGBA.
    background : tuple(R, G, B, A)
        Background color for the initial blank image.

    Returns
    -------
    PIL.Image
        The cumulatively composited result (RGBA).
    """
    # Use the size of the first frame for the output canvas
    w, h = frames[0].size
    # Create a blank RGBA image as the base
    base = Image.new("RGBA", (w, h), background)

    # Composite each frame in order
    for f in frames:
        f_rgba = f.convert("RGBA")  # ensure RGBA
        base = Image.alpha_composite(base, f_rgba)

    return base


def scanline_gif(
    gif: str,
    width: int = 600,
    height: int = 600,
    scale: float = 1.0,
    fps: int = 10,
    delay: float | None = None,
    **scanline_kwargs,
) -> tuple[list[Image.Image], list[float]]:
    """
    Create a 'scanline' animation from a GIF (Python version).

    Parameters
    ----------
    gif : str
        Path to the GIF file.
    width : int
        Output width of each frame (before scaling).
    height : int
        Output height of each frame (before scaling).
    scale : float
        Multiply output width/height by this factor.
    fps : int
        Frames per second if delay is not given.
    delay : float | None
        Delay in 1/100 seconds. If None, we use fps. If float or list, we convert to seconds.
    **scanline_kwargs :
        Additional named arguments to pass to the scanline function.

    Returns
    -------
    Tuple[List[Image.Image], List[float]]
        The processed frames after applying flatten + scanline transformations and the per-frame durations.
    """
    print("This function is experimental in Python as well!")
    print("Reading GIF...")

    # 1) Read frames from the GIF without pilmode
    frames_arr = imageio.mimread(gif)  # <-- no pilmode argument
    n_frames = len(frames_arr)
    print(f"Total frames in GIF: {n_frames}")

    # 2) Convert each frame (NumPy array) to a PIL Image in RGBA
    pil_frames = []
    for arr in frames_arr:
        # Convert NumPy array to PIL.Image
        # Some GIF frames might be palette-based, so force RGBA
        img_pil = Image.fromarray(arr).convert("RGBA")
        pil_frames.append(img_pil)

    # 3) Flatten frames cumulatively (like image_flatten(x[1:i]) in R/magick)
    print("Flattening frames cumulatively...")
    flattened_frames = []
    for i in range(n_frames):
        cumul = flatten_frames(pil_frames[: i + 1], background=(0, 0, 0, 0))
        flattened_frames.append(cumul)

    print("Applying scanline to each flattened frame...")
    processed_frames = []
    out_w = int(width * scale)
    out_h = int(height * scale)

    # 4) For each flattened frame:
    #    - resize to (out_w, out_h)
    #    - apply scanline
    for _, frame in enumerate(flattened_frames):
        if frame is None:
            continue
        resized = frame.resize((out_w, out_h), resample=Image.Resampling.LANCZOS)
        # Dummy function: replace with your real scanline
        result = scanline(resized, **scanline_kwargs)
        processed_frames.append(result)

    # 5) Convert the 'delay' or 'fps' into a list of durations (in seconds).
    if delay is not None:
        # If user gave a float/int => single delay
        if isinstance(delay, (int, float)):
            duration = delay / 100.0  # 1/100 sec => sec
            durations = [duration] * len(processed_frames)
        else:
            # If it's a list => per frame
            durations = [(d / 100.0) for d in delay]
    else:
        # Use fps => 1/fps seconds
        durations = [1.0 / fps] * len(processed_frames)

    print("Animation done. Returning frames in memory.")
    return processed_frames, durations


def convert_frames_to_gif(frames: list[Image.Image], save_path: str) -> None:
    """
    Convert a list of PIL.Image frames to an animated GIF.

    Parameters
    ----------
    frames : list[PIL.Image]
        List of PIL.Image frames (RGBA).
    save_path : str
        Output path for the animated GIF.
    """
    frames_np = [np.array(f) for f in frames]
    imageio.mimsave(save_path, frames_np, duration=1.00, loop=0)  # type: ignore
    print(f"Saved animated GIF to: {save_path}")
