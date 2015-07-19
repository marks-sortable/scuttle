This program prints "Hello, World!". It also demonstrates the use of memory positions and how code can intersect with itself.

Program execution starts at @, and continues moving to the right until it hits the 'k' instruction on the opposite side of the program. It then travels down to the 'h', where it starts to move to the left. The _/~ pair move it up one line without changing its direction, and it continues to the 'j', which sends it moving upwards. At 'l', it resumes its progress to the right, until it falls off the raft and drowns. Through-out this process, it is loading bytes into memory and outputting them to the screen.