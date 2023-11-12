import os
from openai import OpenAI

import tiktoken

# Local imports
from . import prompts


MAX_TOKENS = 2500
MODEL_TOKEN_LIMIT = 8192
MODEL = "gpt-4"
API_KEY = "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"  # This is temp

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
    def send_messages_and_get_response(self):
        return client.chat.completions.create(
            messages=self.messages,
            model=self.model,
            max_tokens=self.max_tokens,
        )

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
    def send_data_in_chunks_and_get_response(
            self,
            initial_prompt: str = None,
            data_to_send: str = None
    ) -> str:
        if not initial_prompt:
            raise ValueError("initial_prompt must be set")
        if not data_to_send:
            raise ValueError("data_to_send must be set")

        # Encode the initial prompt and data to send in UTF-8
        utf8_encoded_initial_prompt = initial_prompt.encode('utf-8')
        utf8_encoded_data = data_to_send.encode('utf-8')

        # Calculate the chunk size based on UTF-8 encoded data
        chunk_size = self.max_tokens - len(utf8_encoded_initial_prompt)

        # Split the UTF-8 encoded data into chunks
        chunks = self.__split_data_into_chunks(utf8_encoded_data, chunk_size)

        # Decode the initial prompt chunk back into a string
        initial_prompt_decoded = utf8_encoded_initial_prompt.decode('utf-8')
        self.__append_message_as(initial_prompt_decoded, "user")
        self.__append_message_as(prompts.SEND_FILE_PROMPT, "user")

        # Send the data in chunks
        for chunk in chunks:
            # Decode each chunk back into a string before sending
            chunk_decoded = chunk.decode('utf-8')
            self.__append_message_as(chunk_decoded, "user")
            self.__remove_oldest_chunk_if_token_limit_exceeded(self.max_tokens)

            response = self.send_messages_and_get_response()

        # Send transmission end signal
        self.__append_message_as(prompts.ALL_PARTS_SENT_PROMPT, "user")
        response = self.send_messages_and_get_response()
        return response.choices[0].message.content

    # @brief Clears the message history
    def clear_message_history(self) -> None:
        self.messages = []


    ###############################
    # Private methods             #
    ###############################

    # @brief Splits the given data into chunks given the chunk size.
    #
    # @param data The data to split into chunks.
    # @param chunk_size The size of each chunk.
    # @return The list of chunks.
    def __split_data_into_chunks(self, data: bytes, chunk_size: int) -> list[bytes]:
        if len(data) <= chunk_size:
            return [data]

        chunks = [
            data[i:i + chunk_size]
            for i in range(0, len(data), chunk_size)
        ]

        return chunks

    # @brief Removes the oldest chunk from the messages if the token limit is exceeded.
    def __remove_oldest_chunk_if_token_limit_exceeded(self, model_token_limit) -> None:
        while (
                sum(len(message["content"].encode('utf-8')) for message in self.messages)
                > model_token_limit
        ):
            self.messages.pop(1)

    # @brief Appends the given message to the messages list as the given role.
    def __append_message_as(self, message: str, role: str) -> None:
        self.messages.append({"role": role, "content": message})
