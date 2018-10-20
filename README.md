# HD Seed Based Address Generator for Testing

Usage:

To create addresses use"python hd_test.py write"

You will be prompted for a number of addresses to generate
If you don't enter a number it will default to 100
The output will store a list of seeds with the correponding address.
The output is stored in a file called "testfile.txt".
This part also tests for duplicates.

To test the created addresses use "python hd_test.py read"

This uses the seed in "testfile.txt" so recreate the addresses
It compares the re-created addresses to the original address.
If the re-created address is the same as the original then all is good.

The standard test would be to create the testfile.txt on one OS and then
do the re-creation test on a different OS platform and then vice-versa

The test should result on 100% success 
