from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ImageRequest(_message.Message):
    __slots__ = ("image_file", "model")
    IMAGE_FILE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    image_file: bytes
    model: str
    def __init__(self, image_file: _Optional[bytes] = ..., model: _Optional[str] = ...) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = ("success", "message", "process_time", "throughput", "power", "cpu_utilized", "memory_utilized")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROCESS_TIME_FIELD_NUMBER: _ClassVar[int]
    THROUGHPUT_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    CPU_UTILIZED_FIELD_NUMBER: _ClassVar[int]
    MEMORY_UTILIZED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    process_time: float
    throughput: float
    power: float
    cpu_utilized: float
    memory_utilized: float
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., process_time: _Optional[float] = ..., throughput: _Optional[float] = ..., power: _Optional[float] = ..., cpu_utilized: _Optional[float] = ..., memory_utilized: _Optional[float] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ("success", "message", "service_name", "ip_address", "process_time", "grpc_response_time", "total_response_time", "throughput", "power", "cpu_utilized", "memory_utilized")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PROCESS_TIME_FIELD_NUMBER: _ClassVar[int]
    GRPC_RESPONSE_TIME_FIELD_NUMBER: _ClassVar[int]
    TOTAL_RESPONSE_TIME_FIELD_NUMBER: _ClassVar[int]
    THROUGHPUT_FIELD_NUMBER: _ClassVar[int]
    POWER_FIELD_NUMBER: _ClassVar[int]
    CPU_UTILIZED_FIELD_NUMBER: _ClassVar[int]
    MEMORY_UTILIZED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    service_name: str
    ip_address: str
    process_time: float
    grpc_response_time: float
    total_response_time: float
    throughput: float
    power: float
    cpu_utilized: float
    memory_utilized: float
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., service_name: _Optional[str] = ..., ip_address: _Optional[str] = ..., process_time: _Optional[float] = ..., grpc_response_time: _Optional[float] = ..., total_response_time: _Optional[float] = ..., throughput: _Optional[float] = ..., power: _Optional[float] = ..., cpu_utilized: _Optional[float] = ..., memory_utilized: _Optional[float] = ...) -> None: ...

class LogResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
