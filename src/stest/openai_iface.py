import os
from openai import OpenAI

import tiktoken

# Local imports
from . import prompts


MAX_TOKENS = 2500
MODEL_TOKEN_LIMIT = 8192
MODEL = "gpt-4"
API_KEY = "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" # This is temp

client = OpenAI(api_key=API_KEY)


# @brief Interface to the OpenAI API
#
# @details This interface is a wrapper around the OpenAI API
#          and provides methods to send data to the model and
#          get responses from it.
#
class IOpenAI:
    def __init__(
        self, 
        model: str = MODEL, 
        max_tokens: int = MAX_TOKENS, 
        model_token_limit: int = MODEL_TOKEN_LIMIT
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.model_token_limit = model_token_limit

        messages = []
        responses = []

    ###############################
    # Public methods              #
    ###############################
    
    # @brief Sends the given prompt to the model and returns the response.
    #        The prompt is added to the conversation.
    # 
    # @param prompt The prompt to send to the model.
    # @return The response from the model.
    #
    # @throws ValueError if prompt is not set.
    def send_and_get_response(self, prompt: str = None) -> str:
        if not prompt:
            raise ValueError("prompt must be set")

        self.messages.append(prompt)
        response = client.completions.create(model=self.model, messages=self.messages)
        chatgpt_response = response.choices[0].message["content"].strip()
        self.responses.append(chatgpt_response)

        return chatgpt_response


    # @brief Sends the given content to the model in chunks.
    #
    # @details Sends the prompt at the start of the conversation
    #          and then sends the data_to_send to the model in chunks.
    #
    # @param initial_prompt The prompt to send to the model at the start of the conversation.
    # @param data_to_send The data to send to the model in chunks.
    # @return The response from the model.
    #
    # @throws ValueError if initial_prompt or data_to_send is not set.
    # @throws OpenAIError if the model returns an error.
    def send_data_in_chunks_and_get_response(
        self, 
        initial_prompt: str = None, 
        data_to_send: str = None
    ) -> str:
        if not initial_prompt:
            raise ValueError("initial_prompt must be set")
        if not data_to_send:
            raise ValueError("data_to_send must be set")

        tokenizer = tiktoken.encoding_for_model(self.model)
        chunk_size = self.max_tokens - len(tokenizer.encode(initial_prompt))
        chunks = self.__split_data_into_chunks(data_to_send, chunk_size)

        self.messages = [
            {"role": "user", "content": initial_prompt},
            {"role": "user", "content": prompts.SEND_FILE_PROMPT},
        ]

        for chunk in chunks:
            self.messages.append({"role": "user", "content": chunk})
            self.__remove_oldest_chunk_if_token_limit_exceeded(tokenizer, self.model_token_limit)

        self.send_and_get_response(prompts.ALL_PARTS_SENT_PROMPT)

    ###############################
    # Private methods             #
    ###############################

    # @brief Splits the given data into chunks given the chunk size.
    #
    # @param data The data to split into chunks.
    # @param chunk_size The size of each chunk.
    # @return The list of chunks.
    def __split_data_into_chunks(self, data: str, chunk_size: int) -> list[str]:
        if len(data) <= chunk_size:
            return [data]

        tokenizer = tiktoken.encoding_for_model(self.model)
        token_integers = tokenizer.encode(data)

        chunks = [
            token_integers[i : i + chunk_size]
            for i in range(0, len(token_integers), chunk_size)
        ]

        return [tokenizer.decode(chunk) for chunk in chunks]


    # @brief Removes the oldest chunk from the messages if the token limit is exceeded.
    def __remove_oldest_chunk_if_token_limit_exceeded(self, tokenizer, model_token_limit) -> None:
        while (
            sum(len(tokenizer.encode(message["content"])) for message in self.messages)
            > model_token_limit
        ):
            self.messages.pop(1)

