import gradio as gr
import requests

API_BASE = "http://localhost:8000/api"


def upload_file(file):
    if file is None:
        return "请先选择文件"
    with open(file.name, "rb") as f:
        resp = requests.post(f"{API_BASE}/upload", files={"file": (file.name, f)})
    if resp.status_code != 200:
        return f"上传失败: {resp.text}"
    data = resp.json()
    return f"✅ {data['file']} 入库成功，共 {data['chunks']} 个分块"


def chat(question, history):
    if not question.strip():
        return ""
    resp = requests.post(f"{API_BASE}/ask", json={"question": question})
    if resp.status_code != 200:
        return f"❌ 出错: {resp.text}"
    data = resp.json()
    answer = data["answer"]
    if data["sources"]:
        answer += "\n\n**引用来源：**\n" + "\n".join(f"- {s}" for s in data["sources"])
    answer += f"\n\n<sub>tokens: {data['tokens_used']}</sub>"
    return answer


with gr.Blocks(title="RAG 知识库问答") as demo:
    gr.Markdown("# 📚 私有知识库 RAG 智能问答")
    with gr.Row():
        file_input = gr.File(label="上传 PDF / Markdown", type="filepath")
        upload_btn = gr.Button("上传入库")
    upload_output = gr.Textbox(label="上传结果")
    upload_btn.click(upload_file, inputs=file_input, outputs=upload_output)

    gr.ChatInterface(fn=chat, title="向知识库提问")

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)