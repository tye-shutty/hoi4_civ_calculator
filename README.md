# hoi4_civ_calculator
Hearts of Iron 4 is a strategy game requiring the player to create a military-industrial complex. This program models the game to help players find the best strategies.

## How to Use
I uploaded a jupyter notebook with an example of using this program to model Germany. It may be more up to date than the following excerpts.

As Paradox loves it's modifiers, to make the model more accurate they should be entered into the model.

```
speed_mod = [(1, 1.05), (int(5*30.42),1.15), (int(10*30.42),1.25), (int(27*30.42),1.35)]
```
speed_mod is construction speed that affects all projects. This data structure, like many of the following, is a ordered list of day-value pairs. There must be a value for the first day. The program will use the most recent value to the current day. The number 30.42 is the average length of a month in the game (no leap years in hoi4), I use this to roughly translate months into days (multiples of 70 for focuses would have been better in some cases). 
```
unique_spd_mod = {'civ': [(1,0), (int(5*30.42),.1), (int(29*30.42),0)], 
                  #hire advisor day 5, fire advisor day 30
                  'civ_con': [(1,0), (int(5*30.42),.1), (int(15*30.42),.3),(int(29*30.42),.2)],
                  'mil': [(1,.35), (int(8*30.42),.45), (int(15*30.42),.55)],
                  'mil_con': [(1,.35), (int(14*30.42),.65), (int(15*30.42),.75)], 
                  #many mil bonuses also apply -add them here too
                  'ref': [(1,.15), (int(5*30.42),.25), (int(29*30.42),.15)],
                  'inf': [(1,0), (int(5*30.42),.1), (int(29*30.42),0)],
                  'doc': [(1,.25)]} # these are all added to speed_mod
```
unique_speed_mod values will be added to speed_mod by the program, depending on which type of project is being constructed.
```
unique_cost_mod = {'civ': [(1,1)], # these are the total mods
                  'civ_con': [(1,0.9), (int(8*30.42),0.8)],
                  'mil': [(1,1)],
                  'mil_con': [(1,0.9), (int(8*30.42),0.8)],
                  'ref': [(1,1)],
                  'inf': [(1,1)],
                  'doc': [(1,1)]}
free_stuff = {'civ': {int(8*30.42):6, int(10*30.42):6, int(26*30.42):12, int(29*30.42):3, int(33*30.42):8}, 
              # in case of conquering or focus #Austria & czech civ guess
              #not sure about trade
              'mil': {int(15*30.42):6, int(26*30.42):7, int(29*30.42):3, int(33*30.42):5}, 
              #key is day had thing at end of day
              'ref': {},
              'inf': {int(13*30.42):{'brandenburg': 2, 'hannover': 3, 'thuringen': 4, 'franken': 3}},
              'doc': {}}
```
free_stuff represents buildings gained not through construction (trade, warfare, focuses). Unlike the previous data structures, free_stuff is only used on the exact day, so I use a dictionary ```{building:{day:amount}}```.
```
space_mod = [(1,1), (int(14*30.42),1.2), (int(18*30.42),1.4), (int(37*30.42),1.6)] 
#ind tech for max factories
    
con_goods = [(1,0.16), (int(15*30.42),0.11)] #1st val is first day ending with the change
#also depends on stab
daily_reports = [{'civ': 32, 'mil': 28, 'ref': 0, 'doc': 10}] #output data

#state, inf mod, max fact, present fact
inf = {'moselland': [1.7, 10, 3],'rhineland': [1.8, 10, 5], 'brandenburg': [1.8, 12, 9],
       'wurttemberg': [1.8, 8, 6],'sachsen': [1.7, 10, 9],'hannover': [1.7, 8, 5]
       ,'thuringen': [1.6, 8, 1],'franken': [1.7, 6, 2]} #where is this in game files?
```
inf must include all states where you intend to build something. 1st num corresponds to level of infrastructure, 2nd to the max factories, 3rd to the number of factories.
```
#duplicates will be grouped together unless there's no space left in state 
con_queue = calc.make_queue([(('inf', 'moselland'),3),(('inf', 'rhineland'),2),(('civ', 'moselland'),9),
              (('civ', 'rhineland'),7),(('mil', 'wurttemberg'),3),(('mil','westfalen'),5),
              (('mil','sachsen'),3),(('mil','brandenburg'),5),(('mil','hannover'),5),
              (('mil','thuringen'),9),(('mil','franken'),5)])
```
con_queue is where you tell the model what to produce. The model will skip projects that have no building space in that state, and run them as soon as space opens up and there's an open production line. 
```
final_day = 60 #runs this long
```
