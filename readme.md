
### For generating GRPC files

python -m grpc_tools.protoc -I..\protos --python_out=. --pyi_out=. --grpc_python_out=. ..\protos\odservice.proto

py -3.8 -m venv venv38


for server side grpc generation
python -m grpc_tools.protoc -I..\protos --python_out=protobuffs --grpc_python_out=protobuffs ..\protos\odservice.proto
