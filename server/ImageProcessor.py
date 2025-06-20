import os
import requests
import time
import json
import csv
import logging
from ObjectProcessor import ObjectProcessor
from LogEntry import LogEntry
from parameters import Parameters
import subprocess
import psutil


class ImageProcessor:
    def __init__(self, servicename, prefix, server_id):
        self.object_processor = ObjectProcessor(prefix)
        self.log_entry = LogEntry(servicename, server_id)
        self.params = Parameters()


    def process_image(self, model_name, img_path):

        # Record system resource usage before processing
        initial_power = self.params.get_power_usage_nvidia()
        process = psutil.Process(os.getpid())
        cpu_start = process.cpu_percent(interval=None)
        memory_info_start = process.memory_info().rss
        start_time = time.perf_counter()

        detections = []
        inference_error = None

        try:
            # print(model_name)
            self.object_processor.load_model(model_name)
            detections = self.object_processor.detect_objects(img_path)

        except FileNotFoundError as fnf_error:
            inference_error = f"FileNotFoundError: {fnf_error}"

        except ValueError as val_error:
            inference_error = f"ValueError: {val_error}"

        except AttributeError as attr_error:
            inference_error = f"AttributeError: {attr_error}"

        except TypeError as type_error:
            inference_error = f"TypeError: {type_error}"

        except RuntimeError as runtime_error:
            inference_error = f"RuntimeError: {runtime_error}"

        except Exception as e:
            inference_error = f"UnexpectedError: {str(e)}"

        # Measure final system resource usage
        end_time = time.perf_counter()
        final_power = self.params.get_power_usage_nvidia()
        cpu_end = process.cpu_percent(interval=None)
        memory_info_end = process.memory_info().rss

        # Compute metrics
        process_time = round((end_time - start_time) * 1000, 8)
        avg_power = round((initial_power + final_power) / 2, 4)
        throughput = round(self.params.get_throughput(process_time, img_path), 4)
        cpu_used_percent = round(cpu_end, 2)  ##might be wrong
        memory_used_mb = round((memory_info_end - memory_info_start) / (1024 * 1024), 4)

        #status
        if inference_error:
            status = False
        else:
            status = True

        # Build response
        metrics = {
            "message": f"Image Processed With Error: {inference_error}" if inference_error else "Image Processed Successfully",
            "success":status,
            "process_time": process_time,
            "throughput": throughput,
            "power": avg_power,
            "cpu_utilized": cpu_used_percent,
            "memory_utilized": memory_used_mb,
            "detections": detections
        }

        return metrics



    def add_logs(self, log_message):
        print("#######################################################")
        logging.info(f"ImageProcessor: {log_message}")

        errors = []

        # Try each method separately and collect any errors
        try:
            self.log_entry.add_user_data(log_message)
        except Exception as e:
            logging.error("Failed to add user data", exc_info=False)
            errors.append(f"add_user_data: {e}")

        try:
            self.log_entry.add_model_data(log_message)

        except Exception as e:
            logging.error("ImageProcessor: Failed to add model data", exc_info=False)
            errors.append(f"add_model_data: {e}")

        try:
            if errors: 
                db_status = False
            else:
                db_status = True
            self.log_entry.add_to_csv(log_message, db_status)
        except Exception as e:
            logging.error("ImageProcessor: Failed to add csv", exc_info=False)
            errors.append(f"add_to_csv: {e}")

        # Handle frontend string generation
        try:
            log_entry_string = self.log_entry.get_frontend_string(log_message)
        except Exception as e:
            errors.append(f"get_frontend_string: {e}")
            log_entry_string = "N/A"

        # Set final status
        if errors:
            success = False
            log_status = "ImageProcessor: Failed: " + "; ".join(errors)
            logging.error(log_status, exc_info=False)
        else:
            success = True
            log_status = "ImageProcessor: Logs saved to DB"
            logging.info(log_status, exc_info=False)

        return success, log_status



        
    