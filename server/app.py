import asyncio
import logging
import grpc
import sys
from dotenv import load_dotenv
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "protobuffs"))
from protobuffs import odservice_pb2, odservice_pb2_grpc
from ImageProcessor import ImageProcessor
import argparse
load_dotenv()


class OdService(odservice_pb2_grpc.OdServiceServicer):

    def __init__(self, service, prefix, server_id):
        # Initialize the object tracker once in the service class
        self.image_processor = ImageProcessor(service, prefix, server_id)
    
    async def UploadImage(self, request_iterator, context):
        total_data = b""
        model_name=""
        self.image_processed_flag=True
        # print("inside upload image function")
        async for image_request in request_iterator:
            # print("inside request iterator")
            total_data += image_request.image_file
            if image_request.model:
                model_name = image_request.model  # Capture model name from request

        
        inbound_path = os.path.abspath("inbound")
        # print(f"inbound path is {inbound_path}")
        os.makedirs(inbound_path, exist_ok=True)
        file_path = os.path.join(inbound_path, "received_image.jpg")

        with open(file_path, 'wb') as f:
            f.write(total_data)
        
        # print(f"model name is:{model_name}")
        
        result = self.image_processor.process_image(model_name, img_path=file_path)

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
            logging.info("App: Logs saved to DB", exc_info=False)
            return odservice_pb2.LogResponse(success=success, message=log_status)
        else:
            logging.error("App: Failed to save Logs", exc_info=False)
            return odservice_pb2.LogResponse(success=success, message=log_status)


async def serve(port, service, prefix, server_id) -> None:
    server = grpc.aio.server()
    odservice_pb2_grpc.add_OdServiceServicer_to_server(OdService(service, prefix, server_id), server)
    listen_addr = f"[::]:{port}"
    server.add_insecure_port(listen_addr)
    logging.info("App: Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="add service name and prefix for model")
    parser.add_argument('--service', required=True, type=str, help='Service type. For exaample - License Plate Service')
    parser.add_argument('--prefix', required=True, type=str, help='prefix for Service type. For exaample - lp for License Plate Service')
    parser.add_argument('--port', required=True, type=str, help='port on which service should host. For exaample - 50051')
    parser.add_argument('--serverid', required=True, type=str, help='ID of server on which this application is running')
    args = parser.parse_args()
    

    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve(args.port, args.service, args.prefix, args.serverid))
