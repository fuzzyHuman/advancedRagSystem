import time
import os 
from typing import Optional, Dict, List

from pinecone_plugin_interface import PineconePlugin

from pinecone_plugins.assistant.control.core.client.api.manage_assistants_api import ManageAssistantsApi as ControlApiClient 
from pinecone_plugins.assistant.control.core.client.model.inline_object import InlineObject as CreateModelRequest
from pinecone_plugins.assistant.control.core.client import ApiClient

from pinecone_plugins.assistant.models import AssistantModel

from pinecone.utils import setup_openapi_client

class Assistant(PineconePlugin):
    """
    The `Assistant` class configures and utilizes the Pinecone Assistant Engine API to create and manage Assistants.

    :param config: A `pinecone.config.Config` object, configured and built in the Pinecone class.
    :type config: `pinecone.config.Config`, required

    :param client_builder: A `pinecone.utils` closure of setup_openapi_client, configured and built in the Pinecone class.
    :type client_builder: `(type(OpenApiClient), type(ClientApiClass), str, **kwargs)->ClientApiClass`, required
    """
    def __init__(self, config, client_builder):
        self.config = config

        self.host = os.getenv("PINECONE_PLUGIN_ASSISTANT_CONTROL_HOST", "https://api.pinecone.io")
        if self.host.endswith("/"):
            self.host = self.host[:-1]
        self._assistant_control_api = client_builder(ApiClient, ControlApiClient, 'unstable', host=self.host)
        self._client_builder = client_builder

    def create_assistant(
        self, 
        assistant_name: str, 
        metadata: dict[str, any] = {}, 
        timeout: Optional[int] = None,
    ) -> AssistantModel:
        """
        Creates a assistant with the specified name, metadata, and optional timeout settings.

        :param assistant_name: The name to assign to the assistant.
        :type assistant_name: str, required

        :param metadata: A dictionary containing metadata for the assistant.
        :type metadata: dict, optional

        :type timeout: int, optional
        :param timeout: Specify the number of seconds to wait until model operation is completed. If None, wait indefinitely; if >=0, time out after this many seconds;
            if -1, return immediately and do not wait. Default: None

        :return: AssistantModel object with properties `name`, `metadata`, 'status', 'updated_at' and `created_at`. 
        - The `name` property contains the name of the model. 
        - The `metadata` property contains the metadata provided. 
        - The `created_at` property contains the timestamp of when the model was created.
        - The `updated_at` property contains the timestamp of when the model was last updated. 
        - The `status` property contains the status of the model. This is one of:
            - 'Initializing' 
            - 'Ready'
            - 'Terminating'
            - 'Failed'

        Example:
        >>> metadata = {"author": "Jane Doe", "version": "1.0"}
        >>> model = (...).create_assistant(assistant_name="example_assistant", metadata=metadata, timeout=30)
        >>> print(model)
         {'created_at': '2024-06-02T19:01:17Z',
          'metadata': {'author': 'Jane Doe', 'version': '1.0'},
          'name': 'example_assistant',
          'status': 'Ready',
          'updated_at': '2024-06-02T19:01:17Z'}
        """ 
        inline_object = CreateModelRequest(name=assistant_name, metadata=metadata)
        assistant = self._assistant_control_api.create_assistant(inline_object=inline_object)

        if timeout == -1:
            # still in processing state
            return AssistantModel(assistant=assistant, client_builder=self._client_builder, config=self.config)
        if timeout is None:
            while not assistant.status == 'Ready':
                time.sleep(5)
                assistant = self.describe_assistant(assistant_name)
        else:
            while not assistant.status == 'Ready' and timeout >= 0:
                time.sleep(5)
                timeout -= 5
                assistant = self.describe_assistant(assistant_name)

        if timeout and timeout < 0:
            raise (
                # TODO: clarify errors
                TimeoutError(
                    "Please call the describe_assistant API ({}) to confirm model status.".format(
                        "https://www.pinecone.io/docs/api/operation/assistant/describe_assistant/"
                    )
                )
            )

        return AssistantModel(assistant=assistant, client_builder=self._client_builder, config=self.config)

    def describe_assistant(
        self, assistant_name: str
    ) -> AssistantModel:
        """
        Describes a assistant with the specified name. Will raise a 404 if no model exists with the specified name.

        :param assistant_name: The name to assign to the assistant.
        :type assistant_name: str, required

        :return: AssistantModel object with properties `name`, `metadata`, 'status', 'updated_at' and `created_at`. 
        - The `name` property contains the name of the model. 
        - The `metadata` property contains the metadata provided. 
        - The `created_at` property contains the timestamp of when the model was created.
        - The `updated_at` property contains the timestamp of when the model was last updated. 
        - The `status` property contains the status of the model. This is one of:
            - 'Initializing' 
            - 'Ready'
            - 'Terminating'
            - 'Failed'

        Example:
        >>> model = (...).describe_assistant(assistant_name="example_assistant")
        >>> print(model)
         {'created_at': '2024-06-02T19:01:17Z',
          'metadata': {'author': 'Jane Doe', 'version': '1.0'},
          'name': 'example_assistant',
          'status': 'Ready',
          'updated_at': '2024-06-02T19:01:17Z'}
        """ 
        
        assistant = self._assistant_control_api.get_assistant(assistant_name=assistant_name)
        return AssistantModel(assistant=assistant, client_builder=self._client_builder, config=self.config)

    def list_assistants(
        self
    ) -> List[AssistantModel]:
        """
        Lists all assistants created from the current API Key. Will raise a 404 if no model exists with the specified name.

        :return: List of AssistantModel objects with properties `name`, `metadata`, 'status', 'updated_at' and `created_at`. 
        - The `name` property contains the name of the model. 
        - The `metadata` property contains the metadata provided. 
        - The `created_at` property contains the timestamp of when the model was created.
        - The `updated_at` property contains the timestamp of when the model was last updated. 
        - The `status` property contains the status of the model. This is one of:
            - 'Initializing' 
            - 'Ready'
            - 'Terminating'
            - 'Failed'

        Example:
        >>> models = (...).list_assistants(assistant_name="example_assistant")
        >>> print(model)
         [{'created_at': '2024-06-02T19:01:17Z',
          'metadata': {'author': 'Jane Doe', 'version': '1.0'},
          'name': 'example_assistant',
          'status': 'Ready',
          'updated_at': '2024-06-02T19:01:17Z'}]
        """ 
        assistants_resp = self._assistant_control_api.list_assistants()
        return [AssistantModel(assistant=assistant, client_builder=self._client_builder, config=self.config) for assistant in assistants_resp.assistants]
    
    def delete_assistant(
        self, 
        assistant_name: str,
        timeout: Optional[int] = None, 
    ) -> AssistantModel:
        """
        Deletes a assistant with the specified name. Will raise a 404 if no model exists with the specified name.

        :param assistant_name: The name to assign to the assistant.
        :type assistant_name: str, required

        :type timeout: int, optional
        :param timeout: Specify the number of seconds to wait until model operation is completed. If None, wait indefinitely; if >=0, time out after this many seconds;
            if -1, return immediately and do not wait. Default: None

        Example:
        >>> (...).delete_assistant(assistant_name="example_assistant", timeout=-1)
        >>> (...).describe_assistant(assistant_name="example_assistant")
         {'created_at': '2024-06-02T19:01:17Z',
          'metadata': {'author': 'Jane Doe', 'version': '1.0'},
          'name': 'example_assistant',
          'status': 'Terminating',
          'updated_at': '2024-06-02T19:01:17Z'}
        """ 
        
        self._assistant_control_api.delete_assistant(assistant_name=assistant_name)

        if timeout == -1:
            # still in processing state
            return
        if timeout is None:
            assistant = self.describe_assistant(assistant_name)
            while assistant:
                time.sleep(5)
                try:
                    assistant = self.describe_assistant(assistant_name)
                except Exception:
                    assistant = None
        else:
            assistant = self.describe_assistant(assistant_name)
            while assistant and timeout >= 0:
                time.sleep(5)
                timeout -= 5
                try:
                    assistant = self.describe_assistant(assistant_name)
                except Exception:
                    assistant = None

        if timeout and timeout < 0:
            raise (
                # TODO: clarify errors
                TimeoutError(
                    "Please call the describe_assistant API ({}) to confirm model status.".format(
                        "https://www.pinecone.io/docs/api/operation/assistant/describe_assistant/"
                    )
                )
            ) 

    def Assistant(
        self, assistant_name: str
    ) -> AssistantModel:
        """
        Describes a assistant with the specified name. Will raise a 404 if no model exists with the specified name.

        :param assistant_name: The name to assign to the assistant.
        :type assistant_name: str, required

        :return: AssistantModel object with properties `name`, `metadata`, 'status', 'updated_at' and `created_at`. 
        - The `name` property contains the name of the model. 
        - The `metadata` property contains the metadata provided. 
        - The `created_at` property contains the timestamp of when the model was created.
        - The `updated_at` property contains the timestamp of when the model was last updated. 
        - The `status` property contains the status of the model. This is one of:
            - 'Initializing' 
            - 'Ready'
            - 'Terminating'
            - 'Failed'

        Example:
        >>> model = (...).describe_assistant(assistant_name="example_assistant")
        >>> print(model)
         {'created_at': '2024-06-02T19:01:17Z',
          'metadata': {'author': 'Jane Doe', 'version': '1.0'},
          'name': 'example_assistant',
          'status': 'Ready',
          'updated_at': '2024-06-02T19:01:17Z'}
        """
        return self.describe_assistant(assistant_name)