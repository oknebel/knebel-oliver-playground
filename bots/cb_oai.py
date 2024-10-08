# chainlit run cb_oai.py -w

import os
from openai import AsyncOpenAI
import chainlit as cl

client = AsyncOpenAI()
client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Allows Running the Chainlit, by Run/Debug command in IDE
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)

# Instrument the OpenAI client
# cl.instrument_openai()

model = "gpt-3.5-turbo"
settings = {
    "model": model,
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start
async def on_chat_start():

    # Sending an image with the local file path
    elements = [
        cl.Image(name="image1", display="inline", path="./images/bbf.jpeg")
    ]
    await cl.Message(content="Open AI- Berufsberater " + model, elements=elements).send()

    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "Du bist ein Berufsberater in der Schweiz und hilfst mir bei Fragen zu Berufswahl und Wegen."}],
    )


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    # await msg.send()

    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
