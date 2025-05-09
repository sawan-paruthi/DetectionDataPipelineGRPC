import asyncio
import logging
import grpc
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "protobuffs"))
from protobuffs import odservice_pb2, odservice_pb2_grpc
from ImageProcessor import ImageProcessor
import requests


LOG_FILE = 'server_logs.json'




class OdService(odservice_pb2_grpc.OdServiceServicer):

    def __init__(self):
        # Initialize the object tracker once in the service class
        self.image_processor = ImageProcessor()
        self.image_processed_flag = True
    
    async def UploadImage(self, request_iterator, context):
        global ot_time
        first=True
        total_data = b""
        model_name=""
        self.image_processed_flag=True
        print("inside upload image function")
        async for image_request in request_iterator:
            print("inside request iterator")
            total_data += image_request.image_file
            if image_request.model:
                model_name = image_request.model  # Capture model name from request

        with open('received_image.jpg', 'wb') as f:
            f.write(total_data)
        
        print(f"model name is:{model_name}")
        
        result = self.image_processor.process_image(model_name)

        if isinstance(result, Exception):
            self.video_processed_flag=False
            print(f"Error occurred while processing image: {str(result)}")
            # Respond to client with failure message
            return odservice_pb2.ImageResponse(
                success=False,
                message=f"Failed to process video: {str(result)}"
            )

        # Respond to client
        return odservice_pb2.ImageResponse(
            success=True,
            message=result['message'],
            process_time = result['process_time'],
            throughput = result['throughput'],
            power = result['power'],
            cpu_utilized = result['cpu_utilized'],
            memory_utilized = result['memory_utilized']

        )
    
    
    
    async def SendLogEntry(self, log_message, context):
        try:
        # Retrieve log entry data from request
            if not self.image_processed_flag:
                raise Exception("No logs generated as the video was not processed successfully.")

            
            log_entry_string = self.image_processor.add_logs(log_message)

        # Return a success response
            return odservice_pb2.LogResponse(success=True, message=log_entry_string)
    
        except Exception as e:
        # Handle any unexpected errors
            error_message = f"Error processing log entry: {str(e)}"
            print(error_message)  # Log the error on the server side
            # return otservice_pb2.LogResponse(success=False, message=error_message)
            return odservice_pb2.LogResponse(
                success=False,
                message=f"Failed to process image: {error_message}"
            )


async def serve() -> None:
    server = grpc.aio.server()
    odservice_pb2_grpc.add_OdServiceServicer_to_server(OdService(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
