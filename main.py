import socket
import requests
import time
import os

TARGET_DOMAIN = 'alpergokcan.net'
DOMAIN_NAME = "alper.cerwin.dev"
API_KEY = os.environ['CLOUDFLARE_API_KEY']
ZONE_ID = os.environ['CLOUDFLARE_ZONE_ID']
SLEEP_DURATION = 120 #in seconds.
                            
def get_ip_address(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except socket.gaierror:
        return None

def set_cloudflare_dns_record(api_key,zone_id, domain_name, ip_address):
    api_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": domain_name,
        "content": ip_address
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            print("DNS record updated successfully.")
        else:
            pass
            #print(f"Failed to update DNS record. Status code: {response.status_code}, Message: {response.json()['errors'][0]['message']}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def get_cloudflare_dns_record(api_key, zone_id, domain_name):
    api_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={domain_name}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                records = data["result"]
                if len(records) > 0:
                    dns_record = records[0]
                    return dns_record['content']
                else:
                    print(f"No 'A' DNS record found for {domain_name}.")
            else:
                print(f"Failed to fetch DNS record. Errors: {data['errors']}")
        else:
            print(f"Failed to fetch DNS record. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    
    return None

def main():
    ip_address = get_cloudflare_dns_record(API_KEY, ZONE_ID, DOMAIN_NAME)
    while True:
        current_ip_address = get_ip_address(domain=TARGET_DOMAIN)
        if current_ip_address != ip_address:
            print("IP Address change detected!")
            print(f'{ip_address} -> {current_ip_address}')
            ip_address = current_ip_address
            set_cloudflare_dns_record(API_KEY, ZONE_ID, DOMAIN_NAME, ip_address)
        time.sleep(SLEEP_DURATION)

if __name__ == "__main__":
    main()
    