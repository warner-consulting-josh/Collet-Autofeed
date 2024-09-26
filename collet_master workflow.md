# collet_master workflow and assumptions

**Workflow**
1. Define global variables
   - #<_Length> = XX (Length of bar stock in inches)
   - #<_Remnant> = 1 (Length of remnant for collet to grip)
   - #<_Body_Length> = 1.175 (Length of Body piece)
   - #<_Nut_Length> = 0.6 (Length of Nut piece)
   - #<_Advancing_Length> = 0.283 (Length of material needed for cleanup and bar pulling)
   - #<_one_or_two> = 1 (1 = body 2 = nut)
2. User input dialog box (currently not working, need to downgrade pathpilot)
3. Part count calculation based on previously defined variables
4. Loop correct number and type of part
   - Check whether nut or body and go to corresponding subroutine
   - Run groove and advance subroutine
5. Finish program and print debug statements with number and type of parts

**Assumptions**
- Separate subroutine files for nut, body, and groove advance
- Subroutine folder path has been added to .ini file
  



