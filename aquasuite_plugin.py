from multiprocessing import shared_memory
import xml.etree.ElementTree as ET
import re

# Attach to an existing shared memory block
def get_sensors_data_aquasuite():
    shm = shared_memory.SharedMemory(name='highflowNEXT')

    # Read the data from shared memory
    data = bytes(shm.buf).decode('utf-8', errors='replace')  # Use 'replace' to handle any potential encoding issues

    # Clean up any non-XML characters, if necessary
    cleaned_data = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]', '', data)  # Strip out non-XML compliant characters

    # Try parsing the cleaned data
    try:
        root = ET.fromstring(cleaned_data)  # Parse the XML data
        # Find the <value> element within the XML
        value_element = root.find('.//value')

        # Check if the <value> element was found and print its content
        if value_element is not None:
            value = value_element.text
            return value
    except ET.ParseError as e:
        print(f"ParseError after cleaning data: {e}")
    finally:
        # Clean up the shared memory
        shm.close()
        shm.unlink()
    return None
