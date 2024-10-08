from openai import OpenAI

class GenerationTools:
    def __init__(self, 
                 generation_model: str = "all-minilm",):
        print("constructor here")
        self.generation_model = generation_model
        self.client = OpenAI(
            base_url = 'http://localhost:11434/v1',
            api_key='ollama', # api_key is required, but unused for local models
        )      
 
    def get_response(self, messages: list) -> str:
        return self.client.chat.completions.create(
            model=self.generation_model,
            messages=messages
        )
             
    def pretty_print(self, message: str) -> str:
        display(Markdown(message.choices[0].message.content))
        