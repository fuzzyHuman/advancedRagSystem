from pinecone_plugin_interface import PluginMetadata
from .assistant import Assistant


__installables__ = [
    PluginMetadata(
        target_object="Pinecone",
        namespace="assistant",
        implementation_class=Assistant
    ) 
]