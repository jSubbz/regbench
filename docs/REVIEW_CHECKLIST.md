# Item review checklist

Review record for the item set. An item that cannot be explained on the spot
gets fixed or cut, not kept because the answer happens to be right.

Four checks per family:

- **Correct** - the answer is right and the rationale is why.
- **Unambiguous** - no other reading gives a different defensible answer.
- **Rename holds** - the rewrite changes nothing that affects the answer.
- **Renumber holds** - new inputs, recomputed correctly, same structure.

`tools/verify_answers.py` covers arithmetic and transcription on items with a
check block. It cannot judge whether a formula is the right formula or whether a
question is ambiguous. Families marked **manual** have no recomputed answer key,
so their answers rest on this review.

Tick the boxes under each family, then rerun `tools/build_checklist.py` to update
the summary table. Ticks survive regeneration; `--reset` clears them.

**3 of 20 families reviewed.**

| Family | Domain | Check | Correct | Unambiguous | Rename | Renumber |
| --- | --- | --- | :-: | :-: | :-: | :-: |
| [`i2c-addr`](#i2c-addr) | i2c | auto |  |  |  |  |
| [`i2c-strap`](#i2c-strap) | i2c | auto |  |  |  |  |
| [`spi-mode`](#spi-mode) | spi | auto |  |  |  |  |
| [`spi-clock`](#spi-clock) | spi | auto |  |  |  |  |
| [`uart-frame`](#uart-frame) | uart | auto |  |  |  |  |
| [`uart-baud`](#uart-baud) | uart | auto |  |  |  |  |
| [`adc-code-to-voltage`](#adc-code-to-voltage) | adc | auto |  |  |  |  |
| [`adc-lsb`](#adc-lsb) | adc | auto |  |  |  |  |
| [`adc-voltage-to-code`](#adc-voltage-to-code) | adc | auto |  |  |  |  |
| [`pwm-ontime`](#pwm-ontime) | pwm | auto |  |  |  |  |
| [`pwm-freq`](#pwm-freq) | pwm | auto |  |  |  |  |
| [`pwm-resolution`](#pwm-resolution) | pwm | auto |  |  |  |  |
| [`gpio-rmw`](#gpio-rmw) | gpio | auto |  |  |  |  |
| [`gpio-pullup`](#gpio-pullup) | gpio | auto |  |  |  |  |
| [`field-extract`](#field-extract) | registers | auto |  |  |  |  |
| [`rtos-preempt`](#rtos-preempt) | rtos | **manual** | ✓ | ✓ | ✓ | ✓ |
| [`rtos-utilization`](#rtos-utilization) | rtos | auto |  |  |  |  |
| [`rtos-rm-bound`](#rtos-rm-bound) | rtos | auto |  |  |  |  |
| [`qnx-ipc`](#qnx-ipc) | rtos | **manual** | ✓ | ✓ | ✓ | ✓ |
| [`timer-tick`](#timer-tick) | timers | auto | ✓ | ✓ | ✓ | ✓ |

## Families

### i2c-addr
i2c, easy, auto

> A temperature sensor sits on an I2C bus at 7-bit slave address 0x48. The master begins a write transaction to it. What single byte appears on SDA during the address phase? Give the answer in hexadecimal.

Answer `0x90`. The 7-bit address is shifted left one place and the R/W bit occupies bit 0. A write sets R/W to 0, so the byte is (0x48 << 1) | 0 = 0x90.

Renumber answer `0x3B`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### i2c-strap
i2c, easy, auto

> An EEPROM has a fixed base 7-bit address of 0b1010000. Its two address pins A1 and A0 replace the two least significant bits of that address. A1 is tied high and A0 is tied to ground. What is the resulting 7-bit slave address? Give the answer in hexadecimal.

Answer `0x52`. 0b1010000 is 0x50. The strap pins contribute 0b10, giving 0x52.

Renumber answer `0x4E`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### spi-mode
spi, easy, auto

> An SPI master is configured with CPOL = 1 and CPHA = 0. Which SPI mode number does this correspond to? Give the mode number as an integer.

Answer `2`. The mode number is (CPOL << 1) | CPHA, so CPOL=1, CPHA=0 is mode 2.

Renumber answer `3`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### spi-clock
spi, easy, auto

> An SPI peripheral is clocked from a 48 MHz peripheral clock and its baud rate prescaler is set to divide by 16. What is the resulting SCLK frequency? Give the answer in MHz.

Answer `3` MHz. 48 MHz divided by 16 is 3 MHz.

Renumber answer `1.25`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### uart-frame
uart, medium, auto

> A UART is configured for 8 data bits, no parity, 1 start bit and 1 stop bit, running at 115200 baud. How long does it take to transmit 64 bytes back to back? Give the answer in milliseconds.

Answer `5.5556` ms. Each frame carries 1 start + 8 data + 1 stop = 10 bit times. 64 frames is 640 bit times, and 640 / 115200 = 5.5556 ms.

Renumber answer `36.667`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### uart-baud
uart, medium, auto

> A UART derives its bit clock from a 16 MHz peripheral clock using 16x oversampling and an integer baud rate divisor of 26. What actual baud rate does this produce? Give the answer in Hz.

Answer `38461.5` Hz. The baud rate is fclk / (oversampling x divisor) = 16e6 / (16 x 26) = 38461.5 baud.

Renumber answer `76923.1`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### adc-code-to-voltage
adc, easy, auto

> A 12-bit single-ended ADC uses a 3.3 V reference and returns the code 2048. Use the convention V = code x Vref / 2^N. What input voltage does this represent? Give the answer in volts.

Answer `1.65` V. 2048 x 3.3 / 4096 = 1.65 V.

Renumber answer `3.75`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### adc-lsb
adc, easy, auto

> A 12-bit ADC uses a 3.3 V reference. Use the convention V = code x Vref / 2^N. What voltage does one LSB represent? Give the answer in millivolts.

Answer `0.80566` mV. One LSB is Vref / 2^N = 3.3 / 4096 = 0.80566 mV.

Renumber answer `0.038147`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### adc-voltage-to-code
adc, medium, auto

> A 12-bit single-ended ADC uses a 3.3 V reference and truncates rather than rounds. Use the convention V = code x Vref / 2^N. What code does an input of 1.0 V produce? Give the answer as a decimal integer.

Answer `1241`. 1.0 x 4096 / 3.3 = 1241.2, and truncation gives 1241.

Renumber answer `368`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### pwm-ontime
pwm, easy, auto

> A PWM output runs at 20 kHz with a duty cycle of 35 percent. How long is the output high during each period? Give the answer in microseconds.

Answer `17.5` us. The period is 1 / 20 kHz = 50 us, and 35 percent of 50 us is 17.5 us.

Renumber answer `320`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### pwm-freq
pwm, medium, auto

> A timer is clocked from an 80 MHz source through a prescaler that divides by 8. The counter runs from 0 to TOP inclusive with TOP = 999, so one PWM period spans TOP + 1 counter ticks. What is the PWM output frequency? Give the answer in kHz.

Answer `10` kHz. 80 MHz / 8 = 10 MHz counter clock, and 10 MHz / 1000 ticks = 10 kHz.

Renumber answer `4`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### pwm-resolution
pwm, easy, auto

> A PWM timer counts from 0 to TOP inclusive with TOP = 1023, giving TOP + 1 distinct compare positions in each period. How many bits of duty cycle resolution does this provide? Give the answer as a decimal integer.

Answer `10`. TOP + 1 = 1024 distinct steps, and log2(1024) = 10 bits.

Renumber answer `8`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### gpio-rmw
gpio, medium, auto

> An 8-bit output register PORTA currently holds 0b10101100. Firmware must set bit 1 and clear bit 3 while leaving every other bit unchanged, where bit 0 is the least significant bit. What value does PORTA hold afterwards? Give the answer in hexadecimal.

Answer `0xA6`. 0b10101100 is 0xAC. Setting bit 1 gives 0b10101110, and clearing bit 3 gives 0b10100110, which is 0xA6.

Renumber answer `0x4B`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### gpio-pullup
gpio, easy, auto

> An input pin is held up by a 10 kilohm pull-up resistor connected to a 3.3 V rail. A switch pulls the pin to ground, closing the circuit. Ignoring pin leakage current, how much current flows through the pull-up resistor? Give the answer in milliamps.

Answer `0.33` mA. The full rail voltage appears across the resistor, so I = 3.3 V / 10 kilohm = 0.33 mA.

Renumber answer `1.0638`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### field-extract
registers, medium, auto

> A 32-bit peripheral register reads back as 0xDEADBEEF. One of its fields occupies bits 12 down to 7 inclusive, where bit 0 is the least significant bit. What is the value of that field? Give the answer in hexadecimal.

Answer `0x3D`. Shifting right by 7 and masking six bits isolates the field: (0xDEADBEEF >> 7) & 0x3F = 0x3D.

Renumber answer `0x45`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### rtos-preempt
rtos, easy, **manual**

> A preemptive fixed-priority scheduler is running, where a larger priority number means higher priority. Task A has priority 10 and is currently executing. Task B, priority 20, becomes ready at the same instant that Task C, priority 5, becomes ready. Which task executes next? Answer with the task name only.

Answer `Task B`. Task B has the highest priority of the three, so a preemptive scheduler preempts Task A and runs Task B.

Renumber answer `Task A`.

- [x] Correct
- [x] Unambiguous
- [x] Rename holds
- [x] Renumber holds

### rtos-utilization
rtos, medium, auto

> Three independent periodic tasks are scheduled on one processor. Their worst-case execution times and periods in milliseconds are (1, 4), (2, 8) and (1, 16). What is the total processor utilization? Give the answer as a percentage.

Answer `56.25` %. Utilization is the sum of C/T: 1/4 + 2/8 + 1/16 = 0.5625, or 56.25 percent.

Renumber answer `60`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### rtos-rm-bound
rtos, medium, auto

> Rate-monotonic scheduling has a sufficient schedulability bound of n(2^(1/n) - 1) for n independent periodic tasks. What is that bound for 3 tasks? Give the answer as a percentage.

Answer `77.976` %. 3 x (2^(1/3) - 1) = 3 x 0.259921 = 0.779763, or 77.976 percent.

Renumber answer `74.349`.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### qnx-ipc
rtos, medium, **manual**

> A QNX Neutrino client thread calls MsgSend() to a server thread that has not yet called MsgReceive(). What blocking state does the client enter? Answer with the state name only.

Answer `SEND-blocked`. Until the server calls MsgReceive() the message has not been taken, so the client waits in the SEND-blocked state.

Renumber answer `REPLY-blocked`.

- [x] Correct
- [x] Unambiguous
- [x] Rename holds
- [x] Renumber holds

### timer-tick
timers, medium, auto

> A timer is clocked from a 16 MHz source through a prescaler that divides by 64. The counter runs from 0 to TOP inclusive with TOP = 249 and raises an interrupt each time it wraps, so one interrupt period spans TOP + 1 counter ticks. What is the interrupt rate? Give the answer in Hz.

Answer `1000` Hz. 16 MHz / 64 = 250 kHz counter clock, and 250 kHz / 250 ticks = 1000 Hz.

Renumber answer `250`.

- [x] Correct
- [x] Unambiguous
- [x] Rename holds
- [x] Renumber holds
