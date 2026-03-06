# ComfyUI Agent Adapter

一个用于 ComfyUI 的插件，提供智能体集成节点，支持无需临时文件的 base64 图片处理。

## 功能特性

- **Base64 转图片节点** - 直接将 base64 字符串解码为图片张量
- **图片转 Base64 节点** - 将图片张量编码为 base64 字符串
- 服务端不产生临时文件
- 支持 PNG、JPEG、WEBP 格式
- 可调节有损压缩质量

## 安装方法

1. 克隆此仓库到 ComfyUI 的 custom_nodes 目录：

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-username/comfyui-agent-adapter.git
```

2. 安装依赖：

```bash
cd comfyui-agent-adapter
pip install -r requirements.txt
```

3. 重启 ComfyUI

## 节点说明

### Base64 转图片 (`Base64Decode`)

将 base64 编码的字符串解码为图片张量。

**输入：**
- `base64_string` (STRING) - Base64 编码的图片（支持 data URI 前缀或纯 base64）

**输出：**
- `image` (IMAGE) - ComfyUI 图片张量 [B, H, W, C]

**使用示例：**
```
智能体发送：data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...
→ Base64 转图片节点 → IMAGE 输出 → 连接到任意图片处理节点
```

### 图片转 Base64 (`Base64Encode`)

将图片张量编码为 base64 字符串。

**输入：**
- `image` (IMAGE) - ComfyUI 图片张量
- `format` (STRING) - 输出格式：PNG、JPEG 或 WEBP（默认：PNG）
- `quality` (INT) - 有损格式质量 1-100（默认：95）

**输出：**
- `base64_string` (STRING) - Base64 编码的图片（纯 base64，不含 data URI 前缀）

**使用示例：**
```
工作流输出 IMAGE → 图片转 Base64 节点 → base64_string → 发送给智能体
```

## 工作流示例

```json
{
  "1": {
    "class_type": "Base64Decode",
    "inputs": {
      "base64_string": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
    }
  },
  "2": {
    "class_type": "Base64Encode",
    "inputs": {
      "image": ["1", 0],
      "format": "PNG",
      "quality": 95
    }
  }
}
```

## API 调用示例

```python
import base64
import requests

# 读取并编码本地图片
with open("input.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

# 发送到 ComfyUI 工作流
prompt = {
    "1": {
        "class_type": "Base64Decode",
        "inputs": {"base64_string": image_data}
    },
    # ... 工作流其余部分
}

response = requests.post("http://localhost:8188/prompt", json={"prompt": prompt})

# 获取结果
result = response.json()
output_base64 = result["outputs"]["2"]["base64_string"]

# 保存结果
with open("output.png", "wb") as f:
    f.write(base64.b64decode(output_base64))
```

## 依赖

- PIL (Pillow)
- torch
- numpy

## 许可证

MIT
