import openai
import gradio as gr
import time
import os
from gradio.themes.base import Base

openai.api_key = os.environ["OPENAI_API_KEY"]
assistant_id = os.environ["ASSISTANT_ID"]

class Seafoam(Base):
    pass

seafoam = Seafoam()

def assistant_response(message, history, thread_id=None):
    if thread_id is None:
        thread = openai.beta.threads.create()
        thread_id = thread.id

    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

    # Criar uma execução para obter resposta
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Esperar pela resposta do Assistant
    while run.status in ['queued', 'in_progress']:
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        time.sleep(1)

    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    assistant_message = messages.data[0].content[0].text.value
    return assistant_message, thread_id

css = """
footer {display: none !important;}
.centered-text {
    text-align: center;
}
"""

example_conversation = [
    {"text": "Os convênios de PD&I podem envolver instituições privadas?"},
    {"text": "Onde posso encontrar o regulamento do curso de Engenharia de Software?"},
    {"text": "Quem é o reitor do IFAL?"}
]

with gr.Blocks(title="Assistente para o IFAL", css=css, theme=seafoam) as iface:
    gr.Markdown("# Converse com os dados do Integra.")
    chatbot = gr.Chatbot(height=400,  label="Chatbot", examples=example_conversation)
    textbox = gr.Textbox(placeholder="Digite sua mensagem aqui...", label="Usuário")
    state = gr.State(None)
    clear_button = gr.Button("Limpar Conversa")
    
    gr.Markdown("<div class='centered-text'>Criado por Giseldo Neo.</div>") 
    def respond(message, chat_history, thread_id=None):
        if thread_id is None:
            thread_id = state.value
            if thread_id is None:
                thread = openai.beta.threads.create()
                thread_id = thread.id
        bot_message, thread_id = assistant_response(message, chat_history, thread_id)
        chat_history.append((message, bot_message))
        return "", chat_history, thread_id

    def clear():
        return None, [], None

    textbox.submit(respond, [textbox, chatbot, state], [textbox, chatbot, state])
    clear_button.click(clear, None, [state, chatbot, state])

iface.launch()