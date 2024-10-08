# chainlit run cb_ollama_stream.py -w

from langchain.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

# Allows Running the Chainlit, by Run/Debug command in IDE
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)


model = "llama3.1:8b"

llm = Ollama(
    model=model,
    temperature=0.0
)
# "Mistral"
# "llama3"


@cl.on_chat_start
async def on_chat_start():
    # Sending an image with the local file path
    elements = [
        cl.Image(name="image1", display="inline", path="./images/bbf.jpeg")
    ]
    await cl.Message(content="Berufsberater " + model, elements=elements).send()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Du bist ein Berufsberater in der Schweiz und hilfst mir bei meiner beruflichenEntwicklung",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | llm | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    for chunk in await cl.make_async(runnable.stream)(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    # await msg.stream_token("\n\n[Served by "+model+"]")
    await msg.send()
