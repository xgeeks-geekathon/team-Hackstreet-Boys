import os
from openai import OpenAI
from dotenv import load_dotenv

import httpx
import tiktoken
from tiktoken import encoding_for_model

# Local imports
from . import prompts

# Load environment variables from .env file
load_dotenv()


# Get the values from the environment variables or use default values
MODEL = os.getenv("MODEL")
API_KEY = os.getenv("API_KEY")
MAX_TOKENS = int(os.getenv("MAX_TOKENS"))
MODEL_TOKEN_LIMIT = int(os.getenv("MODEL_TOKEN_LIMIT"))


# Async HTTP client
async_client = httpx.AsyncClient()


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

        self.messages = []
        self.responses = []

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
    async def send_messages_and_get_response(self):
        response = await async_client.post(
            url="https://api.openai.com/v1/chat/completions",
            json={
                "messages": self.messages,
                "model": self.model,
                "max_tokens": self.max_tokens,
            },
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        response.raise_for_status()
        return response.json()

    # @brief Sends the given content to the model in chunks.
    #
    # @details Sends the prompt at the start of the conversation
    #          and then sends the data_to_send to the model in chunks.
    #
    #          Chat GPT will perform the task described in initial_prompt
    #          on the data after all the chunks have been fed.
    #
    #          This function returns the response as a string.
    #
    # @param initial_prompt The prompt to send to the model at the start of the conversation.
    # @param data_to_send The data to send to the model in chunks.
    # @return The response from the model.
    #
    # @throws ValueError if initial_prompt or data_to_send is not set.
    # @throws OpenAIError if the model returns an error.
    async def send_data_in_chunks_and_get_response(
            self,
            initial_prompt: str = None,
            data_to_send: str = None
    ) -> str:
        if not initial_prompt or not data_to_send:
            raise ValueError("initial_prompt and data_to_send must be set")

        tokenizer = encoding_for_model(self.model)
        chunk_size = self.max_tokens - len(tokenizer.encode(initial_prompt))
        chunks = self.__split_data_into_chunks(data_to_send, chunk_size)

        self.__append_message_as(initial_prompt, "user")
        self.__append_message_as(prompts.SEND_FILE_PROMPT, "user")

        for chunk in chunks:
            self.__append_message_as(chunk, "user")
            self.__remove_oldest_chunk_if_token_limit_exceeded(tokenizer, self.model_token_limit)

            response = await self.send_messages_and_get_response()

        self.__append_message_as(prompts.ALL_PARTS_SENT_PROMPT, "user")
        response = await self.send_messages_and_get_response()
        return response["choices"][0]["message"]["content"].split()

    # @brief Clears the message history
    def clear_message_history(self) -> None:
        self.messages = []

    ###############################
    # Private methods             #
    ###############################

    # @brief Splits the given data into chunks given the chunk size.
    # @param data The data to split into chunks.
    # @param chunk_size The size of each chunk.
    # @return The list of chunks.
    def __split_data_into_chunks(self, data: str, chunk_size: int) -> list[str]:
        if len(data) <= chunk_size:
            return [data]

        tokenizer = tiktoken.encoding_for_model(self.model)
        token_integers = tokenizer.encode(data)

        chunks = [
            token_integers[i: i + chunk_size]
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

    # @brief Appends the given message to the messages list as the given role.
    def __append_message_as(self, message: str, role: str) -> None:
        self.messages.append({"role": role, "content": message})
