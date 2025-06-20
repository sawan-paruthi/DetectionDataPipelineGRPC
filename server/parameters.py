import subprocess
import os
import psutil
import struct
import socket
import requests
from ipwhois import IPWhois
import ipaddress
import torch

class Parameters:
    def __init__(self):
        pass
 
    # Function to calculate image size in bits
    def get_image_size_in_bits(self, image_path):
        file_size_bytes = os.path.getsize(image_path)  # File size in bytes
        file_size_bits = file_size_bytes * 8  # Convert to bits (1 byte = 8 bits)
        return file_size_bits

    # Function to get real-time power consumption (for Nvidia GPUs)
    def get_power_usage_nvidia(self):
        try:
            # Execute nvidia-smi to get power consumption
            output = subprocess.check_output(['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'])
            power_watts = float(output.decode('utf-8').strip())
            return power_watts
        except Exception as e:
            print(f"Error fetching power consumption: {e}")
            return 0  # Return 0 if unable to fetch


    # Function to calculate energy required
    def calculate_energy(self, power_watts, process_time):
        return power_watts * process_time  # Energy in joules (watts * seconds)


    def calculate_latency(self, start_time, end_time):
        return end_time - start_time


    # Get local IP address and subnet mask
    def get_local_ip_info(self):
        net_info = psutil.net_if_addrs()

        for interface, addrs in net_info.items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    return addr.address, addr.netmask  # Return local IP and subnet mask
        return None, None


    # Calculate subnet address from local IP and subnet mask
    def calculate_subnet(self, ip, netmask):
        try:
            if ip == '127.0.0.1' or ip == 'localhost':
                return 'Not applicable'

            ip_binary = struct.unpack('!I', socket.inet_aton(ip))[0]
            mask_binary = struct.unpack('!I', socket.inet_aton(netmask))[0]
            subnet_binary = ip_binary & mask_binary
            subnet = socket.inet_ntoa(struct.pack('!I', subnet_binary))
            return subnet
        except Exception as e:
            print("Error calculating subnet address:", e)
            return None


    # Calculate CIDR notation from subnet mask
    def calculate_cidr(self, netmask):
        try:
            if netmask in ['Not available', 'Unknown Class or Invalid IP Address']:
                return 'Not available'  # Skip invalid netmask cases
            mask_binary = struct.unpack('!I', socket.inet_aton(netmask))[0]
            prefix_length = bin(mask_binary).count('1')  # Count the number of 1s in binary representation
            return prefix_length
        except Exception as e:
            print(f"Error calculating CIDR for netmask {netmask}: {e}")
            return 'Invalid'


    # Get public IP using an external service (ipify)
    def get_public_ip(self):
        try:     
            public_ip = requests.get('https://api.ipify.org').text
            return public_ip
        except Exception as e:
            print("Error getting public IP address:", e)
            return None
        

    # Get ISP and location details using ipinfo.io
    def get_ip_info(self, ip):
        try:
            if ip == '127.0.0.1' or ip == 'localhost':
                return 'Not applicable'
            response = requests.get(f"https://ipinfo.io/{ip}/json")
            data = response.json()
            return data
        except Exception as e:
            print("Error fetching IP information:", e)
            return None
        

    # Get ASN using ipwhois
    def get_asn_info(self, ip):
        try:
            if ip == '127.0.0.1' or ip == 'localhost':
                return 'Not applicable', 'Not applicable'
            obj = IPWhois(ip)
            results = obj.lookup_rdap()
            return results['asn'], results['asn_description']
        except Exception as e:
            print("Error fetching ASN information:", e)
            return None, None


    def get_default_netmask(self, ip):
        try:
            if ip == '127.0.0.1' or ip == 'localhost':
                return 'Not applicable'

            # Parse the IP address
            ip_obj = ipaddress.IPv4Address(ip)
            
            # Determine the class of the IP and return the default subnet mask
            first_octet = int(str(ip_obj).split('.')[0])

            if first_octet >= 1 and first_octet <= 126:
                return '255.0.0.0'  # Class A
            elif first_octet >= 128 and first_octet <= 191:
                return '255.255.0.0'  # Class B
            elif first_octet >= 192 and first_octet <= 223:
                return '255.255.255.0'  # Class C
            else:
                return 'Unknown Class or Invalid IP Address'
        except Exception as e:
            return str(e)
        
    
    def get_location_from_ip(self, ip_address):
        try:
            response = requests.get(f"http://ip-api.com/json/{ip_address}")
            data = response.json()
            if data['status'] == 'success':
                return {
                    'country': data['country'],
                    'region': data['regionName'],
                    'city': data['city']
                }
            else:
                return {"error": "Unable to retrieve location"}
        except Exception as e:
            return {"error": str(e)}
        

    def get_throughput(self,ot_time, img_path):
        file_size_bytes = os.path.getsize(img_path)

        file_size_mb = file_size_bytes / (1024 * 1024)
        if ot_time==0:
            return 'err process time is 0'
        return round((file_size_mb / (ot_time / 1000)) * 8, 4)    #throughput Mbps


    def get_device(self):
    # Check for any GPU backend
        if torch.cuda.is_available():  # NVIDIA GPUs
            return "cuda"
        elif torch.backends.mps.is_available():  # Apple Silicon GPUs
            return "mps"
        elif hasattr(torch.version, "hip") and torch.version.hip:  # AMD GPUs with ROCm
            return "rocm"
        else:
            return "cpu" 

