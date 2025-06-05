import asyncio
import logging
import grpc
import sys
from dotenv import load_dotenv
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "protobuffs"))
from protobuffs import odservice_pb2, odservice_pb2_grpc
from ImageProcessor import ImageProcessor
import requests

load_dotenv()


PORT = os.getenv("LICENSE_PLATE_DETECTOR_PORT")




class OdService(odservice_pb2_grpc.OdServiceServicer):

    def __init__(self):
        # Initialize the object tracker once in the service class
        self.image_processor = ImageProcessor()
    
    async def UploadImage(self, request_iterator, context):
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

        # if isinstance(result, Exception):
        #     self.video_processed_flag=False
        #     print(f"Error occurred while processing image: {str(result)}")
        #     # Respond to client with failure message
        #     return odservice_pb2.ImageResponse(
        #         success=False,
        #         message=f"Failed to process image: {str(result)}",
        #         process_time = result['process_time'],
        #         throughput = result['throughput'],
        #         power = result['power'],
        #         cpu_utilized = result['cpu_utilized'],
        #         memory_utilized = result['memory_utilized']
        #     )

        # Respond to client
        return odservice_pb2.ImageResponse(
            success=result['success'],
            message=result['message'],
            process_time = result['process_time'],
            throughput = result['throughput'],
            power = result['power'],
            cpu_utilized = result['cpu_utilized'],
            memory_utilized = result['memory_utilized']

        )
    
    
    async def SendLogEntry(self, log_message, context):
        success, log_status = self.image_processor.add_logs(log_message)
        
        if success:
        # Return a success response
            logging.info("Logs saved to DB", exc_info=False)
            return odservice_pb2.LogResponse(success=success, message=log_status)
        else:
            logging.error("Failed to save Logs", exc_info=False)
            return odservice_pb2.LogResponse(success=success, message=log_status)

    
        # except Exception as e:
        # # Handle any unexpected errors
        #     error_message = f"Error saving log entry: {str(e)}"
        #     print(error_message)  # Log the error on the server side
        #     # 
        #     return odservice_pb2.LogResponse(
        #         success=False,
        #         message=f"Failed to save logs: {error_message}"
        #     )


async def serve() -> None:
    server = grpc.aio.server()
    odservice_pb2_grpc.add_OdServiceServicer_to_server(OdService(), server)
    listen_addr = f"[::]:{PORT}"
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
