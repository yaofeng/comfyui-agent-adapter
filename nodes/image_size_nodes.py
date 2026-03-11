"""
Image Size Calculation Node for ComfyUI.

Calculates new dimensions and padding values for matching target aspect ratio.
"""


class ImageSizeCalcNode:
    """
    Node that calculates new image dimensions and padding values
    for matching a target aspect ratio without modifying the actual image.
    """

    CATEGORY = "agent_adapter"
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("new_width", "new_height", "pad_top", "pad_bottom", "pad_left", "pad_right")
    FUNCTION = "calculate"
    OUTPUT_NODE = False

    # 宽高比选项
    ASPECT_RATIOS = [
        (1, 1),    # 1:1 正方形
        (4, 3),    # 4:3 传统电视
        (3, 2),    # 3:2 35mm 胶片
        (16, 9),   # 16:9 高清视频
        (21, 9),   # 21:9 超宽屏
        (9, 16),   # 9:16 竖屏视频
        (3, 4),    # 3:4 4:3 竖版
        (2, 3),    # 2:3 35mm 竖版
        (9, 19),   # 9:19 手机竖屏
    ]

    # 对齐选项
    HORIZONTAL_ALIGN = ["left", "center", "right"]
    VERTICAL_ALIGN = ["top", "center", "bottom"]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "aspect_ratio": (cls._get_aspect_ratio_labels(), {
                    "default": cls._get_aspect_ratio_labels()[0]
                }),
                "auto_flip": ("BOOLEAN", {
                    "default": True
                }),
                "horizontal_align": (cls.HORIZONTAL_ALIGN, {
                    "default": "center"
                }),
                "vertical_align": (cls.VERTICAL_ALIGN, {
                    "default": "center"
                }),
            }
        }

    @classmethod
    def _get_aspect_ratio_labels(cls):
        """返回宽高比的字符串标签列表"""
        return [f"{w}:{h}" for w, h in cls.ASPECT_RATIOS]

    @classmethod
    def _parse_aspect_ratio(cls, aspect_ratio: str):
        """解析宽高比字符串为元组"""
        w, h = aspect_ratio.split(":")
        return int(w), int(h)

    @classmethod
    def _get_image_dimensions(cls, image):
        """从图像张量获取宽高"""
        if len(image.shape) == 4:
            # [B, H, W, C]
            return image.shape[2], image.shape[1]  # (width, height)
        else:
            # [H, W, C]
            return image.shape[1], image.shape[0]  # (width, height)

    @classmethod
    def _should_flip(cls, orig_w: int, orig_h: int, ratio_w: int, ratio_h: int, auto_flip: bool):
        """判断是否需要翻转宽高比"""
        if not auto_flip:
            return False

        orig_is_portrait = orig_h > orig_w
        ratio_is_portrait = ratio_h > ratio_w

        return orig_is_portrait != ratio_is_portrait

    @classmethod
    def _calculate_target_dimensions(cls, orig_w: int, orig_h: int, ratio_w: int, ratio_h: int):
        """计算目标尺寸"""
        target_ratio = ratio_w / ratio_h
        orig_ratio = orig_w / orig_h

        if orig_ratio > target_ratio:
            # 原图更"宽"，按原宽计算
            new_width = orig_w
            new_height = int(round(orig_w / target_ratio))
        else:
            # 原图更"高"，按原高计算
            new_width = int(round(orig_h * target_ratio))
            new_height = orig_h

        return new_width, new_height

    @classmethod
    def _distribute_padding(cls, total_pad: int, align: str):
        """根据对齐方式分配外补"""
        if align == "left" or align == "top":
            return 0, total_pad
        elif align == "center":
            pad_start = total_pad // 2
            pad_end = total_pad - pad_start
            return pad_start, pad_end
        else:  # right or bottom
            return total_pad, 0

    def calculate(self, image, aspect_ratio: str, auto_flip: bool,
                  horizontal_align: str, vertical_align: str):
        """计算匹配目标宽高比所需的尺寸和外补值"""
        # 1. 获取原图尺寸
        orig_w, orig_h = self._get_image_dimensions(image)

        # 2. 解析目标宽高比
        ratio_w, ratio_h = self._parse_aspect_ratio(aspect_ratio)

        # 3. 判断是否需要翻转宽高比
        if self._should_flip(orig_w, orig_h, ratio_w, ratio_h, auto_flip):
            ratio_w, ratio_h = ratio_h, ratio_w

        # 4. 计算目标尺寸
        new_width, new_height = self._calculate_target_dimensions(orig_w, orig_h, ratio_w, ratio_h)

        # 5. 计算总外补量
        total_pad_w = new_width - orig_w
        total_pad_h = new_height - orig_h

        # 6. 分配外补
        pad_left, pad_right = self._distribute_padding(total_pad_w, horizontal_align)
        pad_top, pad_bottom = self._distribute_padding(total_pad_h, vertical_align)

        return (new_width, new_height, pad_top, pad_bottom, pad_left, pad_right)


# 导出节点
NODE_CLASS_MAPPINGS = {
    "ImageSizeCalc": ImageSizeCalcNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageSizeCalc": "Calculate Image Size",
}
