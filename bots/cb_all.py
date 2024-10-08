# You can find this code for Chainlit python streaming here (https://docs.chainlit.io/concepts/streaming/python)
import ollama as ol
from ollama import AsyncClient
import chainlit as cl  # importing chainlit for our app
from chainlit.input_widget import Select, Slider

import os
from openai import AsyncOpenAI


# allows launching chainlit and bot by Run/Debug command in IDE
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)


# okn: check installed modells and init current model and options
models_ddic = ol.list().get('models')
llm_list = [d['model'] for d in models_ddic]
llm_list.append("gpt-4o")
llm_list.append("gpt-3.5-turbo")


llm = "llama3.1:8b"

llm_options = {
    "temperature": 0.2,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

# okn: definied some starter questions for convinience


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="What can you do for me?",
            message="What can you do for me?",
            #    icon="/public/idea.svg",
        ),

    ]


@cl.on_chat_start  # marks a function that will be executed at the start of a user session
async def start_chat():
    user_model = llm
    user_options = llm_options

    user_model_idx = llm_list.index(user_model)

    # okn: define some sesion settings to adjust model and temperature
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="LLM",
                values=llm_list,
                initial_index=user_model_idx,
            ),
            Slider(
                id="Temperature",
                label="Temperature",
                initial=user_options["temperature"],
                min=0,
                max=2,
                step=0.1,
            )
        ]
    ).send()

    # okn: add message history and options to session cache
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpfull assistant answering user questions."}],
    )
    cl.user_session.set("user_model", user_model)
    cl.user_session.set("user_options", user_options)

    await setup_agent(settings)


# okn: callback to update session model and options
@cl.on_settings_update
async def setup_agent(settings):
    cl.user_session.set("user_model", settings["Model"])
    user_options = cl.user_session.get("user_options")
    user_options["temperature"] = settings["Temperature"]


@ cl.on_message  # marks a function that should be run each time the chatbot receives a message from a user
async def main(message: cl.Message):

    # call responder, either openAI or local ollama
    # parse user prompt

    # call llm
    user_prompt = message.content
    user_model = cl.user_session.get("user_model")
    user_options = cl.user_session.get("user_options")

    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": user_prompt})

    msg = cl.Message(content="")
    await msg.stream_token("[MODEL: " + user_model + ", TEMP: " + str(user_options["temperature"]) + "]\n\n")

    # invoke selected responder
    if user_model.startswith("gpt"):
        # call open ai
        client = AsyncOpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        await msg.send()
        stream = await client.chat.completions.create(
            model=user_model, messages=message_history, stream=True, **user_options
        )
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await msg.stream_token(token)
    else:
        # call ollama
        async for chunk in await AsyncClient().chat(
            model=user_model, messages=message_history, stream=True, options=user_options
        ):
            token = chunk["message"]["content"]
            await msg.stream_token(token)

    # add response to message history
    message_history.append({"role": "assistant", "content": msg.content})

    # Send and close the message stream
    print("Done.")
    # await msg.send()
