from __future__ import absolute_import, division, print_function
import os
from ciscoconfparse import CiscoConfParse
from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException
from json_config import block_number_config
from dotenv import load_dotenv

load_dotenv()

USERNAME, PASSWORD, ENABLE_SECRET = os.getenv('user_name'), os.getenv('user_pass'), os.getenv('enable_secret')

def get_number():
    while True:
        phone_number = input("Enter number: ")
        if not phone_number.isdigit():
            print ("Enter only numbers\n")
            continue
        elif len(phone_number) != 10:
            print ("Enter 10 digits\n")
            continue
        elif int(phone_number[0]) <= 1:
            print ("Invalid Phone Number\n")
        else:
            break
    return phone_number

def update_routers():
    voice_gateways = block_number_config['voice_gateways']
    blocked_numbers = block_number_config['blocked_numbers']
    block_numbering = [*blocked_numbers]
    number_block = []
    for number in block_numbering:
        number_block.append([number, blocked_numbers[number]])
    for gateway in voice_gateways:
        existing_list = []
        try:
            net_connect = ConnectHandler(device_type='cisco_ios_ssh', ip=gateway, username=USERNAME, password=PASSWORD, secret=ENABLE_SECRET)
        except (NetMikoAuthenticationException):
            print(f"Invalid Credentials Entered for Voice Gateway {gateway}.")
        net_connect.enable()
        current_config = net_connect.send_command('show run | sec translation-rule 2')
        cisco_obj = CiscoConfParse(current_config.splitlines())
        match = cisco_obj.find_objects(r"voice translation-rule 2")[0].children
        i = 1
        for item in match:
            split_components = item.text.split('/')
            for split_piece in split_components:
                if split_piece.isnumeric() and len(split_piece) == 10:
                    existing_list.append([i, split_piece])




        while phone_number in current_config:
    print("Phone number is already being blocked")
    phone_number = get_number()

# Find the voice translation rule 2


# Match on last rule in the list


# Increment rule value by 1
new_value = int((last_rule.strip().split()[1]))
new_value += 1

# Create the new rule
new_rule = ("rule " + str(new_value) + " reject " + "/" + str(phone_number) + "/")
print("\nRule to be added: " + new_rule)

# Set devices as the CUBE routers for configuration
devices = open('cube.txt','r').read()
devices = devices.strip()
devices = devices.splitlines()

success = 0
failure = 0
unreachable = 0

print("Applying new rules to CUBE devices. \n")

for device in devices:
    try:
        with open('output.txt', 'a') as output_file:
            net_connect = ConnectHandler(device_type='cisco_ios_ssh', ip=device,
                                         username=USERNAME, password=PASSWORD)
            hostname = net_connect.find_prompt()
            print(hostname, file=output_file)
            net_connect.send_command('send log START - BLOCKING NUMBER ADDITION')
            config_commands = [ 'voice translation-rule 2',
                                new_rule]
            new_config = net_connect.send_config_set(config_commands)
            net_connect.send_command('send log COMPLETE - BLOCKING NUMBER ADDITION')
            print(hostname, new_config, file=output_file)
            print("Finished " + str(hostname))
            print("\n", file=output_file)
            print("\n")
            success += 1
    except:
        print ("Unable to reach device " + device)
        unreachable += 1

print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
print("Results")
print("Successful: " + str(success))
print("Failures: " + str(failure))
print("Unable to Reach: " + str(unreachable))
