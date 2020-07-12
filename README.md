# hoi4_civ_calculator
Hearts of Iron 4 is a strategy game requiring the player to create a military-industrial complex. This program models the construction part of hoi4 to help players compare different strategies.

## Input Variables
I uploaded jupyter notebooks with an example of using this program to compare Germany strategies and to compare some theoretical comparisons.
This is the method signature used to create the model:
```
def calculate(daily_reportsp, con_queuep, infp, final_dayp, speed_modp,
        unique_spd_mod = {'civ': [(1,0)], 'civ_con': [(1,0)], 'mil': [(1,0)], 'mil_con': [(1,0)],
                           'ref': [(1,0)], 'inf': [(1,0)], 'doc': [(1,0)]}, 
        unique_cost_mod = {'civ': [(1,1)], 'civ_con': [(1,1)], 'mil': [(1,1)], 'mil_con': [(1,1)],
                            'ref': [(1,1)], 'inf': [(1,1)], 'doc': [(1,1)]}, 
        free_stuff = {}, 
        space_mod = [(1,1)],
        con_goods = [(1,0)],
        debug = False):
```
As Paradox loves it's modifiers, to make the model more accurate they should be entered into the model. All the parameters with '=' have default arguments in case you don't want to deal with that complexity. These can be changed by calling the function like ```calculate(debug=True)```. Debug will print the progress of each factory line every day and other events.

```
speed_mod = [(1, 1.05), (int(5*30.42),1.15), (int(10*30.42),1.25), (int(27*30.42),1.35)]
```
speed_mod is construction speed that affects all projects. This data structure, like many of the following, is a ordered list of day-value pairs. There must be a value for the first day. The program will use the most recent value to the current day. The number 30.42 is the average length of a month in the game, I use this to roughly translate months into days (multiples of 70 for focuses would have been better in some cases). I also wrote a function ymd_to_day to more accurately convert to days.

The day should be the first day the modifier is used to produce something. For example, if a focus completes on jan 10, then it is first used jan 11. Furthermore, Jan 1 in game is not used to produce anything, so jan 11 is actually day 10. ```ymd_to_day(1936,'jan',11)``` will give you the correct day (10).
```
unique_spd_mod = {'civ': [(1,0), (int(5*30.42),.1), calc.ymd_to_day(1936,'oct',8)], 
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
free_stuff represents buildings gained not through construction (trade, warfare, focuses). Unlike the previous data structures, free_stuff is only used on the exact day, so I use a dictionary ```{building:{day:amount}}```. Currently there is no way to model losing factories (by trading them away or losing states).
```
space_mod = [(1,1), (int(14*30.42),1.2), (int(18*30.42),1.4), (int(37*30.42),1.6)] 
```
space_mod is the max factories modifier given by factory tech.
``` 
con_goods = [(1,0.158), (int(15*30.42),0.118)]
```
con_goods is the consumer goods ratio. Depends on stability. Notice that Germany's consumer goods at game start is actually 15.8%, not 16%.
```
daily_reports = [{'civ': 32, 'mil': 28, 'ref': 0, 'doc': 10, 'goods': 9}]
```
daily_reports is a list of dictionaries, the first dictionary is used to set the number of factories in the model. Every day a new dictionary will be added to the list with the most recent counts. This is the return value of calculate(). ref = refinery, doc = dockyard, goods = consumer goods.
```
inf = {'moselland': [1.7, 10, 3],'rhineland': [1.8, 10, 5], 'brandenburg': [1.8, 12, 9],
       'wurttemberg': [1.8, 8, 6],'sachsen': [1.7, 10, 9],'hannover': [1.7, 8, 5]
       ,'thuringen': [1.6, 8, 1],'franken': [1.7, 6, 2]} #where is this in game files?
```
inf must include all states where you intend to build something. 1st num corresponds to level of infrastructure, 2nd to the max factories baseline, 3rd to the current number of factories.
```
con_queue = calc.make_queue([(('inf', 'moselland'),3),(('inf', 'rhineland'),2),(('civ', 'moselland'),9),
              (('civ', 'rhineland'),7),(('mil', 'wurttemberg'),3),(('mil','westfalen'),5),
              (('mil','sachsen'),3),(('mil','brandenburg'),5),(('mil','hannover'),5),
              (('mil','thuringen'),9),(('mil','franken'),5)])
```
con_queue is where you tell the model what to produce. The model will skip projects that have no building space in that state, and run them as soon as space opens up and there's an open production line. 
```
final_day = 365*3
```
Models the game every day for 3 years (No leap years in hoi4).

## Graphing Results

Data from the calculate() method can be graphed as follows:

```
inf_mil_1x = calc.calculate(daily_reports, con_queue1, inf, final_day, speed_mod_1x)
```
First assign the return value to a variable.
```
calc.graph([inf_mil_1x, inf_mil_2x, mil_1x, mil_2x], 
           ['mil'],
           ['1 inf then mil (1x con speed)', '1 inf then mil (2x con speed)',
            'mil (1x con speed)', 'mil (2x con speed)'],
           [0.5,1])
```
Then send that data to graph(). In this case, I have sent 4 different results (must be inside a list). The second argument is a list of all the buildings I want to graph. The third variable is a list of all the labels for each result (in same order). The final argument is a list of time ratios for finding the area under the curves. For example, ```[0.4]``` would return the area for the last 40% of the graph.

The above code produces the following output:
![alt text](https://raw.githubusercontent.com/tye-shutty/hoi4_civ_calculator/temp2/graphs/inf_mil.png)

| | 	1 inf then mil (1x con speed): mil |	1 inf then mil (2x con speed): mil |	mil (1x con speed): mil |	mil (2x con speed): mil |
| - | - | -| - | - |
|**integral of last 548 days** |	7755 |	16201 |	7699 |	15670 |
|**integral of last 1096 days**| 	9924 |	21160 |	10086 |	20708 |

- parameters include 0% consumer goods, and states with 100 building slots

Some of the other sccenarios I have analyzed:
![alt text](https://raw.githubusercontent.com/tye-shutty/hoi4_civ_calculator/temp2/graphs/civ_14_15.png)
- parameters include 2x construction speed, 0% consumer goods, and states with 100 building slots

![alt text](https://raw.githubusercontent.com/tye-shutty/hoi4_civ_calculator/temp2/graphs/civ_mil.png)
- parameters include 2x construction speed, 20% consumer goods, and states with 100 building slots

![alt text](https://raw.githubusercontent.com/tye-shutty/hoi4_civ_calculator/temp2/graphs/germany.png)
- parameters are designed to model Germany in 1936.

All the code for these examples is provided in the jupyter notebooks.
