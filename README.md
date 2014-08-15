# pythonista-scripts
A collection of various Pythonista scripts by dgelessus.

## BaseNSudoku
A sudoku solver, originally written for a base 25 sudoku, but works with grids of any size. The number range can be adjusted freely, as well as the width and height of the number blocks to allow non-square blocks and grids. Technically it even works with uncertain (multiple solution) sudokus, however the result will then contain empty sets in place of unknown numbers.

## filenav
A simple file navigator with support for accessing the entire directory structure, not just the Script Library. Additional features include automatic file icons depending on type, analysis of a few basic file attributes, and opening files directly in the default editor.

## filenav_plugin
Plugin for [ShellistaExt](http://github.com/briarfox/ShellistaExt) by [briarfox](http://github.com/briarfox) that adds a filenav command, which opens filenav in either the given or current directory.

## KeyboardControl
A proof-of-concept for using an external keyboard to control a UI script.

## PackUI
A means of distribution for .py and .pyui files without requiring any other scripts. The main script packages the two files into a new script, which will extract the files again when run.
