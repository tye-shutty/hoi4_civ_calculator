# hoi4_civ_calculator

Hearts of Iron 4 is a strategy game requiring the player to create a military-industrial complex. This program models the construction part of hoi4 to help players compare different strategies.

The image below graphs the number of military factories the USSR has each month starting January 1936. This program also helps users calculate the area under the graph to find which strategies result in the most military production.

![alt text](https://raw.githubusercontent.com/tye-shutty/hoi4_civ_calculator/master/graphs/ussr.png)
- parameters are designed to model the USSR from 1936 to mid 1941.

My main finding is that it's not worth building civilian factories (civs) purely from a perspective of maximizing production. However, more civs early will boost production of late war material, which is better quality.

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
        in_trade = [(1,0)],
        out_trade = {},
        space_mod = [(1,1)],
        con_goods = [(1,0)],
        debug = False):
```
As Paradox loves it's modifiers, to make the model more accurate they should be entered into the model. All the parameters with '=' have default arguments in case you don't want to deal with that complexity.

### An example of the input data structure:

```
speed_mod = [(1, 1.05), (int(5*30.42),1.15), (int(10*30.42),1.25), (int(27*30.42),1.35)]
```
speed_mod is construction speed that affects all projects. This data structure is an ordered list of day-value pairs. There must be a value for the first day. The program will use the most recent value to the current day. The number 30.42 is the average length of a month in the game, I use this to roughly translate months into days (multiples of 70 for focuses would have been better in some cases). I also wrote a function ymd_to_day to more accurately convert to days.

The day should be the first day the modifier is used to produce something. For example, if a focus completes on jan 10, then it is first used jan 11. Furthermore, Jan 1 in game is not used to produce anything, so jan 11 is actually day 10. ```ymd_to_day(1936,'jan',11)``` will give you the correct day (10).

### Infrastructure

```
inf = {'moselland': [1.7, 10, 3],'rhineland': [1.8, 10, 5], 'brandenburg': [1.8, 12, 9],
       'wurttemberg': [1.8, 8, 6],'sachsen': [1.7, 10, 9],'hannover': [1.7, 8, 5]
       ,'thuringen': [1.6, 8, 1],'franken': [1.7, 6, 2]}
```
inf must include all states where you intend to build something. 1st num corresponds to level of infrastructure, 2nd to the max factories baseline, 3rd to the current number of factories.

### What You Decide to Build

```
con_queue = calc.make_queue([(('inf', 'moselland'),3),(('inf', 'rhineland'),2),(('civ', 'moselland'),9),
              (('civ', 'rhineland'),7),(('mil', 'wurttemberg'),3),(('mil','westfalen'),5),
              (('mil','sachsen'),3),(('mil','brandenburg'),5),(('mil','hannover'),5),
              (('mil','thuringen'),9),(('mil','franken'),5)])
```
What you want, where you want it, and how much. The model will skip projects that have no building space in that state, and run them as soon as space opens up and there's an open production line. 

## Graphing Results

Data from the calculate() method can be graphed as follows:

```
calc.graph([inf_mil_1x, inf_mil_2x, mil_1x, mil_2x], 
           ['mil'],
           ['1 inf then mil (1x con speed)', '1 inf then mil (2x con speed)',
            'mil (1x con speed)', 'mil (2x con speed)'],
           [0.5,1])
```
In this case, I have sent 4 different results (must be inside a list). The second argument is a list of all the buildings I want to graph. The third variable is a list of all the labels for each result (in same order). The final argument is a list of time ratios for finding the area under the curves. For example, ```[0.4]``` would return the area for the last 40% of the graph.
