from __future__ import absolute_import, division, print_function
import string
from ciscoconfparse import CiscoConfParse
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import NetMikoAuthenticationException
import sys

# my_config = """
#      ! Config from router
#      voice translation-rule 300
#       rule 1 reject /1235551111/
#       rule 2 reject /5551115555/
#      """

print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
print("Welcome!")
print("This script will update the voice translation-rule 300 on CUBE routers.")
print("CUBE routers are listed in CUBE.txt in the same directory.")
print("")

def get_input(prompt=''):
    try:
        line = raw_input(prompt)
    except NameError:
        line = input(prompt)
    return line

def get_credentials():
    """Prompt for and return a username and password."""
    USERNAME = get_input('Enter Username: ')
    PASSWORD = None
    while not PASSWORD:
        PASSWORD = getpass()
        password_verify = getpass('Retype your password: ')
        if PASSWORD != password_verify:
            print('Passwords do not match.  Try again.')
            PASSWORD = None
    return USERNAME, PASSWORD

USERNAME, PASSWORD = get_credentials()

# Get phone number from user
print("")
print("Enter a phone number that is 10 digits, including area code.")

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

phone_number = get_number()

#Gather configuration from golden router
#Update $GOLDENROUTER with an IP address of a CUBE router
print("Connecting to router")
try:
    net_connect = ConnectHandler(device_type='cisco_ios_ssh', ip='$GOLDENROUTER',
                                 username=USERNAME, password=PASSWORD)
except (NetMikoAuthenticationException):
    print("Invalid Credentials Entered, Try Again.")
    sys.exit()

hostname = net_connect.find_prompt()
print("Getting baseline configuration from: " + str(hostname) + "\n")
net_connect.send_command('send log SCRIPT IS GETTING PRE-CHANGE TRANSLATION-RULE 300 LIST')
current_config = net_connect.send_command('show run | sec translation-rule 300')
print(current_config)
# Check if the numbered entered is already being blocked
while phone_number in current_config:
    print("Phone number is already being blocked")
    phone_number = get_number()

# Parse the lines returned by the router
cisco_obj = CiscoConfParse(current_config.splitlines())
# Find the voice translation rule 300
match = cisco_obj.find_objects(r"voice translation-rule 300")
match = match[0]
match.children
# Match on last rule in the list
last_rule = match.children[-1]
last_rule = last_rule.text

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
            config_commands = [ 'voice translation-rule 300',
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
