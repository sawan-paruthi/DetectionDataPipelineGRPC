import os
import csv
import json
from dotenv import load_dotenv
import requests
from parameters import Parameters
from ipwhois import IPWhois
import logging

load_dotenv()

LOG_FILE = os.getenv("LOG_FILE")
DB_URL = os.getenv("DB_URL") 


class LogEntry:
    def __init__(self, service_name, server_id):
        self.parameters = Parameters()
        self.task_name = service_name
        self.server_id = server_id

    def add_to_csv(self, log_message, db_status):
        log_entry_csv = {
            'message':log_message.message,
            'success':log_message.success,
            'server_id': self.server_id,
            'db_status': "Success" if db_status else "failed",
            'task_name':self.task_name,
            'service_name': log_message.service_name,
            'ip_address': log_message.ip_address,
            'location': self.parameters.get_location_from_ip(log_message.ip_address),
            'grpc_response_time': round(log_message.grpc_response_time,4),
            'grpc_system_latency': round(log_message.grpc_response_time - log_message.process_time, 4),
            'total_response_time': round(log_message.total_response_time,4),
            'total_latency': round(log_message.total_response_time - log_message.process_time, 4),
            'throughput': round(log_message.throughput,4),
            'power': log_message.power
        }
        # Check if the file already exists
        file_exists = os.path.isfile(LOG_FILE)
        # Define fieldnames to maintain the column order
        fieldnames = [
            'task_name','service_name', 'message', 'success', 'server_id', 'db_status', 'ip_address', 'location', 
            'grpc_response_time', 'grpc_system_latency', 
            'total_response_time', 'total_latency', 'throughput', 'power'
        ]
        # Open the CSV file in append mode
        try:
            with open(LOG_FILE, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                # Write header only if file does not exist
                if not file_exists:
                    writer.writeheader()
                # Write the log entry as a new row
                writer.writerow(log_entry_csv)
        except:
            raise FileNotFoundError


    def get_frontend_string(self, log_message):
        log_entry_frontend = {
            'service_name': log_message.service_name,
            'ip_address': log_message.ip_address,
            'location': self.parameters.get_location_from_ip(log_message.ip_address),
            'grpc_response_time': str(round(log_message.grpc_response_time,2)) + " ms",  # Convert to string
            'grpc_system_latency': str(round(log_message.grpc_response_time - log_message.process_time, 2)) + " ms",  # Convert to string
            'total_response_time': str(round(log_message.total_response_time,2)) + " ms",  # Convert to string
            'total_latency': str(round(log_message.total_response_time - log_message.process_time, 2)) + " ms",  # Convert to string
            'throughput': str(round(log_message.throughput,2)) + " Mbps"  # Convert to string
        }
        log_entry_string = json.dumps(log_entry_frontend, indent=4)

        return log_entry_string
    


    def add_user_data(self, log_message):
        try:
            ip_address = log_message.ip_address

            # Default values
            subnet = 'Not available'
            netmask = 'Not available'
            city, region, country = 'Not available', 'Not available', 'Not available'
            longitude, latitude = 0.0, 0.0
            asn, asn_description = 'Not available', 'Not available'

            if ip_address == '127.0.0.1' or ip_address == 'localhost':
                pass
            else:
                netmask = self.parameters.get_default_netmask(ip_address)
                if netmask != 'Unknown Class or Invalid IP Address':
                    subnet = f"{self.parameters.calculate_subnet(ip_address, netmask)}/{self.parameters.calculate_cidr(netmask)}"
                else:
                    print(f"Invalid netmask: {netmask}")
                    netmask = 'Not available'
                    subnet = 'Not available'

                # Get ASN info
                asn, asn_description = self.parameters.get_asn_info(ip_address)

                # Get IP info
                ip_info = self.parameters.get_ip_info(ip_address)
                if isinstance(ip_info, dict):
                    location = ip_info.get('loc', '0.0,0.0')
                    try:
                        latitude, longitude = map(float, location.split(','))
                    except ValueError:
                        print(f"Invalid location format: {location}")
                        latitude, longitude = 0.0, 0.0

                    city = ip_info.get('city', 'Not available')
                    region = ip_info.get('region', 'Not available')
                    country = ip_info.get('country', 'Not available')
                else:
                    print("Could not retrieve public IP information.")

            # Prepare user data dict
            user_data = {
                'ip_address': ip_address,
                'latitude': latitude,
                'longitude': longitude,
                'city': city,
                'region': region,
                'country': country,
                'asn': asn,
                'asn_description': asn_description,
                'subnet_mask': netmask,
                'subnet': subnet
            }

        # Check if user data already exists in the central Flask app
        
            response = requests.post(f'{DB_URL}/add_userdata', json=user_data)
            res_json = response.json()
            logging.info(f"LogEntry: User Data API Response {response.status_code}")
            if response.status_code == 200:
                error = res_json.get("message")
                logging.info(f"LogEntry: User not Added: {error}")
            else:
                logging.info(f"LogEntry: Response Content: {res_json}")
                if response.status_code != 201:
                    logging.error(f"LogEntry: Failed to save user data. Response: {res_json}", exc_info=False)
                    raise requests.exceptions.HTTPError(res_json.get("message"))
                
        except requests.RequestException as e:
            raise ConnectionError(f"HTTP request failed, User Data not saved to DB: {e}")

        except Exception as e:
            raise RuntimeError(f"LogEntry: error in add_user_data: {e}")

         
    def add_model_data(self, log_messages):
        try:
            model_result = {
                    'ip_address': log_messages.ip_address,
                    'status': log_messages.success,
                    'message': log_messages.message,
                    'model_name': log_messages.service_name,
                    'server_id': self.server_id,
                    'service_type': self.task_name,
                    'latency_time': round(log_messages.total_response_time - log_messages.process_time, 4),
                    'cpu_usage': round(log_messages.cpu_utilized, 2),
                    'memory_usage': round(log_messages.memory_utilized, 2),
                    'throughput': round(log_messages.throughput,2),
                    'energy_required': round(log_messages.power*log_messages.process_time,4),
                    'power_watts': round(log_messages.power, 2),
                    'response_time': round(log_messages.total_response_time,2)
                }

            # Send POST request to add model result
        
            response = requests.post(f'{DB_URL}/modelresult', json=model_result)
            logging.info(f"LogEntry: Model Data API Response Status: {response.status_code}")
            resjson = response.json()
            if response.status_code != 201:
                logging.error("LogEntry: Server Error: 500", exc_info=False)
                raise requests.exceptions.HTTPError(resjson.get("message"))
            else:
                logging.info("LogEntry: Model Data Added")
        
        except Exception as e:
            raise RuntimeError(f"LogEntry: error in add_model_data: {e}")

    
    




 



