Configuration:

Maze Structure:
Either each maze 'cell' contains a parent (NORTH, EAST, SOUTH, WEST) which points to which direction the path will follow.
Or each cell will have bitwise flags for which walls exist / don't exist

Maze Solution:
A series of NORTH, EAST, SOUTH, WEST instructions (0, 1, 2, 3) then potentially compacted into groups of n instructions.