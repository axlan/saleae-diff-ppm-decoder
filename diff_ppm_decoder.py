from saleae.range_measurements import DigitalMeasurer

# Set to a file path to write measurement results to file. If `None` don't write values to a file.
# OUT_FILE = 'C:/Users/username/Documents/diff_ppm.txt'
OUT_FILE = None

# If OUT_FORMAT==nibbles format output like:
#    1, 1, 1, 1,
#    1, 1, 1, 1,
# If OUT_FORMAT==time_series format output like:
#  1758132435.572233,0
#  1758132435.573173,0
#  1758132435.575154,1
#  1758132435.576092,0
#  1758132435.578078,1
# Otherwise format like:
#  1, 1, 1, 1, 1, 1, 1, 1
OUT_FORMAT = 'nibbles'

# Only consider pulses where the gap is greater than this many seconds.
MIN_GAP = 0

# Only consider pulses where the gap is less than this many seconds.
MAX_GAP = 1

# Hard code a pulse gap threshold for decoding values.
# If the gap between pulses is greater than this value, decode a `1`. Otherwise decond a `0`.
# If this is `None` use the average of the largest and smallest gap times as the threshold.
MIN_GAP_FOR_1 = None

class DiffPPMDecoder(DigitalMeasurer):
    supported_measurements = []

    # Initialize your measurement extension here
    # Each measurement object will only be used once, so feel free to do all per-measurement initialization here
    def __init__(self, requested_measurements):
        super().__init__(requested_measurements)
        self.gap_times = []
        self.gap_durations = []
        self.last_time = None

    # This method will be called one or more times per measurement with batches of data
    # data has the following interface
    #   * Iterate over to get transitions in the form of pairs of `Time`, Bitstate (`True` for high, `False` for low)
    # `Time` currently only allows taking a difference with another `Time`, to produce a `float` number of seconds
    def process_data(self, data):
        for t, bitstate in data:
            if bitstate and self.last_time:
                elapsed = float(t - self.last_time)
                if elapsed < MIN_GAP or elapsed > MAX_GAP:
                    continue

                self.gap_times.append(t.as_datetime().timestamp())
                self.gap_durations.append(elapsed)

            self.last_time = t

    # This method is called after all the relevant data has been passed to `process_data`
    # It returns a dictionary of the request_measurements values
    def measure(self):

        if MIN_GAP_FOR_1 is not None:
            gap_threshold = MIN_GAP_FOR_1
        elif len(self.gap_durations) > 0:
            gap_threshold = (max(self.gap_durations) + min(self.gap_durations)) / 2.0
        else:
            gap_threshold = 0

        bits = [ 1 if gap > gap_threshold else 0 for gap in self.gap_durations ]


        bit_vals = 0
        for i, bit in enumerate(bits):
            bit_vals |= (bit << (len(bits) - i - 1))

        if OUT_FILE:
            with open(OUT_FILE, 'w') as fd:
                if OUT_FORMAT == 'time_series':
                    for i in range(len(bits)):
                        fd.write(f'{self.gap_times[i]},{bits[i]}\n')
                elif OUT_FORMAT == 'nibles':
                    for offset in range(0,len(self.bits), 4):
                        fd.write('    ' + ' '.join(str(b) + ',' for b in self.bits[offset:offset+4]) + '\n')
                else:
                    fd.write(', '.join(str(b) for b in self.bits))

        return {'num_bits': len(bits),'bit_vals': bit_vals, 'gap_threshold': gap_threshold}
