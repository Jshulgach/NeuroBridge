import pathlib

def parse_config_file(config_file):
    """ Helper function to parse config.yaml file"""
    # Dictionary to store the key-value pairs
    config_data = {}
    config_filepath = pathlib.Path(config_file)
    with open(config_filepath, 'r') as file:
        for line in file:
            # Strip whitespace and ignore empty lines or comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Split the line into key and value at the first '='
            key, value = line.split('=', 1)
            # Make sure to remove any '#' if they are in the line as comments
            value = value.split('#')[0]

            config_data[key.strip()] = value.strip()

    return config_data

