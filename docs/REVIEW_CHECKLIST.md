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

Each family below shows all three variants with their answers, so every check can
be made from this file alone.

- **Correct**: does the stated reasoning produce the base answer?
- **Unambiguous**: could another reading give a different defensible answer? Is
  every convention that could differ stated in the question?
- **Rename holds**: read the rename against the base. Same question underneath?
  (The answers are asserted identical by the test suite, so what you are judging
  is whether the rewrite changed what is being asked.)
- **Renumber holds**: same structure, new inputs, answer recomputed correctly?

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

**base** -> `0x90`

> A temperature sensor sits on an I2C bus at 7-bit slave address 0x48. The master begins a write transaction to it. What single byte appears on SDA during the address phase? Give the answer in hexadecimal.

**rename** -> `0x90`

> An ambient light sensor is addressed on a two-wire bus using 7-bit slave address 0x48. A controller starts a write to it. Which single byte is driven on the data line during the addressing phase? Give the answer in hexadecimal.

**renumber** -> `0x3B`

> A pressure sensor sits on an I2C bus at 7-bit slave address 0x1D. The master begins a read transaction from it. What single byte appears on SDA during the address phase? Give the answer in hexadecimal.

Why `0x90`: The 7-bit address is shifted left one place and the R/W bit occupies bit 0. A write sets R/W to 0, so the byte is (0x48 << 1) | 0 = 0x90.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### i2c-strap
i2c, easy, auto

**base** -> `0x52`

> An EEPROM has a fixed base 7-bit address of 0b1010000. Its two address pins A1 and A0 replace the two least significant bits of that address. A1 is tied high and A0 is tied to ground. What is the resulting 7-bit slave address? Give the answer in hexadecimal.

**rename** -> `0x52`

> A real-time clock chip has a fixed base 7-bit address of 0b1010000. Two hardware-strap inputs, AD1 and AD0, occupy the two least significant bits of that address. AD1 is strapped to VCC and AD0 is strapped to VSS. What is the resulting 7-bit slave address? Give the answer in hexadecimal.

**renumber** -> `0x4E`

> An I/O expander has a fixed base 7-bit address of 0b1001000. Its three address pins A2, A1 and A0 replace the three least significant bits of that address. A2 is tied high, A1 is tied high and A0 is tied to ground. What is the resulting 7-bit slave address? Give the answer in hexadecimal.

Why `0x52`: 0b1010000 is 0x50. The strap pins contribute 0b10, giving 0x52.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### spi-mode
spi, easy, auto

**base** -> `2`

> An SPI master is configured with CPOL = 1 and CPHA = 0. Which SPI mode number does this correspond to? Give the mode number as an integer.

**rename** -> `2`

> An SPI master idles its clock line high and captures each incoming data bit on the first of the two clock edges in that bit's period, rather than the second. Which SPI mode number does this correspond to? Give the mode number as an integer.

**renumber** -> `3`

> An SPI master is configured with CPOL = 1 and CPHA = 1. Which SPI mode number does this correspond to? Give the mode number as an integer.

Why `2`: The mode number is (CPOL << 1) | CPHA, so CPOL=1, CPHA=0 is mode 2.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### spi-clock
spi, easy, auto

**base** -> `3` MHz

> An SPI peripheral is clocked from a 48 MHz peripheral clock and its baud rate prescaler is set to divide by 16. What is the resulting SCLK frequency? Give the answer in MHz.

**rename** -> `3` MHz

> A serial peripheral interface block runs from a 48 MHz bus clock, and its clock divider is configured for a division factor of 16. What is the resulting serial clock frequency? Give the answer in MHz.

**renumber** -> `1.25` MHz

> An SPI peripheral is clocked from an 80 MHz peripheral clock and its baud rate prescaler is set to divide by 64. What is the resulting SCLK frequency? Give the answer in MHz.

Why `3` MHz: 48 MHz divided by 16 is 3 MHz.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### uart-frame
uart, medium, auto

**base** -> `5.5556` ms

> A UART is configured for 8 data bits, no parity, 1 start bit and 1 stop bit, running at 115200 baud. How long does it take to transmit 64 bytes back to back? Give the answer in milliseconds.

**rename** -> `5.5556` ms

> An asynchronous serial port sends 8-bit characters with no parity, framed by one start bit and one stop bit, at a line rate of 115200 baud. How long does a back-to-back burst of 64 characters occupy the line? Give the answer in milliseconds.

**renumber** -> `36.667` ms

> A UART is configured for 8 data bits, no parity, 1 start bit and 2 stop bits, running at 9600 baud. How long does it take to transmit 32 bytes back to back? Give the answer in milliseconds.

Why `5.5556` ms: Each frame carries 1 start + 8 data + 1 stop = 10 bit times. 64 frames is 640 bit times, and 640 / 115200 = 5.5556 ms.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### uart-baud
uart, medium, auto

**base** -> `38461.5` Hz

> A UART derives its bit clock from a 16 MHz peripheral clock using 16x oversampling and an integer baud rate divisor of 26. What actual baud rate does this produce? Give the answer in Hz.

**rename** -> `38461.5` Hz

> A serial port generates its bit clock from a 16 MHz module clock. The receiver samples each bit 16 times, and the integer prescale register holds the value 26. What actual line rate does this produce? Give the answer in Hz.

**renumber** -> `76923.1` Hz

> A UART derives its bit clock from a 24 MHz peripheral clock using 8x oversampling and an integer baud rate divisor of 39. What actual baud rate does this produce? Give the answer in Hz.

Why `38461.5` Hz: The baud rate is fclk / (oversampling x divisor) = 16e6 / (16 x 26) = 38461.5 baud.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### adc-code-to-voltage
adc, easy, auto

**base** -> `1.65` V

> A 12-bit single-ended ADC uses a 3.3 V reference and returns the code 2048. Use the convention V = code x Vref / 2^N. What input voltage does this represent? Give the answer in volts.

**rename** -> `1.65` V

> A 12-bit successive-approximation converter operating single-ended from a 3.3 V full-scale reference reports a conversion result of 2048. Use the convention V = code x Vref / 2^N. What input voltage does this represent? Give the answer in volts.

**renumber** -> `3.75` V

> A 10-bit single-ended ADC uses a 5.0 V reference and returns the code 768. Use the convention V = code x Vref / 2^N. What input voltage does this represent? Give the answer in volts.

Why `1.65` V: 2048 x 3.3 / 4096 = 1.65 V.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### adc-lsb
adc, easy, auto

**base** -> `0.80566` mV

> A 12-bit ADC uses a 3.3 V reference. Use the convention V = code x Vref / 2^N. What voltage does one LSB represent? Give the answer in millivolts.

**rename** -> `0.80566` mV

> A 12-bit analogue-to-digital converter is referenced to a 3.3 V full-scale input. Use the convention V = code x Vref / 2^N. What is the step size of a single count? Give the answer in millivolts.

**renumber** -> `0.038147` mV

> A 16-bit ADC uses a 2.5 V reference. Use the convention V = code x Vref / 2^N. What voltage does one LSB represent? Give the answer in millivolts.

Why `0.80566` mV: One LSB is Vref / 2^N = 3.3 / 4096 = 0.80566 mV.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### adc-voltage-to-code
adc, medium, auto

**base** -> `1241`

> A 12-bit single-ended ADC uses a 3.3 V reference and truncates rather than rounds. Use the convention V = code x Vref / 2^N. What code does an input of 1.0 V produce? Give the answer as a decimal integer.

**rename** -> `1241`

> A 12-bit converter running single-ended from a 3.3 V reference discards the fractional part of the conversion result rather than rounding it. Use the convention V = code x Vref / 2^N. Which count results from an applied input of 1.0 V? Give the answer as a decimal integer.

**renumber** -> `368`

> A 10-bit single-ended ADC uses a 5.0 V reference and truncates rather than rounds. Use the convention V = code x Vref / 2^N. What code does an input of 1.8 V produce? Give the answer as a decimal integer.

Why `1241`: 1.0 x 4096 / 3.3 = 1241.2, and truncation gives 1241.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### pwm-ontime
pwm, easy, auto

**base** -> `17.5` us

> A PWM output runs at 20 kHz with a duty cycle of 35 percent. How long is the output high during each period? Give the answer in microseconds.

**rename** -> `17.5` us

> A motor drive signal is switched at 20 kHz and spends 35 percent of each switching cycle in the on state. What is the on-time per cycle? Give the answer in microseconds.

**renumber** -> `320` us

> A PWM output runs at 2.5 kHz with a duty cycle of 80 percent. How long is the output high during each period? Give the answer in microseconds.

Why `17.5` us: The period is 1 / 20 kHz = 50 us, and 35 percent of 50 us is 17.5 us.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### pwm-freq
pwm, medium, auto

**base** -> `10` kHz

> A timer is clocked from an 80 MHz source through a prescaler that divides by 8. The counter runs from 0 to TOP inclusive with TOP = 999, so one PWM period spans TOP + 1 counter ticks. What is the PWM output frequency? Give the answer in kHz.

**rename** -> `10` kHz

> A capture/compare unit is fed from an 80 MHz module clock via a clock divider set to a division factor of 8. Its counter wraps from 0 through the period register value 999 inclusive, so one output cycle takes 999 + 1 counter increments. What is the output frequency? Give the answer in kHz.

**renumber** -> `4` kHz

> A timer is clocked from a 48 MHz source through a prescaler that divides by 16. The counter runs from 0 to TOP inclusive with TOP = 749, so one PWM period spans TOP + 1 counter ticks. What is the PWM output frequency? Give the answer in kHz.

Why `10` kHz: 80 MHz / 8 = 10 MHz counter clock, and 10 MHz / 1000 ticks = 10 kHz.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### pwm-resolution
pwm, easy, auto

**base** -> `10`

> A PWM timer counts from 0 to TOP inclusive with TOP = 1023, giving TOP + 1 distinct compare positions in each period. How many bits of duty cycle resolution does this provide? Give the answer as a decimal integer.

**rename** -> `10`

> A pulse-width modulator increments its counter from 0 up to a period register value of 1023 inclusive, so each cycle offers 1023 + 1 distinct compare match positions. How many bits of duty resolution does that correspond to? Give the answer as a decimal integer.

**renumber** -> `8`

> A PWM timer counts from 0 to TOP inclusive with TOP = 255, giving TOP + 1 distinct compare positions in each period. How many bits of duty cycle resolution does this provide? Give the answer as a decimal integer.

Why `10`: TOP + 1 = 1024 distinct steps, and log2(1024) = 10 bits.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### gpio-rmw
gpio, medium, auto

**base** -> `0xA6`

> An 8-bit output register PORTA currently holds 0b10101100. Firmware must set bit 1 and clear bit 3 while leaving every other bit unchanged, where bit 0 is the least significant bit. What value does PORTA hold afterwards? Give the answer in hexadecimal.

**rename** -> `0xA6`

> An 8-bit general purpose output latch named OUTREG currently holds 0b10101100. A driver needs to drive bit 1 high and bit 3 low without disturbing the remaining bits, where bit 0 is the least significant bit. What value does OUTREG hold afterwards? Give the answer in hexadecimal.

**renumber** -> `0x4B`

> An 8-bit output register PORTA currently holds 0x5A. Firmware must set bit 0 and clear bit 4 while leaving every other bit unchanged, where bit 0 is the least significant bit. What value does PORTA hold afterwards? Give the answer in hexadecimal.

Why `0xA6`: 0b10101100 is 0xAC. Setting bit 1 gives 0b10101110, and clearing bit 3 gives 0b10100110, which is 0xA6.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### gpio-pullup
gpio, easy, auto

**base** -> `0.33` mA

> An input pin is held up by a 10 kilohm pull-up resistor connected to a 3.3 V rail. A switch pulls the pin to ground, closing the circuit. Ignoring pin leakage current, how much current flows through the pull-up resistor? Give the answer in milliamps.

**rename** -> `0.33` mA

> A digital input is biased high through a 10 kilohm resistor tied to a 3.3 V supply. When a button is pressed the input is shorted to the ground rail. Neglecting input leakage, what current flows in the bias resistor while the button is held? Give the answer in milliamps.

**renumber** -> `1.0638` mA

> An input pin is held up by a 4.7 kilohm pull-up resistor connected to a 5.0 V rail. A switch pulls the pin to ground, closing the circuit. Ignoring pin leakage current, how much current flows through the pull-up resistor? Give the answer in milliamps.

Why `0.33` mA: The full rail voltage appears across the resistor, so I = 3.3 V / 10 kilohm = 0.33 mA.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### field-extract
registers, medium, auto

**base** -> `0x3D`

> A 32-bit peripheral register reads back as 0xDEADBEEF. One of its fields occupies bits 12 down to 7 inclusive, where bit 0 is the least significant bit. What is the value of that field? Give the answer in hexadecimal.

**rename** -> `0x3D`

> A 32-bit control register in a memory-mapped peripheral currently contains 0xDEADBEEF. A configuration bitfield is defined as spanning bit positions 12 through 7 inclusive, counting bit 0 as the least significant. What value is currently stored in that bitfield? Give the answer in hexadecimal.

**renumber** -> `0x45`

> A 32-bit peripheral register reads back as 0x12345678. One of its fields occupies bits 19 down to 12 inclusive, where bit 0 is the least significant bit. What is the value of that field? Give the answer in hexadecimal.

Why `0x3D`: Shifting right by 7 and masking six bits isolates the field: (0xDEADBEEF >> 7) & 0x3F = 0x3D.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### rtos-preempt
rtos, easy, **manual**

**base** -> `Task B`

> A preemptive fixed-priority scheduler is running, where a larger priority number means higher priority. Task A has priority 10 and is currently executing. Task B, priority 20, becomes ready at the same instant that Task C, priority 5, becomes ready. Which task executes next? Answer with the task name only.

**rename** -> `Task B`

> A scheduler always runs the highest-priority ready task, and will interrupt a running task the moment a more urgent one becomes ready. Priority values rise with urgency. Task A, at priority 10, is currently on the processor. At one instant Task B at priority 20 and Task C at priority 5 both become ready. Which task runs next? Answer with the task name only.

**renumber** -> `Task A`

> A preemptive fixed-priority scheduler is running, where a larger priority number means higher priority. Task A has priority 30 and is currently executing. Task B, priority 20, becomes ready at the same instant that Task C, priority 5, becomes ready. Which task executes next? Answer with the task name only.

Why `Task B`: Task B has the highest priority of the three, so a preemptive scheduler preempts Task A and runs Task B.

- [x] Correct
- [x] Unambiguous
- [x] Rename holds
- [x] Renumber holds

### rtos-utilization
rtos, medium, auto

**base** -> `56.25` %

> Three independent periodic tasks are scheduled on one processor. Their worst-case execution times and periods in milliseconds are (1, 4), (2, 8) and (1, 16). What is the total processor utilization? Give the answer as a percentage.

**rename** -> `56.25` %

> Three independent periodic threads share a single core. Thread 1 needs at most 1 ms every 4 ms, thread 2 needs at most 2 ms every 8 ms, and thread 3 needs at most 1 ms every 16 ms. What fraction of the core do they demand in total? Give the answer as a percentage.

**renumber** -> `60` %

> Three independent periodic tasks are scheduled on one processor. Their worst-case execution times and periods in milliseconds are (2, 10), (3, 15) and (1, 5). What is the total processor utilization? Give the answer as a percentage.

Why `56.25` %: Utilization is the sum of C/T: 1/4 + 2/8 + 1/16 = 0.5625, or 56.25 percent.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### rtos-rm-bound
rtos, medium, auto

**base** -> `77.976` %

> Rate-monotonic scheduling has a sufficient schedulability bound of n(2^(1/n) - 1) for n independent periodic tasks. What is that bound for 3 tasks? Give the answer as a percentage.

**rename** -> `77.976` %

> The Liu and Layland utilization test gives a sufficient condition for rate-monotonic schedulability of n independent periodic tasks, namely that total utilization stays at or below n(2^(1/n) - 1). Evaluate that threshold for a task set of size 3. Give the answer as a percentage.

**renumber** -> `74.349` %

> Rate-monotonic scheduling has a sufficient schedulability bound of n(2^(1/n) - 1) for n independent periodic tasks. What is that bound for 5 tasks? Give the answer as a percentage.

Why `77.976` %: 3 x (2^(1/3) - 1) = 3 x 0.259921 = 0.779763, or 77.976 percent.

- [ ] Correct
- [ ] Unambiguous
- [ ] Rename holds
- [ ] Renumber holds

### qnx-ipc
rtos, medium, **manual**

**base** -> `SEND-blocked`

> A QNX Neutrino client thread calls MsgSend() to a server thread that has not yet called MsgReceive(). What blocking state does the client enter? Answer with the state name only.

**rename** -> `SEND-blocked`

> Under QNX Neutrino message-passing IPC, a requesting thread issues MsgSend() to a service thread that is busy and has not reached its MsgReceive() call. In which blocking state does the requesting thread wait? Answer with the state name only.

**renumber** -> `REPLY-blocked`

> A QNX Neutrino client thread calls MsgSend() to a server thread. The server has already called MsgReceive() and has taken the message, but has not yet called MsgReply(). What blocking state is the client in? Answer with the state name only.

Why `SEND-blocked`: Until the server calls MsgReceive() the message has not been taken, so the client waits in the SEND-blocked state.

- [x] Correct
- [x] Unambiguous
- [x] Rename holds
- [x] Renumber holds

### timer-tick
timers, medium, auto

**base** -> `1000` Hz

> A timer is clocked from a 16 MHz source through a prescaler that divides by 64. The counter runs from 0 to TOP inclusive with TOP = 249 and raises an interrupt each time it wraps, so one interrupt period spans TOP + 1 counter ticks. What is the interrupt rate? Give the answer in Hz.

**rename** -> `1000` Hz

> A hardware counter is driven from a 16 MHz oscillator through a clock divider set to 64. The counter increments from 0 up to a period value of 249 inclusive and signals an overflow interrupt on wrap, so each interrupt spans 249 + 1 increments. How often does the interrupt fire? Give the answer in Hz.

**renumber** -> `250` Hz

> A timer is clocked from an 8 MHz source through a prescaler that divides by 256. The counter runs from 0 to TOP inclusive with TOP = 124 and raises an interrupt each time it wraps, so one interrupt period spans TOP + 1 counter ticks. What is the interrupt rate? Give the answer in Hz.

Why `1000` Hz: 16 MHz / 64 = 250 kHz counter clock, and 250 kHz / 250 ticks = 1000 Hz.

- [x] Correct
- [x] Unambiguous
- [x] Rename holds
- [x] Renumber holds
