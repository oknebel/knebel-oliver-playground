from IPython.display import display, Markdown


class PromptTools:

    USER_TEMPLATE_2 = """ \
{user_query}

CONTEXT:
{context}
"""

    SYSTEM_TEMPLATE_2 = """ \
You are a helpfull Expert, answering questions about the following topic:
TOPIC:
{context}
INSTRUCTIONS:
When asked about yourself, introduce yourself and your expertise using the information in TOPIC.
For all other questions use the provided CONTEXT for your answer. Provide exact quotations.
If you do not find information, then say exactly "I don't know" and nothing else.
 """

    def __init__(self):

        # Check here for the format of the templates: https://docs.mistral.ai/guides/rag/#combine-context-and-question-in-a-prompt-and-generate-response
        # and also here https://docs.mistral.ai/guides/prompting_capabilities/
        self.SYSTEM_TEMPLATE = """ \
CONTEXT:
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query.
If you do not find the answer in the context information, then say exactly "Ich weiss es nicht" and nothing else.
If the context is not related to the question, then say exactly: "Dazu habe ich keine Information" and nothing else:
Answer:
"""
        self.USER_TEMPLATE = """ \
Query: {user_query}
"""

    def system_prompt(self, message: str) -> dict:
        return {"role": "system", "content": self.SYSTEM_TEMPLATE.format(context=message)}

    def assistant_prompt(self, message: str) -> dict:
        return {"role": "assistant", "content": self.ASSISTANT_TEMPLATE.format(assistant_response=message)}

    def user_prompt(self, message: str) -> dict:
        return {"role": "user", "content": self.USER_TEMPLATE.format(user_query=message)}

    def user_prompt_rag(self, message: str, context: str) -> dict:
        return {"role": "user", "content": self.USER_TEMPLATE.format(user_query=message, context=context)}

    def set_user_template(self, template: str) -> dict:
        self.USER_TEMPLATE = template

    def set_system_template(self, template: str) -> dict:
        self.SYSTEM_TEMPLATE = template
