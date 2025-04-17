import grpc
import odservice_pb2_grpc, odservice_pb2
import grpc.aio
import asyncio


# when video is comming from the client and stored at client server
async def image_file_generator(file_path):
    with open(file_path, 'rb') as f:
        chunk_size = 1024 * 1024  # 1MB chunks
        while chunk := f.read(chunk_size):
            yield odservice_pb2.ImageRequest(image_file=chunk, model="loloyolo")


# when video is comming from user from the flask app
async def in_memory_image_file_generator(in_memory_file, model_name):
    chunk_size = 1024 * 1024  
    in_memory_file.seek(0)  
    while chunk := in_memory_file.read(chunk_size):
        yield odservice_pb2.ImageRequest(image_file=chunk, model=model_name)


async def upload_image_to_grpc(in_memory_file, model_name):
    """
    Handles the gRPC communication and uploads the video using the provided generator.
    """
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = odservice_pb2_grpc.OdServiceStub(channel)
        response = await stub.UploadImage(in_memory_image_file_generator(in_memory_file, model_name))
    return response


async def send_log_entry_to_grpc(request):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = odservice_pb2_grpc.OdServiceStub(channel)

        data = request.get_json()
        
        # Create a LogEntry message
        log_message = odservice_pb2.LogEntry(
            service_name = data['service_name'],
            ip_address = request.remote_addr,
            process_time = data['process_time'],
            grpc_response_time = data['grpc_response_time'],
            total_response_time = data['total_response_time'],
            throughput = data['throughput'],
            power = data['power']
        )


        # Send the log entry to the server
        response = await stub.SendLogEntry(log_message)

        # Check for a successful response
        if response.success:
            print("Log entry successfully sent to the server.")
        else:
            print(f"Failed to send log entry: ")
            print(response.message)
            return response
        
        return response



async def run():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = odservice_pb2_grpc.OdServiceStub(channel)
        response = await stub.UploadImage(image_file_generator("C:\\Users\\12514\\Desktop\\LicensePlateDetectorGRPC\\client\\data\\testBL.jpg"))
        print(f"Response: {response.message}, Success: {response.success}")

if __name__ == '__main__':
    asyncio.run(run())
