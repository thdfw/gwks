import machine
import time
file_name = "res_5_5_take_1.csv"
header = "1000 readings with 10 kOhm voltage divider and 5.55 kOhm NTC stand-in\n"
# Define the ADC pin
adc0 = machine.ADC(26)

# Function to read the voltage from ADC0
def read_voltage():
    # Read the raw ADC value (0-65535)
    adc_value = adc0.read_u16()
    # Convert the raw value to a voltage
    # The reference voltage (Vref) is typically 3.3V on the Pico
    voltage = (adc_value / 65535) * 3.3
    return voltage


def test(samples=1000):
    readings = []
    for _ in range(samples):
        readings.append(adc0.read_u16())
    return readings

readings = test()

voltages = list(map(lambda x: x * 3.3 / 65535, readings))
# 1000 readings in 30 ms


# Save timestamps to a CSV file
with open(file_name, "w") as csvfile:
    csvfile.write(header)
    for volts in voltages:
        csvfile.write(f"{volts}\n")
print(f"Data saved to {file_name}")
read_voltage()
