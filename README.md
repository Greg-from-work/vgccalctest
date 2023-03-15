# vgccalctest
Pokemon calculator which allows for team-wide calculations

Initial setup:
1) Download all files and put them in the same directory
2) Open main.py and change the "filesdirectory" field near the top of the file to match the directory you placed the files in
3) Optionally change "level" if playing in a non level50 format

To run the program:
If you wish to use your own team, export it from showdown and paste that data over the contents of team.txt
Next, run main.py

To start, you will be asked to supply a mode.

MODES:  
Type s in order to see how your speed matches up to the enemy team

Type d to see how much damage a particular move from one of the opponent's Pokémon will do to each of your teammembers
Type d+ for the same as the above, but the opposing Pokémon will be treated as having a +Atk/+SpA nature rather than a neutral one

Type a to see how much damage one of your Pokémon can be expected to deal to the whole enemy team

DATA YOU NEED TO ENTER WHILE IN A MODE:  
If asked for an enemy team string, the program is looking for the way that Showdown displays the enemy team. This looks something like:
Lunala / Groudon / Tapu Fini / Tsareena / Incineroar / Stakataka

If in mode a the attacking mon should be one of the pokemon in your team

MULTS:  
The last thing you can be asked for is mults. This is an optional field, so if you don't wish to supply any then just hit enter.

Though the program automatically handles some things (such as typings, STAB, EVs and natures) there are a ton of possible multipliers in pokemon. As an example, consider a specs Gholdengo using make it rain (a spread move) while its ally uses helping hand. Since the point of this program is to give you an idea of how much damage you should expect to take as quickly as possible, I did not want the user to have to spend a long time searching and clicking various buttons. Instead I allow the user to lump all of their multipliers together as a grouping of comma separated values and fractions.

To represent the above example (a gholdengo with choice specs that is using a spread move, while its ally uses helping hand), you can supply the following for mults:
1.5,3/4,1.5

Note that there will potentially be small rounding errors if you use the mults field, since it technically matters which order you multiply things in. This is intentional, since the purpose of this program is speed rather than perfect accuracy, and achieving perfect accuracy requires a lot more time spent by the user on expressing exactly what all of the multipliers are. In my experience the calculations are never off by much, provided that you aren't a little cup player (since lower levels are much more affected by rounding). 

In other words, there should never be a scenario in which it looks like your Pokémon lives 2 hits 100% of the time, if it is in actuality often dead to two hits. If you ever do want exact damage numbers though, I'd suggest either not using the mults field, or using the pokemon showdown calculator.

Below is an example of me running this Gholdengo calculation against the team in the default supplied files.

******************
Example run with the default files
******************

Input the mode:  
d  
Enemy Pokemon name:  
gholdengo  
Move name:  
make it rain  
Mults:  
1.5,3/4,1.5  
bellibolt: 39.1-46.0% or 47.4-55.8%  
ceruledge: 40.1-47.3% or 47.8-56.6%  
oranguru: 56.3-66.5% or 67.5-79.7%  
garchomp: 88.4-104.2% or 106.9-125.9%  
kilowattrel: 75.3-89.0% or 91.1-107.5%  
annihilape: 74.4-87.9% or 89.3-105.6%
