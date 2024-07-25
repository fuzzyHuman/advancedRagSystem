import os
import time
import requests
import json
from typing import Iterable, List, Optional, Union

from pinecone_plugins.assistant.data.core.client.api.manage_assistants_api import ManageAssistantsApi as DataApiClient
from pinecone_plugins.assistant.data.core.client.model.inline_object1 import InlineObject1 as ChatRequest
from pinecone_plugins.assistant.control.core.client.models import Assistant as OpenAIAssistantModel
from pinecone_plugins.assistant.data.core.client.model.assistant_chat_assistant_name_chat_completions_messages \
    import AssistantChatAssistantNameChatCompletionsMessages as ChatContext
from pinecone_plugins.assistant.data.core.client import ApiClient
from pinecone import config

from pinecone_plugins.assistant.models.file_model import FileModel

from .chat import ChatResultModel, Message, StreamingChatResultModel

class AssistantModel:
    def __init__(self, assistant: OpenAIAssistantModel, client_builder, config):
        self.assistant = assistant
        self.host = os.getenv("PINECONE_PLUGIN_ASSISTANT_DATA_HOST", "https://prod-1-data.ke.pinecone.io")
        self.config = config if config else {}

        if self.host.endswith("/"):
            self.host = self.host[:-1]
        self._assistant_data_api = client_builder(ApiClient, DataApiClient, 'unstable', host=self.host)
        # initialize types so they can be accessed
        self.name = self.assistant.name
        self.created_at = self.assistant.created_at
        self.updated_at = self.assistant.updated_at
        self.metadata = self.assistant.metadata
        self.status = self.assistant.status
        self.ctxs = []

    def __str__(self):
        return str(self.assistant)
    
    def __repr__(self):
        return repr(self.assistant)

    def __getattr__(self, attr):
        return getattr(self.assistant, attr)
    
    def upload_file(
        self, 
        file_path: str,
        timeout: Optional[int] = None
    ) -> FileModel:
        """
        Uploads a file from the specified path to this assistant for internal processing.

        :param file_path: The path to the file that needs to be uploaded.
        :type file_path: str, required

        :type timeout: int, optional
        :param timeout: Specify the number of seconds to wait until file processing is done. If None, wait indefinitely; if >=0, time out after this many seconds;
            if -1, return immediately and do not wait. Default: None

        :return: FileModel object with the following properties:
            - id: The UUID of the uploaded file.
            - name: The name of the uploaded file.
            - created_on: The timestamp of when the file was created.
            - updated_on: The timestamp of the last update to the file.
            - metadata: Metadata associated with the file.
            - status: The status of the file.

        Example:
        >>> km = (...).assistant.Model("model_name")
        >>> file_model = km.upload_file(file_path="/path/to/file.txt") # use the default timeout
        >>> print(file_model)
          {'created_on': '2024-06-02T19:48:00Z',
          'id': '070513b3-022f-4966-b583-a9b12e0920ff',
          'metadata': None,
          'name': 'tiny_file.txt',
          'status': 'Available',
          'updated_on': '2024-06-02T19:48:00Z'}
        """
        
        try:
            with open(file_path, 'rb') as file:
                upload_resp = self._assistant_data_api.upload_file(assistant_name=self.assistant.name, file=file)

                # wait for status
                if timeout == -1:
                    # still in processing state
                    return FileModel(file_model=upload_resp)
                if timeout is None:
                    while not upload_resp.status == 'Available':
                        time.sleep(5)
                        upload_resp = self.describe_file(upload_resp.id)
                else:
                    while not upload_resp.status == 'Available' and timeout >= 0:
                        time.sleep(5)
                        timeout -= 5
                        upload_resp = self.describe_file(upload_resp.id)

                if timeout and timeout < 0:
                    raise (
                        # TODO: fix url
                        TimeoutError(
                            "Please call the describe_file API ({}) to confirm model status.".format(
                                "https://www.pinecone.io/docs/api/operation/assistant/describe_model/"
                            )
                        )
                    )
                return FileModel(file_model=upload_resp)
        except FileNotFoundError:
            raise Exception(f"Error: The file at {file_path} was not found.")
        except IOError:
            raise Exception(f"Error: Could not read the file at {file_path}.")
    
    def describe_file(self, file_id: str) -> FileModel:
        """
        Describes a file with the specified file_id from this assistant. Includes information on its status and metadata.

        :param : The file id of the file to be described
        :type file_id: str, required

        :return: FileModel object with the following properties:
            - id: The UUID of the requested file.
            - name: The name of the requested file.
            - created_on: The timestamp of when the file was created.
            - updated_on: The timestamp of the last update to the file.
            - metadata: Metadata associated with the file.
            - status: The status of the file.

        Example:
        >>> km = (...).assistant.Model("model_name")
        >>> file_model = km.upload_file(file_path="/path/to/file.txt") # use the default timeout
        >>> print(file_model)
          {'created_on': '2024-06-02T19:48:00Z',
          'id': '070513b3-022f-4966-b583-a9b12e0290ff',
          'metadata': None,
          'name': 'tiny_file.txt',
          'status': 'Available',
          'updated_on': '2024-06-02T19:48:00Z'}
        >>> km.describe_file(file_id='070513b3-022f-4966-b583-a9b12e0290ff')
          {'created_on': '2024-06-02T19:48:00Z',
          'id': '070513b3-022f-4966-b583-a9b12e0290ff',
          'metadata': None,
          'name': 'tiny_file.txt',
          'status': 'Available',
          'updated_on': '2024-06-02T19:48:00Z'}
        """

        file = self._assistant_data_api.describe_file(assistant_name=self.name, assistant_file_id=file_id)
        return FileModel(file_model=file) 

    def list_files(self) -> List[FileModel]:
        """
        Lists all uploaded files in this assistant.

        :return: List of FileModel objects with the following properties:
            - id: The UUID of the requested file.
            - name: The name of the requested file.
            - created_on: The timestamp of when the file was created.
            - updated_on: The timestamp of the last update to the file.
            - metadata: Metadata associated with the file.
            - status: The status of the file.

        Example:
        >>> km = (...).assistant.Model("model_name")
        >>> km.list_files()
          [{'created_on': '2024-06-02T19:48:00Z',
          'id': '070513b3-022f-4966-b583-a9b12e0290ff',
          'metadata': None,
          'name': 'tiny_file.txt',
          'status': 'Available',
          'updated_on': '2024-06-02T19:48:00Z'}, ...]
        """
        files_resp = self._assistant_data_api.list_files(self.name)
        return [FileModel(file_model=file) for file in files_resp.files]

    def delete_file(
        self, 
        file_id: str,
        timeout: Optional[int] = None 
    ):
        """
        Deletes a file with the specified file_id from this assistant.

        :param file_path: The path to the file that needs to be uploaded.
        :type file_path: str, required

        :type timeout: int, optional
        :param timeout: Specify the number of seconds to wait until file processing is done. If None, wait indefinitely; if >=0, time out after this many seconds;
            if -1, return immediately and do not wait. Default: None

        Example:
        >>> km = (...).assistant.Model("model_name")
        >>> km.delete_file(file_id='070513b3-022f-4966-b583-a9b12e0290ff') # use the default timeout
        >>> km.list_files()
          []
        """
        self._assistant_data_api.delete_file(assistant_name=self.name, assistant_file_id=file_id)

        if timeout == -1:
            # still in processing state
            return
        if timeout is None:
            file = self.describe_file(file_id=file_id)
            while file:
                time.sleep(5)
                try:
                    file = self.describe_file(file_id=file_id)
                except Exception:
                    file = None
        else:
            file = self.describe_file(file_id=file_id)
            while file and timeout >= 0:
                time.sleep(5)
                timeout -= 5
                try:
                    file = self.describe_file(file_id=file_id)
                except Exception:
                    file = None

        if timeout and timeout < 0:
            raise (
                TimeoutError(
                    "Please call the describe_model API ({}) to confirm model status.".format(
                        "https://www.pinecone.io/docs/api/operation/assistant/describe_model/"
                    )
                )
            ) 

        
    def chat_completions(self, messages: List[Message], stream: bool = False) -> Union[ChatResultModel, Iterable[StreamingChatResultModel]]:
        """
        Performs a chat completion request to the following assistant.

        :param messages: The current context for the chat request. The final element in the list represents the user query to be made from this context.
        :type messages: List[Message] where Message requires the following:
            Message:
                - role: str, the role of the context ('user' or 'agent')
                - content: str, the content of the context
        
        :param stream: If this flag is turned on, then the return type is an Iterable[StreamingChatResultModel] whether data is returned as a generator/stream
        :type stream: bool (default false)
        
        :return: 
        The default result is a ChatResultModel with the following format:
            {
                "choices": [
                    {
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": "The 2020 World Series was played in Texas at Globe Life Field in Arlington.",
                        "role": "assistant"
                    },
                    "logprobs": null
                    }
                ],
                "id": "chatcmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW",
                "model": "gpt-3.5-turbo-0613",
            }

        However, when stream is set to true, the response is an iterable of StreamingChatResultModel's. See examples below:
            {
                "choices": [
                    {
                    "finish_reason": null,
                    "index": 0,
                    "delta": {
                        "content": "The",
                        "role": ""
                    },
                    "logprobs": null
                    }
                ],
                "id": "chatcmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW",
                "model": "gpt-3.5-turbo-0613",
            }
        
        Example:
        >>> from pinecone_plugins.assistant.models import Message 
        >>> km = (...).assistant.Model("planets-km")
        >>> chat_context = [Message(role='user', content='How old is the earth')]
        >>> resp = km.chat_completions(chat_context=chat_context)
        >>> print(resp)
        {'choices': [{'finish_reason': 'stop',
              'index': 0,
              'message': {'content': 'The age of the Earth is estimated to be '
                                     'about 4.54 billion years, based on '
                                     'evidence from radiometric age dating of '
                                     'meteorite material and Earth rocks, as '
                                     'well as lunar samples. This estimate has '
                                     'a margin of error of about 1%.',
                          'role': 'assistant'}}],
        'id': 'chatcmpl-9VmkSD9s7rfP28uScLlheookaSwcB',
        'model': 'planets-km'}

        Streaming example:
        >>> resp = km.chat_completions(chat_context=chat_context)
        >>> for chunk in resp:
                if chunk:  
                    print(chunk)
        
        [{'choices': [{'finish_reason': 'stop',
              'index': 0,
              'delta': {'content': 'The age of the Earth is estimated to be '
                                     'about 4.54 billion years, based on '
                                     'evidence from radiometric age dating of '
                                     'meteorite material and Earth rocks, as '
                                     'well as lunar samples. This estimate has '
                                     'a margin of error of about 1%.',
                          'role': 'assistant'}}],
        'id': 'chatcmpl-9VmkSD9s7rfP28uScLlheookaSwcB',
        'model': 'planets-km'}, ... ]
        
        """
        if stream:
            return self._chat_completions_streaming(messages=messages)
        else:
            return self._chat_completions_single(messages=messages)

    def _chat_completions_single(self, messages: List[Message]) -> ChatResultModel:
        messages = [ChatContext(role=ctx.role, content=ctx.content) for ctx in messages]
        context = ChatRequest(messages=messages)
        search_result = self._assistant_data_api.chat_completion_assistant(
            assistant_name=self.name, 
            inline_object1=context
        )
        return search_result
    
    def _chat_completions_streaming(self, messages: List[Message]) -> Iterable[StreamingChatResultModel]:
        api_key = self.config.api_key
        base_url = f"{self.host}/assistant/chat/{self.name}/chat/completions"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        messages = [vars(message) for message in messages]
        content = {
            "messages": messages, 
            "stream": True
        }

        try:
            response = requests.post(
                base_url, headers=headers, json=content, timeout=60, stream=True
            )
            response.raise_for_status()

            response_text = ""
            for line in response.iter_lines():
                if line:
                    data = line.decode("utf-8")
                    if data.startswith("data:"):
                        data = data[5:]
                    
                    json_data = json.loads(data)
                    res = StreamingChatResultModel(data=json_data)
                    
                    yield res
        except Exception as e:
            raise ValueError(f"Error in chat completions streaming: {e}")
            return []