import gradio as gr
from app.research_agent import start_research_workflow
from pydantic import BaseModel
from typing import List


class ThreadPost(BaseModel):
    post_number: int
    content: str


class Thread(BaseModel):
    title: str
    posts: List[ThreadPost]


def search_articles(query, count, instructions) -> str:
    try:
        # Call your workflow
        results: Thread = start_research_workflow(query, count, instructions)

        html_output = f"<h2 style='font-family:sans-serif; color:#f5f5f5;'>{results.title}</h2>"

        for post in results.posts:
            post_id = f"post_{post.post_number}"
            post_content = post.content.replace("\n", "<br>")  # preserve line breaks

            html_output += f"""
            <div style="display:flex; align-items:flex-start; margin-bottom:20px; padding:4px;
                        border-bottom:1px solid #2f3336; font-family:sans-serif; color:#e7e9ea;">

                <!-- Profile Picture -->
                <div style="margin-right:12px;">
                    <img src="https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png"
                         style="width:48px; height:48px; border-radius:50%;" />
                </div>

                <!-- Post Content -->
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:6px;">
                        <span style="font-weight:bold; color:#fff;">User {post.post_number}</span>
                        <span style="color:#8b98a5;">@user{post.post_number} · now</span>
                    </div>
                    <div style="margin-top:5px; font-size:15px; line-height:1.5;">
                        {post_content}
                    </div>

                    <!-- Action Bar -->
                    <div style="display:flex; justify-content:space-between; max-width:300px; margin-top:10px; color:#8b98a5; font-size:14px;">
                        <span style="cursor:pointer;">💬</span>
                        <span style="cursor:pointer;">🔁</span>
                        <span style="cursor:pointer;">❤️</span>
                        <span style="cursor:pointer;" onclick="navigator.clipboard.writeText(document.getElementById('{post_id}').innerText)">📋</span>
                    </div>
                </div>
            </div>

            <!-- Hidden div for copy -->
            <div id="{post_id}" style="display:none;">{post.content}</div>
            """

        return f"<div style='background-color:#000; padding:20px; border-radius:10px;'>{html_output}</div>"

    except Exception as e:
        return f"<b style='color:red;'>Error:</b> {str(e)}"


with gr.Blocks() as demo:
    gr.Markdown("# 🔎 Article Research Tool")

    with gr.Row():
        query = gr.Textbox(label="Search Query", placeholder="Enter your query...")
        count = gr.Slider(1, 100, value=20, step=1, label="Number of Results")
        instructions = gr.Textbox(
            label="Instructions (optional)", placeholder="Extra instructions..."
        )

    search_btn = gr.Button("Search")
    status = gr.Label(value="", label="Status")  # Loader indicator
    output = gr.HTML()

    def with_loader(query, count, instructions):
        yield "⏳ Processing...", ""  # Show loader
        results_html = search_articles(query, count, instructions)
        yield "", results_html  # Clear loader, show results

    search_btn.click(
        fn=with_loader,
        inputs=[query, count, instructions],
        outputs=[status, output],
    )

if __name__ == "__main__":
    demo.launch()
