# 赵图图设计编写;Design by zhaotutu;
import os
import base64
import gradio as gr
from openai import OpenAI

# 读取环境变量中的API Key
API_KEY = os.getenv("DASH_API_KEY")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 初始化 OpenAI 客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 默认 System Message
DEFAULT_SYSTEM_MESSAGE = {
    "文生视频": (
        "你是一个专业的视频创作助手，请按照以下要求扩展提示词，确保适合生成一个5秒的视频："
        "注意！输出结果必须是完整的一段话，控制在500字以内，语言精炼，表达准确，避免冗余。尽量使用简单的词语和句子结构。"
        "包含主体（主体描述）、运动、场景、镜头 、光影 、氛围等元素。"
        "运动要符合物理规律，运动变化幅度不能过大。"
        "避免非常复杂的物理动作，如球类的弹跳、高空抛物等。"
    ),
    "图生视频": (
        "你是一个专业的视频创作助手，请根据上传的图片，扩展视频提示词，确保适合生成一个5秒的视频："
        "注意！输出结果必须是完整的一段话，控制在500字以内，语言精炼，表达准确，避免冗余。尽量使用简单的词语和句子结构。"
        "这段话包含主体描述、背景（图片中的背景描述）、运动描述等元素。"
        "运动要符合物理规律，尽量用图片中可能发生的运动描述，描述不能与图片相差过大，运动变化幅度不能过大。"
        "避免非常复杂的物理动作，如球类的弹跳、高空抛物等。"
    )
}

# 统一的 Prompt 生成函数
def generate_prompt(task_type, input_text, system_message, image_path=None, temperature=0.7, top_p=0.9):
    """
    生成优化后的提示词：
    - task_type: '文生视频' or '图生视频'
    - input_text: 用户输入的原始提示词
    - system_message: 用户自定义的 System Message，如果为空则使用默认参数
    - image_path: 仅在图生视频时提供本地图片路径
    - temperature: 控制创造力
    - top_p: 控制生成的多样性
    """

    # 如果用户未输入 System Message，则使用默认参数
    if not system_message.strip():
        system_message = DEFAULT_SYSTEM_MESSAGE[task_type]

    if task_type == "文生视频":
        model_name = "qwq-32b"
        user_content = input_text

    elif task_type == "图生视频":
        model_name = "qwen-vl-max-latest"

        # 读取图片并进行 Base64 编码
        if image_path:
            with open(image_path, "rb") as img_file:
                encoded_img = base64.b64encode(img_file.read()).decode("utf-8")
            user_content = [
                {"type": "text", "text": input_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_img}"}}
            ]
        else:
            return "错误：请上传图片"

    else:
        return "错误：未识别的任务类型"

    # 调用 API
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ],
            stream=True,  # 必须开启流式模式
            temperature=temperature,
            top_p=top_p
        )

        # 获取生成的内容
        generated_prompt = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                generated_prompt += chunk.choices[0].delta.content

        # 确保字数控制
        if len(generated_prompt) > 500:
            return generate_prompt(task_type, input_text, system_message, image_path, temperature, top_p)

        return generated_prompt

    except Exception as e:
        return f"❌ 生成失败，错误信息：{str(e)}"


# Gradio 界面设计
def interface(task_type, input_text, system_message, image=None, temperature=0.7, top_p=0.9):
    if task_type == "图生视频" and image is None:
        return "请上传图片后再点击生成！"

    image_path = None
    if image:
        image_path = image

    return generate_prompt(task_type, input_text, system_message, image_path, temperature, top_p)


# Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("## 🎬 提示词扩展工具")
    gr.Markdown(
        "### 🎉 欢迎加入赵图图的知识星球 🎉\n"
        "知识星球有很多独家的小软件哦！\n"
        "**星球号：12116758**\n"
        "📌 **QQ群：**\n"
        "- 小粉屋 628266084\n"
        "- 小绿屋 903753035\n"
        "- 小黑屋 950351015\n"
    )
    
    with gr.Row():
        task_type = gr.Dropdown(["文生视频", "图生视频"], label="选择任务类型", value="文生视频")

    input_text = gr.Textbox(label="输入原始提示词", placeholder="请输入你的提示词...")
    system_message = gr.Textbox(
        label="自定义 System Message（可选，默认提供优化参数）",
        placeholder="如果为空，则使用默认优化规则"
    )
    image_input = gr.Image(type="filepath", label="上传图片（仅限图生视频）", visible=False)

    with gr.Row():
        temperature = gr.Slider(0.0, 1.0, value=0.7, label="创造性 (Temperature)")
        top_p = gr.Slider(0.1, 1.0, value=0.9, label="Top-P 采样")

    generate_button = gr.Button("生成扩展提示词")
    output_text = gr.Textbox(label="扩展后的提示词", interactive=False)

    # 控制图片上传的显示
    def toggle_image_visibility(selected_task):
        return gr.update(visible=(selected_task == "图生视频"))

    task_type.change(toggle_image_visibility, inputs=task_type, outputs=image_input)

    # 绑定按钮事件
    generate_button.click(interface, inputs=[task_type, input_text, system_message, image_input, temperature, top_p], outputs=output_text)

# 启动 Gradio
demo.launch()
