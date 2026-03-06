import base64
import io
from PIL import Image


def decode_base64_to_image(base64_string: str) -> Image.Image:
    """
    Decode base64 string to PIL Image.

    Args:
        base64_string: Base64 encoded image string (with or without data URI prefix)

    Returns:
        PIL Image object
    """
    # Remove data URI prefix if present (e.g., "data:image/png;base64,")
    if "," in base64_string:
        base64_string = base64_string.split(",", 1)[1]

    # Decode base64
    image_data = base64.b64decode(base64_string)

    # Load as PIL Image
    image = Image.open(io.BytesIO(image_data))

    # Convert to RGB if necessary (handles RGBA, P mode, etc.)
    if image.mode in ("RGBA", "P", "LA"):
        image = image.convert("RGB")

    return image


def encode_image_to_base64(image: Image.Image, format: str = "PNG", quality: int = 95) -> str:
    """
    Encode PIL Image to base64 string.

    Args:
        image: PIL Image object
        format: Output format (PNG, JPEG, WEBP)
        quality: Quality for lossy formats (JPEG, WEBP)

    Returns:
        Base64 encoded string (without data URI prefix)
    """
    buffer = io.BytesIO()

    # Handle format-specific options
    save_kwargs = {}
    if format.upper() == "JPEG":
        # JPEG doesn't support alpha channel
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif format.upper() == "WEBP":
        save_kwargs["quality"] = quality
        save_kwargs["lossless"] = False
    elif format.upper() == "PNG":
        save_kwargs["optimize"] = True

    image.save(buffer, format=format.upper(), **save_kwargs)

    # Encode to base64
    image_data = buffer.getvalue()
    base64_string = base64.b64encode(image_data).decode("utf-8")

    return base64_string


def image_to_tensor(image: Image.Image) -> tuple:
    """
    Convert PIL Image to ComfyUI tensor format.

    Args:
        image: PIL Image object

    Returns:
        Tuple containing (image_tensor, mask_tensor or None)
    """
    import torch
    import numpy as np

    # Convert to numpy array
    image_array = np.array(image).astype(np.float32) / 255.0

    # Convert to tensor (H, W, C) -> ComfyUI expects this format
    image_tensor = torch.from_numpy(image_array)

    # Check for alpha channel to create mask
    mask = None
    if image.mode == "RGBA":
        alpha = np.array(image)[:, :, 3].astype(np.float32) / 255.0
        mask = torch.from_numpy(1.0 - alpha)  # Invert: 0 = opaque, 1 = transparent

    return (image_tensor, mask)


def tensor_to_image(image_tensor) -> Image.Image:
    """
    Convert ComfyUI tensor to PIL Image.

    Args:
        image_tensor: ComfyUI image tensor (H, W, C)

    Returns:
        PIL Image object
    """
    import torch
    import numpy as np

    # Ensure tensor is on CPU and convert to numpy
    if isinstance(image_tensor, torch.Tensor):
        image_tensor = image_tensor.cpu().numpy()

    # Scale from [0, 1] to [0, 255]
    image_array = (image_tensor * 255.0).astype(np.uint8)

    # Handle different channel counts
    if image_array.shape[-1] == 1:
        image_array = np.repeat(image_array, 3, axis=-1)

    return Image.fromarray(image_array)
