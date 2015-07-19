#Scuttle - A Fungeoid With Moving Parts
##What is Scuttle?

Scuttle is one of those esoteric programming languages, whose purpose is less to make useful programs, but rather to make people (or at least programmers) shudder with horror and question the sanity of the author.

I'd been reading about various esoteric languages and thought I'd try my hand at one of my own. I admired Befunge's style and Brainfuck's simplicity, and so decided to make one based on the two. As an added twist, I decided that pieces of code should be able to move, or scuttle about. I started writing the spec, and decided that the code should be self modifying as well, beyond movement. So far I've implemented only one of the 4 or so code manipulation instructions.
So what can I do with Scuttle?

In theory, everything that you can do with a Turing machine since the language supports all of Brainfuck's instructions with only two variations. Like Brainfuck (and unlike Befunge), Scuttle uses an array of memory. Like Befunge (and unlike Brainfuck) program execution can flow in any direction. Code is divided into blocks called rafts, which can move independently of each other. Once set into motion, the raft will continue moving until it either hits another raft, is told to stop, or hits the edge of the program.

The instruction set is as follows:
<table style="width: 500px">
		<tr><th>Instruction</th><th>Meaning</th></tr>
		<tr><td valign="top">+</td><td valign="top">Increase value in current memory position</td></tr>
		<tr><td valign="top">-</td><td valign="top">Decrease value in current memory position</td></tr>
		<tr><td valign="top">!</td><td valign="top">Set current memory position to 0</td></tr>
		<tr><td valign="top">a s d f</td><td valign="top">Move current raft west, north, south or east respectively.</td></tr>
		<tr><td valign="top">x</td><td valign="top">Stop movement of current raft</td></tr>
		<tr><td valign="top">h j k l</td><td valign="top">Change direction of program execution to west, north, south or east respectively.</td></tr>
		<tr><td valign="top">&lt; &gt; and ^ v</td><td valign="top">Store the hexadecimal value indicated between the executed instruction and the corresponding closing one into the current memory position. The order the parts of the hexadecimal value are read in depends on which of the instructions was executed.</td></tr>
		<tr><td valign="top">[ ] and ~ _</td><td valign="top">Program flow continues at the corresponding closing instruction. The direction that it searches depends on the current memory value. If zero, [ will search west and ] east, ~ up and _ down, otherwise [ will search east and ] west, ~ down and _ up.</td></tr>
		<tr><td valign="top">o</td><td valign="top">Rock. Never moves and never part of a raft. Will stop rafts. A NOP if executed.</td></tr>
		<tr><td valign="top">$</td><td valign="top">Cannon. Destroys instructions. Which instructions are destroyed depend on the adjacent instructions. If a or h are to its west, the next instruction to the west will be destroyed. Likewise s or j to the north, d or k to the south and f or l to the east.</td></tr>
		<tr><td valign="top">)</td><td valign="top">Move to the next memory position</td></tr>
		<tr><td valign="top">(</td><td valign="top">Move to the previous memory position</td></tr>
		<tr><td valign="top">.</td><td valign="top">Tar. Program execution halts one cycle, but rafts still continue to move.</td></tr>
		<tr><td valign="top">"</td><td valign="top">Prints ASCII character with value equal to current memory position</td</tr>
		<tr><td valign="top">#</td><td valign="top">Prints integer value of current memory position</td></tr>
		<tr><td valign="top">?</td><td valign="top">Gets character from user and stores its ASCII value into current memory position</td></tr>
		<tr><td valign="top">@</td><td valign="top">Indicates program starting position. Blatent Nethack reference.</td></tr>
		<tr><td valign="top">Space</td><td valign="top">Ends program execution. Freely traversed by rafts.</td></tr>
		<tr><td valign="top">Pretty much everything else</td><td valign="top">Blocks rafts, included in rafts, NOP if executed.</td></tr>
	</table>

!, >, >, ^, v and # were added mostly for convenience once I started writing the sample code. Purists can feel free to ignore them.

##Where can I find some Scuttle code, and how does it work?
See helloworld.sct and 99bottles.sct for code, and helloworld.md and 99bottles.md for explanations of execution.