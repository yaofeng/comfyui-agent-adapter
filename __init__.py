"""
ComfyUI Agent Adapter

A plugin for ComfyUI that provides nodes for easy agent integration.
Includes Base64 encode/decode nodes for seamless image handling without temp files.
"""

from .nodes.base64_nodes import NODE_CLASS_MAPPINGS as BASE64_NODE_MAPPINGS
from .nodes.base64_nodes import NODE_DISPLAY_NAME_MAPPINGS as BASE64_DISPLAY_NAME_MAPPINGS
from .nodes.image_size_nodes import NODE_CLASS_MAPPINGS as IMAGE_SIZE_NODE_MAPPINGS
from .nodes.image_size_nodes import NODE_DISPLAY_NAME_MAPPINGS as IMAGE_SIZE_DISPLAY_NAME_MAPPINGS

# 合并节点映射
NODE_CLASS_MAPPINGS = {**BASE64_NODE_MAPPINGS, **IMAGE_SIZE_NODE_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**BASE64_DISPLAY_NAME_MAPPINGS, **IMAGE_SIZE_DISPLAY_NAME_MAPPINGS}

# Export for ComfyUI
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# ComfyUI entry point
NODE_CLASS_MAPPINGS = NODE_CLASS_MAPPINGS
NODE_DISPLAY_NAME_MAPPINGS = NODE_DISPLAY_NAME_MAPPINGS
