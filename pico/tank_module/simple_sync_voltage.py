import machine
import utime
import utime
import uio

ADC0_PIN_NUMBER = 26
ADC1_PIN_NUMBER = 27
DEFAULT_CAPTURE_PERIOD_S = 10
DEFAULT_EXPERIENCE_TIME_S = 30*60
DEFAULT_SAMPLES = 1000

class TankModule:
    def __init__(self):
        self.adc0 = machine.ADC(ADC0_PIN_NUMBER)
        self.adc1 = machine.ADC(ADC1_PIN_NUMBER)
        self.prev_mv0 = -1
        self.prev_mv1 = -1
        self.mv0 = None
        self.mv1 = None
        self.capture_period_s = DEFAULT_CAPTURE_PERIOD_S
        self.samples = DEFAULT_SAMPLES
        self.num_recorded = 0
        self.list0 = []
        self.list1 = []
        self.list_diff = []
        self.sync_report_timer = machine.Timer(-1)

    def adc0_micros(self):
        readings = []
        for _ in range(self.samples):
            # Read the raw ADC value (0-65535)
            readings.append(self.adc0.read_u16())
        voltages = list(map(lambda x: x * 3.3 / 65535, readings))
        return int(10**6 * sum(voltages) / self.samples)
    
    def adc1_micros(self):
        readings = []
        for _ in range(self.samples):
            # Read the raw ADC value (0-65535)
            readings.append(self.adc1.read_u16())
        voltages = list(map(lambda x: x * 3.3 / 65535, readings))
        return int(10**6 * sum(voltages) / self.samples)

    def sync_post_microvolts(self, timer):
        if self.num_recorded <= DEFAULT_EXPERIENCE_TIME_S / DEFAULT_CAPTURE_PERIOD_S:
            print('0', self.mv0/1000)
            print('1', self.mv1/1000)
            diff = (self.mv0-self.mv1)/1000
            diff = -diff if diff<0 else diff
            print('difference', diff)
            print('')
            self.list0.append(self.mv0/1000)
            self.list1.append(self.mv1/1000)
            self.list_diff.append(diff)
        if self.num_recorded == DEFAULT_EXPERIENCE_TIME_S / DEFAULT_CAPTURE_PERIOD_S:
            self.save_in_csv()
        self.num_recorded += 1

    def save_in_csv(self):
        with uio.open(f'mV_data_{utime.time()}.csv', 'w') as f:
            f.write('adc0,adc1,difference\n')
            for i in range(len(self.list0)):
                row = f"{self.list0[i]},{self.list1[i]},{self.list_diff[i]}\n"
                f.write(row)

    def start(self):
        # Start the synchronous reporting
        self.sync_report_timer.init(
            period=self.capture_period_s * 1000, 
            mode=machine.Timer.PERIODIC,
            callback=self.sync_post_microvolts)
        while self.num_recorded <= DEFAULT_EXPERIENCE_TIME_S / DEFAULT_CAPTURE_PERIOD_S:
            # Average of 1000 measurements
            self.mv0 = self.adc0_micros()
            self.mv1 = self.adc1_micros()
            utime.sleep_ms(100)

if __name__ == "__main__":
    t = TankModule()
    t.start()