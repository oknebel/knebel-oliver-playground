# ---------------------------------------------------------------------------------------------------
# Semesterarbeit 1 - Simple RAG Chat Bot PDF
#                    Oliver Knebel
# ---------------------------------------------------------------------------------------------------
# Log:
#   - Vorlage: Simple_Mistral.ipynb (Vector DB, Embeddings), Simple_ChatBot
#   - Prompt Templates: Kontext-Injection in den User Prompt verschoben
#   - Ollama als Model Server, Ollama Library
#   - OpenAI Models (GPT) integriert
#   - Model Switching implementiert (CL-Setting)
#   - Conversation History handling
# Observations:
#   - System / User Prompt werden je nach LLM verschieden/garnicht interpretiert / befolgt
#     (Logik scheint mir nicht standardisiert)
#   - Conversation History sprengt schnell die max. Kontext Grösse der LLM
#   - Man kann etliche Stunden damit verbringen Kombinationen von Prompts Templates und LLMs zu testen
# ----------------------------------------------------------------------------------------------------


import ollama as ol
import chainlit as cl
from chainlit.input_widget import Select, Slider
from py4ragTools.database import Database
from py4ragTools.prompt_tools import PromptTools
from py4ragTools.text_tools import TextHelper, CharacterTextSplitter

import os
from openai import AsyncOpenAI

# this enables launching chainlit/bot via Run/Debug command in VS Code
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)

# init prompt tool templates to be used in this bot
pt = PromptTools()

# using different templates, where context is injected to the user message
pt.set_system_template(PromptTools.SYSTEM_TEMPLATE_2)
pt.set_user_template(PromptTools.USER_TEMPLATE_2)

# --------------
# LLM MODELS
# --------------

# allow changeing the underlaying llm model

models_ddic = ol.list().get('models')
llm_list = [d['model'] for d in models_ddic]
llm_list.append("gpt-4o")
llm_list.append("gpt-3.5-turbo")
llm_list.append("gpt-4o-mini")

init_llm = "llama3.1:8b"
init_llm_options = {
    "temperature": 0.2,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

# -------------------
# DOCUMENT / DATABASE
# -------------------
the_document_path = "./data/2205.13147v4.pdf"
# experimenting with a global system context, so that bot knows about itself and its general knowledge domain
document_info = """ \
    Matryoshka Representation Learning
    Paper, published at 36th Conference on Neural Information Processing Systems (NeurIPS 2022).
"""

# embedding_model = 'all-minilm'  # 384
embedding_model = 'nomic-embed-text'  # 768

db = Database(embedding_model=embedding_model)

th = TextHelper()

# load the document
doc = th.load(the_document_path)

# split the text into chunks
splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=200)
chunks = splitter.split(doc)

# now we build the 'vector store' converting each chunk into a vector
count = 0
for chunk in chunks:
    # Bei Texten der Länge 0 bleibt ollama stehen
    # Sehr kurze Texte sind unbrauchbar für's anschliessende Generieren
    if len(chunk) > 10:
        # print(count)
        # print(entry)
        db.add(chunk)
        count += 1


# ----------------
# CL: SET STARTERS
# ----------------
# okn: definied some starter questions for convinience
@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="What do you know?",
            message="What do you know?",
            #    icon="/public/idea.svg",
        ),
        cl.Starter(
            label="What is your topic?",
            message="What is your topic?",
            #    icon="/public/idea.svg",
        ),
        cl.Starter(
            label="Are there computational and statistical constraints?",
            message="Are there computational and statistical constraints?",
            #    icon="/public/idea.svg",
        ),
    ]


# -------------------
# CL: ON CHAT START
# -------------------
@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
    # init llm
    llm = cl.user_session.get("llm")
    llm_options = cl.user_session.get("llm_options")

    if llm is None:
        llm = init_llm
        llm_options = init_llm_options

    llm_idx = llm_list.index(llm)

    # define some sesion settings to adjust model and temperature
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="LLM",
                values=llm_list,
                initial_index=llm_idx,
            ),
            Slider(
                id="Temperature",
                label="Temperature",
                initial=llm_options["temperature"],
                min=0,
                max=2,
                step=0.1,
            )
        ]
    ).send()

    # add system message only once, argumented with a general summary of the document
    message_history = cl.user_session.get("message_history", [])
    message_history.clear()
    message_history.append(pt.system_prompt(document_info))
    # add message history and options to session cache
    cl.user_session.set("message_history", message_history)
    cl.user_session.set("llm", llm)
    cl.user_session.set("llm_options", llm_options)

    await setup_agent(settings)

# ----------------------
# CL: ON UPDATE SETTINGS
# ----------------------


@cl.on_settings_update
async def setup_agent(settings):
    cl.user_session.set("llm", settings["Model"])
    llm_options = cl.user_session.get("llm_options")
    llm_options["temperature"] = settings["Temperature"]


# ---------------
# CL: ON MESSAGE
# ----------------
@ cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):

    llm = cl.user_session.get("llm")
    llm_options = cl.user_session.get("llm_options")

    user_prompt = message.content
    msg = cl.Message(content="")

    # ---------
    # RETRIEVAL
    # ---------
    context = db.query_database(user_prompt, 0.5)
    await msg.stream_token("[MODEL: " + llm + ", TEMP: " + str(llm_options["temperature"]) + ", CONTEXT: " + str(len(context)) + "]\n\n")

    # ---------
    # AUGMENT
    # ---------
    context_prompt = ""
    for (score, text) in context:
        context_prompt += (text + "\\n")

    # okn: add message with context injection
    user_msg = pt.user_prompt_rag(user_prompt, context_prompt)

    # ---------
    # GENERATION
    # ---------
    message_history = cl.user_session.get("message_history", [])
    message_history.append(user_msg)

    # invoke responder
    if llm.startswith("gpt"):
        # call open ai
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        stream = await client.chat.completions.create(model=llm, messages=message_history, stream=True, **llm_options)
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await msg.stream_token(token)
    else:
        # call ollama
        client = ol.AsyncClient()
        stream = await client.chat(model=llm, messages=message_history, stream=True, options=llm_options)
        async for part in stream:
            if token := part["message"]["content"] or "":
                await msg.stream_token(token)

    await msg.send()

    # append some prompt infos attachements
    text_elements = []
    text_elements.append(
        cl.Text(content=pt.system_prompt(document_info).get("content"),
                name="system_prompt", display="side")
    )
    text_elements.append(
        cl.Text(content=user_msg.get("content"),
                name="user_prompt", display="side")
    )
    info_names = [text_el.name for text_el in text_elements]
    info = f"\nInfos: {', '.join(info_names)}"

    await cl.Message(
        content=info,
        elements=text_elements,
    ).send()

    # add response to message history
    message_history.append({"role": "assistant", "content": msg.content})
