from typing import Optional


class Message:
    def __init__(self, data: Optional[dict[str, any]] = None, **kwargs) -> None:
        if data:
            self.role = data.get("role")
            self.content = data.get("content")
        else:
            self.role = kwargs.get("role", "user")
            self.content = kwargs.get("content")
    
    def __str__(self) -> str:
        return str(vars(self))

    def __repr__(self):
        return str(vars(self))

    def __getattr__(self, attr):
        return vars(self).get(attr)
                       
class ChatResultModel:
    def __init__(self, data):
        self.data = data
        self.id = data.get("id")
        self.choices = [StreamChoice(data=choice_data) for choice_data in data.get("choices", [])]
        self.model = data.get("model")

    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return repr(self.data)

    def __getattr__(self, attr):
        return getattr(self.data, attr)

class StreamingChatResultModel:
    def __init__(self, data: dict[str, any]) -> None:
        self.data = data
        self.id = data.get("id")
        self.choices = [StreamChoice(data=choice_data) for choice_data in data.get("choices", [])]
        self.model = data.get("model")
    
    def __str__(self) -> str:
        return str(self.data)



class StreamChoice: 
    def __init__(self, data: dict[str, any]) -> None:
        self.index = data.get("index")
        self.delta = Message(data=data.get("delta"))
        self.finish_reason = data.get("finish_reason")
    
    def __str__(self) -> str:
        return str(vars(self))
    

class Choice: 
    def __init__(self, data: dict[str, any]) -> None:
        self.index = data.get("index")
        self.message = Message(data=data.get("message"))
        self.finish_reason = data.get("finish_reason")
    
    def __str__(self) -> str:
        return str(vars(self))