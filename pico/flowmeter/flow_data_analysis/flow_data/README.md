Date: June 14 2024
Location: Jessica's front porch in New Haven
These experiments involve attaching a garden hose to a couple feet of copper pipe (with a manual shut-off ball valve), to the Sen HZ43W Hall Effect meter, to an omega meter that sends out a pulse per 1/10th of a gallon, to more garden hose, to a garden sprayer (to a tomato).

For the folders directly in the top level folder the dragon was in a horizontal position with a garden sprayer attached at the end (aimed at a tomato). For the vertical subfolder, the above assembly (aka "the dragon") was in a vertical position.  For the lower pressure subfolder, the assembly is horizontal again but the garden sprayer was removed.

We record nanosecond (really microsecond) timestamps on a pico w using IRQ RISING triggers on the PIO state machines. We do this for both the omega and the hall. The pico runs out of memory after a while, but instead of figuring out serial or wifi comms we are just saving these locally to the pico and then re-running. The naming scheme is "about_n_hz*.csv" where * is nothing for the first in a series, and then 1,2,3 etc. 