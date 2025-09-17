# Differential PPM Decoder

An extension for Saleae Logic 2 to add a digital measurement for decoding a [differential poistion pulse modulated](https://www.pcbheaven.com/wikipages/Pulse_Position_Modulation/) (diff-ppm) signal.

This extension would be better implemented using the [Protocol Analyzer SDK](https://support.saleae.com/saleae-api-and-sdk/protocol-analyzer-sdk), but this is a quick implementation to decode short sequences.

## GUI Usage

Since [Digital Measurement Extension](https://support.saleae.com/extensions/measurement-extensions/digital-measurement-extensions) doesn't allow strings to be reported, getting the bits out is a bit tedious. See setting `OUT_FILE` in [Parameters](#parameters) to directly write the bits to a file.

This extension reports the following measurement values:

- ppm_packed_bit_value - An integer made up of the the decoded bits where the msb was the earliest and the lsb was the last.
- ppm_num_bits - The number of bits decoded. This can be used to determine if the leading bits in `ppm_packed_bit_value` were 0's.
- ppm_gap_threshold - The gap size between a pair of pulses that was used to determine if a bit was `1` or `0`.


These values can be copy/pasted from the Logic 2 GUI.

Ex.
```
ppm_packed_bit_value	8589806307
ppm_num_bits	33
ppm_gap_threshold	0.0011590378787877575	s
```

To get the bit values, convert `ppm_packed_bit_value` to binary. For example, `8589806307` is `0b111111111111111100000101011100011`.

Many tools can do this including most calculator apps:

![Convert integer to binary](docs\prog_calc.png)

**NOTE:** bits are decoded just based on the low time before a rising edge. This means that the measurement range needs to start during the first high pulse, and end during the last high pulse. Otherwise, the first or last bit may be incorrect.

![Measure PPM bits](docs\logic2_pic.png)

## Parameters

Since [Digital Measurement Extension](https://support.saleae.com/extensions/measurement-extensions/digital-measurement-extensions) doesn't allow parameters to be set, there are some paramaters that can be modified in [diff_ppm_decoder.py](diff_ppm_decoder.py) to change the extensions behavior.

### OUT_FILE
Set to a file path to write measurement results to file. If `None` don't write values to a file.

Writing to a file makes it much easier to collect data than copying from the GUI.

For example `'C:/Users/username/Documents/diff_ppm.txt'`.

### OUT_FORMAT

A string to set the format of the output file if `OUT_FILE` is set.

If OUT_FORMAT=="nibbles" format output like:
```
    1, 1, 1, 1,
    1, 1, 1, 1,
```

If OUT_FORMAT=="time_series" format output like:
```
  1758132435.572233,0
  1758132435.573173,0
  1758132435.575154,1
  1758132435.576092,0
  1758132435.578078,1
```

Otherwise format like:
`1, 1, 1, 1, 1, 1, 1, 1`

### MIN_GAP

Only consider pulses where the gap is greater than this many seconds.

### MAX_GAP

Only consider pulses where the gap is less than this many seconds.

### MIN_GAP_FOR_1

Hard code a pulse gap threshold for decoding values.
If the gap between pulses is greater than this value, decode a `1`. Otherwise decond a `0`.
If this is `None` use the median gap time as the threshold.

