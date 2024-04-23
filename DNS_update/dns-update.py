import json
import logging
import os
import requests
import configparser
import pathlib
import dns.resolver
import time
import sys
import urllib3
# Disable urllib3 warnings
urllib3.disable_warnings()

# Configure logging
log_dir = "logs"
parent_dir = pathlib.Path(__file__).parent.resolve()
log_file_dir = os.path.join(parent_dir, log_dir)
if not os.path.exists(log_file_dir):
    os.mkdir(log_file_dir)

log_file_name = "dns-log.log"
log_file = os.path.join(log_file_dir, log_file_name)
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%b %d %H:%M:%S')

def read_config_file(file_path):
    config_data = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Split each line into key and value based on the delimiter
            key, value = line.strip().split(':', 1)  # Assuming ":" is the delimiter
            config_data[key.strip()] = value.strip()
    return config_data
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test.py <config_file>")
        exit(1)

    config_file = sys.argv[1]
    config_data = read_config_file(config_file)
    # Assign variables using config data
    host = config_data.get('Host')
    token = config_data.get('Token')
    account = config_data.get('Account')
    domain = config_data.get('Domain')
    dns_server = config_data.get('dns-server')

# Function to update DNS records in the zone file
def update_zone(dns_ip, pub_ip):
    logging.info(f"Updating DNS records from {dns_ip} to {pub_ip}")
    url = f'https://api.edgecast.com/v2/mcc/customers/{account}/dns/routezone'
    headers = {
        'Authorization': f'TOK:{token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    params = {
        'name': f'{domain}',
    }

    response = requests.get(url, params=params, headers=headers, verify=False)

    # Create a copy of the original zone
    orig_zone_path = 'orig_zone.json'
    with open(orig_zone_path, 'w') as f:
        json.dump(response.json(), f, indent=4)

    # Make the change from old IP to New
    zone = response.json()
    for record in zone['Records']['A']:
        if record['Rdata'] == dns_ip:
            record['Rdata'] = pub_ip

    # Export the updated new zone to a new JSON file
    new_zone_path = 'new_zone.json'
    with open(new_zone_path, 'w') as f:
        json.dump(zone, f, indent=4)

    # Upload the new updated file
    url = f"https://api.edgecast.com/v2/mcc/customers/{account}/dns/routezone"
    with open(new_zone_path, 'rb') as file:
        response = requests.put(url, headers=headers, data=file, verify=False)
        if response.status_code == 200:
            logging.info("File uploaded successfully.")
            return True
        else:
            logging.error(f"Failed to upload file. Status code: {response.status_code}")
            return False


# Get public IP function
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        else:
            return "Error: Unable to retrieve public IP address"
    except Exception as e:
        return f"Error: {e}"


public_ip = get_public_ip()

# DNS lookup function for target host
def get_dns_ip(hostname, dns_server):
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [dns_server]  # Set the DNS server
        response = resolver.resolve(hostname, 'A')
        return str(response[0])  # Assuming the first A record IP is the one we want
    except Exception as e:
        logging.error(f"Error resolving DNS for {hostname}: {e}")
        return None
dns_ip = get_dns_ip(host, dns_server)

# Compare to see if we have work to do
if public_ip == dns_ip:
    logging.info(f"IPs are the same for {host} No change required.")
    exit(0)
else:
    logging.info(f"IP Mismatch for {host}. Making change.")
    logging.info(f'Was {dns_ip}. Changing to {public_ip}')
    if update_zone(dns_ip, public_ip):
        logging.info("Verifying DNS change...")
        time.sleep(10)  # Add a delay if not long enough

        # add URL to fetch zone from API
        url = f'https://api.edgecast.com/v2/mcc/customers/{account}/dns/routezone'
        params = {
            'name': f'{domain}',
        }
        headers = {
            'Authorization': f'TOK:{token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Retrieve the updated DNS zone
        logging.info("Fetching updated DNS zone...")
        updated_zone_response = requests.get(url, params=params, headers=headers, verify=False)
        if updated_zone_response.status_code == 200:
            updated_zone = updated_zone_response.json()
            # Verify if the IP has been successfully updated in the zone
            for record in updated_zone['Records']['A']:
                if record['Rdata'] == public_ip:
                    logging.info("DNS change verified.")
                    break
            else:
                logging.error("DNS change not verified. IP not found in the updated zone.")
        else:
            logging.error("Failed to fetch updated DNS zone.")
    else:
        logging.error("DNS update failed. Skipping verification.")
if os.path.exists("new_zone.json"):
    os.remove("new_zone.json")
if os.path.exists("orig_zone.json"):
    os.remove("orig_zone.json")