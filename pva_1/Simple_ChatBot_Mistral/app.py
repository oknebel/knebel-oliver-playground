# You can find this code for Chainlit python streaming here (https://docs.chainlit.io/concepts/streaming/python)


from mistralai import Mistral  # importing mistralai for API usage
import chainlit as cl  # importing chainlit for our app


# Chat Templates
system_template = """You are a helpful assistant who answers always in well-formed German rhymes in the style of Goethe!
"""

user_template = """{input}
Think through your response step by step. 
"""

print("b4")


@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
    settings = {
        "model": "Mistral",
        "temperature": 0,
        "max_tokens": 500,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    cl.user_session.set("settings", settings)


@cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):
    settings = cl.user_session.get("settings")

    print(message.content)

    client = Mistral(
        server_url='http://localhost:11434/',
        api_key='ollama',  # api_key is required, but unused for local models
    )

    messages = [
        {
            "role": "system", "content": system_template,
        },
        {

            "role": "user", "content": message.content
        }
    ]

    msg = cl.Message(content="")
    print(settings['model'])
    print(messages)

    # Call Ollama
    async_response = await client.chat.stream_async(
        model=settings['model'],
        messages=messages
    )

    async for chunk in async_response:
        token = chunk.data.choices[0].delta.content
        if not token:
            token = ""
        await msg.stream_token(token)

    # Send and close the message stream
    print("4")
    # await msg.send()
