from IPython.display import display, Markdown

class PromptTools:
    def __init__(self):
       
# Check here for the format of the templates: https://docs.mistral.ai/guides/rag/#combine-context-and-question-in-a-prompt-and-generate-response
# and also here https://docs.mistral.ai/guides/prompting_capabilities/
        self.SYSTEM_TEMPLATE = """ \
Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query.
If you do not know the answer, then say exactly "Ich weiss es nicht" and nothing else. 
If the context is not related to the question, then say exactly: "Dazu habe ich keine Information" and nothing else:
Answer:
"""

        self.USER_TEMPLATE = """ \
Query: {user_query}
"""

    def system_prompt(self,message: str) -> dict:
        return {"role": "system", "content": self.SYSTEM_TEMPLATE.format(context=message)}
    
    def assistant_prompt(self, message: str) -> dict:
        return {"role": "assistant", "content": self.ASSISTANT_TEMPLATE.format(assistant_response=message)}

    def user_prompt(self, message: str) -> dict:
        return {"role": "user", "content": self.USER_TEMPLATE.format(user_query=message)}

