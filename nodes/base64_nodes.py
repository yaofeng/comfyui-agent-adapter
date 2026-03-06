import torch
import numpy as np
from ..utils.image_utils import decode_base64_to_image


class Base64DecodeNode:
    """
    Node that decodes a base64 string to an image tensor.

    This simplifies the workflow by allowing agents to pass base64-encoded
    images directly without uploading to a server or creating temp files.
    """

    CATEGORY = "agent_adapter"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "decode"
    OUTPUT_NODE = False

    def INPUT_TYPES(s):
        return {
            "required": {
                "base64_string": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Paste base64 encoded image string here"
                }),
            }
        }

    def decode(self, base64_string: str):
        """
        Decode base64 string to ComfyUI image tensor.

        Args:
            base64_string: Base64 encoded image (with or without data URI prefix)

        Returns:
            Tuple containing image tensor with shape [1, H, W, C]
        """
        # Handle empty input
        if not base64_string or not base64_string.strip():
            raise ValueError("Base64 string is empty")

        # Decode base64 to PIL Image
        image = decode_base64_to_image(base64_string.strip())

        # Convert to ComfyUI tensor format
        # ComfyUI expects [B, H, W, C] format, float32, range [0, 1]
        image_array = np.array(image).astype(np.float32) / 255.0

        # Add batch dimension: (H, W, C) -> (1, H, W, C)
        image_tensor = torch.from_numpy(image_array).unsqueeze(0)

        return (image_tensor,)

    @classmethod
    def IS_CHANGED(cls, base64_string, **kwargs):
        """Recompute when input changes"""
        return base64_string


class Base64EncodeNode:
    """
    Node that encodes an image tensor to a base64 string.

    This simplifies the workflow by allowing agents to receive base64-encoded
    results directly without downloading from a server or dealing with temp files.
    """

    CATEGORY = "agent_adapter"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64_string",)
    FUNCTION = "encode"
    OUTPUT_NODE = True

    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "format": (["PNG", "JPEG", "WEBP"], {
                    "default": "PNG"
                }),
                "quality": ("INT", {
                    "default": 95,
                    "min": 1,
                    "max": 100
                }),
            }
        }

    def encode(self, image, format: str = "PNG", quality: int = 95):
        """
        Encode ComfyUI image tensor to base64 string.

        Args:
            image: ComfyUI image tensor [B, H, W, C]
            format: Output format (PNG, JPEG, WEBP)
            quality: Quality for lossy formats (1-100)

        Returns:
            Tuple containing base64 encoded string (PNG format by default)
        """
        from ..utils.image_utils import encode_image_to_base64

        # Handle batch dimension - take first image
        if image.dim() == 4:
            image = image[0]

        # Convert tensor to PIL Image
        if isinstance(image, torch.Tensor):
            image_np = image.cpu().numpy()
        else:
            image_np = np.array(image)

        # Scale from [0, 1] to [0, 255]
        image_array = (image_np * 255.0).clip(0, 255).astype(np.uint8)

        # Handle grayscale
        if image_array.shape[-1] == 1:
            image_array = np.repeat(image_array, 3, axis=-1)

        pil_image = Image.fromarray(image_array)

        # Encode to base64
        base64_string = encode_image_to_base64(pil_image, format=format, quality=quality)

        return (base64_string,)

    @classmethod
    def IS_CHANGED(cls, image, format, quality, **kwargs):
        """Recompute when input changes"""
        return f"{image.sum().item()}_{format}_{quality}"


# Export all nodes
NODE_CLASS_MAPPINGS = {
    "Base64Decode": Base64DecodeNode,
    "Base64Encode": Base64EncodeNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Base64Decode": "Base64 to Image",
    "Base64Encode": "Image to Base64",
}
