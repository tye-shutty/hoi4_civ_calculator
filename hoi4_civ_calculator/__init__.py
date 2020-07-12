import copy
import matplotlib.pyplot as plt
import pandas as pd

civ_spd_base = 5
task_cost = {'civ': 10800, 'civ_con': 9000, 'mil': 7200, 'mil_con': 4000, 
            'inf': 3000, 'doc': 6400, 'ref': 14500}
            
def ref(list_dict, day):
    prev = list_dict[0]
    for m in list_dict[1:]:
        if m[0] <= day:
            prev = m
        else:
            break
    if prev[0] <= day:
        return prev[1]
    else:
        raise Exception('no value for day ' + str(day))

def day_to_ymd(days):
    m_days = [31,28,31,30,31,30,31,31,30,31,30,31] #no leap years in hoi4
    m_name = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    year = days // 365
    days %= 365
    for m_i in range(len(m_days)):
        days -= m_days[m_i]
        if days <= 0:
            return (year+1936,m_name[m_i], m_days[m_i]+days)
        
def ymd_to_day(year, month, day):
    m_days = [31,28,31,30,31,30,31,31,30,31,30,31] #no leap years in hoi4
    m_name = {'jan':0,'feb':1,'mar':2,'apr':3,'may':4,'jun':5,'jul':6,'aug':7,'sep':8,'oct':9,'nov':10,'dec':11}
    days = (year-1936)*365
    days += sum(m_days[:m_name[month]])
    days += day
    return days-1 #-1 because jan 1st is useless

##make one of these for modifiers? -nah it's easy enough
def make_queue(things_amounts):
    con_queue = []
    for t,a in things_amounts:
        con_queue += [t]*a
    return con_queue

def graph(scenarios, buildings, labels, area=[1]):
    "area is ratio of time from the end date used in calculating the integral" 
    fig, ax = plt.subplots(figsize=(14, 9))
    data = {}
    for report_i in range(len(scenarios)):
        for b in buildings:
            y = [r[b] for r in scenarios[report_i]]
            plt.plot(range(len(scenarios[report_i])), y, label=labels[report_i]+': '+b)
            data[labels[report_i]+': '+b] = {}
            for ratio in area:
                days = int(len(scenarios[report_i])*ratio)
                data[labels[report_i]+': '+b]['integral of last '+str(days)+' days'] = sum(y[-days:])
                #print('scenario '+str(report_i)+' '+b,'integral of last',days,'days', sum(y[-days:]))
    plt.legend()
    plt.show()
    return pd.DataFrame(data)

def find_task(day):
    "Only one line can work on a particular project in a particular state: eg. civ in moscow"
    valid_task = False
    task_i = 0
    for task_i in range(len(con_queue)):
        valid_task = True
        state = con_queue[task_i][1]
        limited = con_queue[task_i][0] not in ['inf', 'civ_con', 'mil_con']
        if limited and int(inf[state][1] * ref(space_modg, day)) - inf[state][2] < 1:
            if debugg:
                print('no space for construction in', con_queue[task_i][1])
            valid_task = False
        for line in prod_lines:
            if con_queue[task_i][0] == line.task and con_queue[task_i][1] == line.state:
                valid_task = False
                break
        if valid_task:
            break
    if valid_task:
        return con_queue.pop(task_i)
    else:
        raise Exception('No available construction task')
        
def continue_task(task, state, day):
    "returns True if matching task-state combos in the queue"
    if debugg:
        print(task,state,'space:',int(inf[state][1]*ref(space_modg,day)),'used',inf[state][2])
    unlimited = task in ['inf', 'civ_con', 'mil_con']
    if unlimited or int(inf[state][1]*ref(space_modg,day)) - inf[state][2] > 0:
        try:
            con_queue.remove((task,state))
            #print('continuing', task, state)
            return True
        except:
            pass
    #print('not continuing',task,state)
    return False

"""if can't continue, civs get distributed to other lines --in hoi4, it appears all 
remaining progress is lost"""
kill = []

class ProdLine():
    def __init__(self, task, num_civ):
        self.progress = 0
        self.init_task(task)
        self.num_civ = num_civ
        
    def construct(self, day):
        cost = task_cost[self.task]*ref(unique_cost_modg[self.task], day)
        spd_mod = ref(speed_mod, day)
        spd_mod+=ref(unique_spd_modg[self.task], day)
        spd_mod*=inf[self.state][0] if self.task != 'inf' else 1
        #print(self.state, 'spd', spd_mod, inf[self.state][0])
        work = spd_mod*civ_spd_base*self.num_civ
        self.progress += work
        
        if self.progress >= cost:
            if debugg:
                print('completed', self.task, 'in', self.state)
            if self.task not in ['civ_con', 'mil_con', 'inf']:
                inf[self.state][2] += 1
            if self.task == 'civ':
                bld_civ(day)
            elif self.task == 'civ_con':
                bld_civ(day)
                daily_reports[-1]['mil'] -= 1
                if daily_reports[-1]['mil'] < 0:
                    raise Exception('Converted a non-existing mil')
            elif self.task == 'mil':
                add_mil(day)
            elif self.task == 'mil_con':
                add_mil_con()
            elif self.task == 'inf':
                add_inf(self.state)
            else:
                add_other(self.task)
                           
            if continue_task(self.task, self.state, day):
                self.init_task((self.task, self.state))
            else:
                kill.append((self.task,self.state))
            
            self.progress -= cost
        if debugg:
            print(self.state, self.task, 'progress', '{0:.2f}%'.format(self.progress/cost*100),
            'civ', self.num_civ, 'inf {0:.2f}'.format(inf[self.state][0]), 
            'mod {0:.2f}'.format(ref(unique_spd_modg[self.task], day)+ref(speed_mod, day)),
            'prog {0:.2f}'.format(self.progress), 'today {0:.2f}'.format(work), 'cost {0:.1f}'.format(cost))
                                        
    def init_task(self, task):
        if debugg:
            print('starting', task)
        self.task, self.state = task

def inc_con_good(day):
    """It appears that the game calculates consumer goods to at least 1/10 precision, so Germany's starting consumer
    goods ratio is actually 15.8%. Then, it seems the number of goods factories is rounded. e.g., Germany's starting
    goods factories is 9.48 (rounded to 9), then after they build one factory goods change to 9.638 (10)"""
    n_fac = daily_reports[-1]['civ'] + daily_reports[-1]['mil']
    #print('old vs new goods', round((n_fac-1)*ref(con_goodsg, day)), round(n_fac*ref(con_goodsg,day)))
    return round(n_fac*ref(con_goodsg,day)) > round((n_fac-1)*ref(con_goodsg, day))
    
def bld_civ(day):
    daily_reports[-1]['civ'] += 1

    if not inc_con_good(day):
        add_civ(day)

def add_civ(day):
    if len(prod_lines) != 0 and prod_lines[-1].num_civ < 15:
        prod_lines[-1].num_civ += 1
    else:
        prod_lines.append(ProdLine(find_task(day), 1))

def remove_civ():
    try:
        i = -1
        while prod_lines[i].num_civ <= 0:
            i -= 1
        prod_lines[i].num_civ -= 1
    except:
        pass
def add_mil(day):
    daily_reports[-1]['mil'] += 1
    if inc_con_good(day):
        remove_civ()
    
def add_inf(state):
    temp_inf.append(state)
    
def add_other(name):
    daily_reports[-1][name] += 1

def add_mil_con():
    remove_civ()
    daily_reports[-1]['civ'] -= 1
    daily_reports[-1]['mil'] += 1

def calculate(daily_reportsp, con_queuep, infp, final_dayp, speed_modp,
        unique_spd_mod = {'civ': [(1,0)], 'civ_con': [(1,0)], 'mil': [(1,0)], 'mil_con': [(1,0)],
                           'ref': [(1,0)], 'inf': [(1,0)], 'doc': [(1,0)]}, 
        unique_cost_mod = {'civ': [(1,1)], 'civ_con': [(1,1)], 'mil': [(1,1)], 'mil_con': [(1,1)],
                            'ref': [(1,1)], 'inf': [(1,1)], 'doc': [(1,1)]}, 
        free_stuff = {}, 
        space_mod = [(1,1)],
        con_goods = [(1,0)],
        debug = False):
    global speed_mod
    global unique_spd_modg
    global unique_cost_modg
    global free_stuffg
    global space_modg
    global con_goodsg
    global daily_reports
    global inf
    global con_queue
    global final_day
    global debugg
    speed_mod = speed_modp
    unique_spd_modg = unique_spd_mod
    unique_cost_modg = unique_cost_mod
    free_stuffg = free_stuff
    space_modg = space_mod
    con_goodsg = con_goods
    daily_reports = copy.deepcopy(daily_reportsp)
    inf = copy.deepcopy(infp)
    con_queue = copy.deepcopy(con_queuep)
    final_day = final_dayp
    debugg = debug

    global temp_inf
    global prod_lines
    global kill
    temp_inf = [] #temp storage to avoid propogating effects of finishing inf
    prod_lines = [] #process back to front to avoid propogating effects of finishing civs
    kill = []

    i = daily_reports[0]['civ']-int((daily_reports[0]['civ']+daily_reports[0]['mil'])*ref(con_goodsg,1))
    while i > 0: #initialize prod_lines
        n = i if i < 15 else 15
        i -= 15
        prod_lines.append(ProdLine(find_task(1), n))

    return execute()

def execute():
    day = 1        
    while day <= final_day:
        if debugg:
            print('{0[1]} {0[2]} {0[0]}'.format(day_to_ymd(day+1)))
        for thing in free_stuffg:
            if day in free_stuffg[thing]:
                if thing == 'civ':
                    for _ in range(free_stuffg[thing][day]):
                        bld_civ(day)
                        #print('civ', daily_reports[-1]['civ'])
                elif thing == 'mil':
                    for _ in range(free_stuffg[thing][day]):
                        add_mil(day)
                elif thing == 'inf':
                    for state in free_stuffg[thing][day]:
                        inf[state][0] += free_stuffg[thing][day][state]*0.1
                        if inf[state][0] > 2:
                            if debugg:
                                print('you made too much inf in', state)
                            inf[state][0] = 2
                else:
                    add_other(thing)
                    
        prev = 0
        p = 0
        for p in range(1, len(con_goodsg)):
            if con_goodsg[p][0] >= day:
                break
            prev = p
        if p != prev:
            if con_goodsg[p][0] == day:
                n_fac = daily_reports[-1]['civ'] + daily_reports[-1]['mil']
                diff = int(n_fac*con_goodsg[p][1]) - int(n_fac*con_goodsg[prev][1])
                for _ in range(diff):
                    bld_civ(day)
                for _ in range(diff*-1):
                    remove_civ()
            
        if day%30==0 and debugg:
            print('report',daily_reports[-1])     #180               
        daily_reports.append(daily_reports[-1].copy())
        #don't make me program this for people who swap the order of production lines
        for line_i in range(len(prod_lines))[::-1]:
            prod_lines[line_i].construct(day)
        global temp_inf
        for state in temp_inf:
            #print('inf upgrade', inf[state][0])
            inf[state][0] += 0.1
            #print('to', inf[state][0])
        temp_inf = []

        num_civ = 0
        global kill
        for task, state in kill:
            #print('killing', task, state)
            for line_i in range(len(prod_lines))[::-1]:
                if prod_lines[line_i].state == state and prod_lines[line_i].task == task:
                    num_civ += prod_lines[line_i].num_civ
                    prod_lines.pop(line_i)
                    break
        kill = []
        for _ in range(num_civ):
            add_civ(day+1)

        daily_reports[-1]['goods'] = round((daily_reports[-1]['mil']+daily_reports[-1]['civ'])*ref(con_goodsg,day))
        day += 1

    return copy.deepcopy(daily_reports)