# You can find this code for Chainlit python streaming here (https://docs.chainlit.io/concepts/streaming/python)
from ollama import AsyncClient
import chainlit as cl  # importing chainlit for our app

# Allows Running the Chainlit, by Run/Debug command in IDE
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)

model = "llama3.1:8b"

system_template = "You are a helpful assistant that translates to Berlinerisch. Translate the user input."

settings = {
    "model": model,
    "temperature": 0,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
   # Sending an image with the local file path
    elements = [
        cl.Image(name="image1", display="inline", path="./images/bbf.jpeg")
    ]
    await cl.Message(content="Hello there, I am a Berlin Bablefish in the ocean of: " + model, elements=elements).send()

    cl.user_session.set("settings", settings)


@cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")
    print(message.content)

    messages = [
        {
            "role": "system", "content": system_template,
        },
        {
            "role": "user", "content": message.content
        }
    ]

    msg = cl.Message(content="")

    # Call Mistral
    async for chunk in await AsyncClient().chat(
        model=model, messages=messages, stream=True
    ):
        token = chunk["message"]["content"]
        await msg.stream_token(token)

    # Send and close the message stream
    print("Done.")
    # await msg.send()
