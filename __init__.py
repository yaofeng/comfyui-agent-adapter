"""
ComfyUI Agent Adapter

A plugin for ComfyUI that provides nodes for easy agent integration.
Includes Base64 encode/decode nodes for seamless image handling without temp files.
"""

from .nodes.base64_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Export for ComfyUI
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# ComfyUI entry point
NODE_CLASS_MAPPINGS = NODE_CLASS_MAPPINGS
NODE_DISPLAY_NAME_MAPPINGS = NODE_DISPLAY_NAME_MAPPINGS
