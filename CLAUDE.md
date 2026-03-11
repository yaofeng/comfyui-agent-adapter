# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

ComfyUI Agent Adapter - 为 ComfyUI 提供智能体集成节点的插件，支持无临时文件的 base64 图片处理。

## 依赖安装

```bash
pip install -r requirements.txt
```

依赖：Pillow, torch, numpy

## 架构结构

```
comfyui-agent-adapter/
├── __init__.py              # 插件入口，导出 NODE_CLASS_MAPPINGS
├── nodes/
│   ├── __init__.py
│   ├── base64_nodes.py      # 核心节点：Base64DecodeNode, Base64EncodeNode
│   └── image_size_nodes.py  # 图像尺寸计算节点：ImageSizeCalcNode
├── utils/
│   ├── __init__.py
│   └── image_utils.py       # 图片编解码工具函数
└── requirements.txt
```

## 核心节点

**Base64DecodeNode** (`Base64Decode`)
- 输入：`base64_string` (STRING) - 支持 data URI 前缀或纯 base64
- 输出：`image` (IMAGE) - ComfyUI 张量格式 [1, H, W, C], float32, 范围 [0, 1]

**Base64EncodeNode** (`Base64Encode`)
- 输入：`image` (IMAGE), `format` (PNG/JPEG/WEBP), `quality` (1-100)
- 输出：`base64_string` (STRING) - 纯 base64，无 data URI 前缀
- 注意：`OUTPUT_NODE = True`，返回 dict 包含 `ui` 和 `result` 用于 API 访问

**ImageSizeCalcNode** (`ImageSizeCalc`)
- 计算匹配目标宽高比所需的新尺寸和外补像素值（不实际处理图像）
- 输入：
  - `image` (IMAGE) - ComfyUI 图像张量
  - `aspect_ratio` (COMBO) - 目标宽高比：1:1, 4:3, 3:2, 16:9, 21:9, 9:16, 3:4, 2:3, 9:19
  - `auto_flip` (BOOLEAN) - 自动匹配长短边（纵向图配横向宽高比时自动翻转）
  - `horizontal_align` (COMBO) - 水平对齐：left, center, right
  - `vertical_align` (COMBO) - 垂直对齐：top, center, bottom
- 输出：
  - `new_width`, `new_height` (INT) - 目标尺寸
  - `pad_top`, `pad_bottom`, `pad_left`, `pad_right` (INT) - 四个方向的外补像素值
- 计算逻辑：
  1. 如果 `auto_flip=true` 且原图方向与宽高比方向不一致，翻转宽高比
  2. 按"保持图像完整"原则计算目标尺寸（一个方向不变，另一个方向扩展）
  3. 根据对齐方式分配外补到两侧

## 图片格式处理

- ComfyUI 期望格式：[B, H, W, C]，float32，范围 [0, 1]
- PIL 转换时自动处理：RGBA/P/LA 模式转 RGB，单通道重复为三通道
- Base64DecodeNode 添加 batch 维度：(H, W, C) → (1, H, W, C)
