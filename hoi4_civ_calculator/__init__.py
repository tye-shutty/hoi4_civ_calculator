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

def make_queue(things_amounts):
    con_queue = []
    for t,a in things_amounts:
        con_queue += [t]*a
    return con_queue

def find_task(day):
    "Only one line can work on a particular project in a particular state: eg. civ in moscow"
    for task_i in range(len(con_queue)):
        valid_task = True
        state = con_queue[task_i][1]
        if int(inf[state][1] * ref(space_mod, day)) - inf[state][2] < 1:
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
    if task == 'inf' or int(inf[state][1]*ref(space_mod,day)) - inf[state][2] > 0:
        try:
            con_queue.remove((task,state))
            #print('continuing', task, state)
            return True
        except:
            pass
    #print('not continuing',task,state)
    return False

class ProdLine():
    def __init__(self, task, num_civ):
        self.progress = 0
        self.init_task(task)
        self.num_civ = num_civ
        
    def construct(self, day):
        cost = task_cost[self.task]*ref(unique_cost_mod[self.task], day)
        spd_mod = ref(speed_mod, day)
        spd_mod+=ref(unique_spd_mod[self.task], day)
        spd_mod*=inf[self.state][0] if self.task != 'inf' else 1
        #print(self.state, 'spd', spd_mod, inf[self.state][0])
        self.progress += spd_mod*civ_spd_base*self.num_civ
        
        if self.progress >= cost:
            print('completed', self.task, 'in', self.state)
            if self.task == 'civ':
                add_civ(day)
            elif self.task == 'civ_con':
                add_civ(day)
                daily_reports[-1]['mil'] -= 1
                if daily_reports[-1]['mil'] < 0:
                    raise Exception('Converted a non-existing mil')
            elif self.task == 'mil':
                add_mil(day)
            elif self.task == 'inf':
                add_inf(self.state)
            else:
                add_other(self.task)
                           
            if continue_task(self.task, self.state, day):
                self.init_task((self.task, self.state))
            else:
                self.init_task(find_task(day))
            
            self.progress -= cost
                
        print(self.state, self.task, 'progress', '{0:.2f}%'.format(self.progress/cost*100))
                                        
    def init_task(self, task):
        print('starting', task)
        self.task, self.state = task

def inc_con_good(day):
    n_fac = daily_reports[-1]['civ'] + daily_reports[-1]['mil']
    return int(n_fac*ref(con_goods,day)) > int((n_fac-1)*ref(con_goods, day))
    
def add_civ(day):
    daily_reports[-1]['civ'] += 1
    if not inc_con_good(day):
        if prod_lines[-1].num_civ < 15:
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
    if name == 'mil_con':
        remove_civ()
        daily_reports[-1]['civ'] -= 1

def init(speed_modp, unique_spd_modp, unique_cost_modp, free_stuffp, space_modp, con_goodsp, 
         daily_reportsp, infp, con_queuep, final_dayp):
    global speed_mod
    global unique_spd_mod
    global unique_cost_mod
    global free_stuff
    global space_mod
    global con_goods
    global daily_reports
    global inf
    global con_queue
    global final_day
    speed_mod = speed_modp
    unique_spd_mod = unique_spd_modp
    unique_cost_mod = unique_cost_modp
    free_stuff = free_stuffp
    space_mod = space_modp
    con_goods = con_goodsp
    daily_reports = daily_reportsp
    inf = infp
    con_queue = con_queuep
    final_day = final_dayp

    global temp_inf
    global prod_lines
    temp_inf = [] #temp storage to avoid propogating effects of finishing inf
    prod_lines = [] #process back to front to avoid propogating effects of finishing civs

    i = daily_reports[0]['civ']-int((daily_reports[0]['civ']+daily_reports[0]['mil'])*ref(con_goods,1))
    while i > 0: #initialize prod_lines
        n = i if i < 15 else 15
        i -= 15
        prod_lines.append(ProdLine(find_task(1), n))

def execute():
    day = 1        
    while day <= final_day:
        print('day', day)
        for thing in free_stuff:
            if day in free_stuff[thing]:
                if thing == 'civ':
                    for _ in range(free_stuff[thing][day]):
                        add_civ(day)
                        #print('civ', daily_reports[-1]['civ'])
                elif thing == 'mil':
                    for _ in range(free_stuff[thing][day]):
                        add_mil(day)
                elif thing == 'inf':
                    for state in free_stuff[thing][day]:
                        inf[state][0] += free_stuff[thing][day][state]*0.1
                        if inf[free_stuff[thing][day][state]][0] > 2:
                            print('you made too much inf in', state)
                            inf[free_stuff[thing][day][state]][0] = 2
                else:
                    add_other(thing)
                    
        prev = 0
        p = 0
        for p in range(1, len(con_goods)):
            if con_goods[p][0] >= day:
                break
            prev = p
        if p != prev:
            if con_goods[p][0] == day:
                n_fac = daily_reports[-1]['civ'] + daily_reports[-1]['mil']
                diff = int(n_fac*con_goods[p][1]) - int(n_fac*con_goods[prev][1])
                for _ in range(diff):
                    add_civ(day)
                for _ in range(diff*-1):
                    remove_civ()
            
        if day%30==0:
            print(daily_reports[-1])                    
        daily_reports.append(daily_reports[-1])
                
        #don't make me program this for people who swap the order of production lines
        for line_i in range(len(prod_lines))[::-1]:
            prod_lines[line_i].construct(day)
        global temp_inf
        for state in temp_inf:
            #print('inf upgrade', inf[state][0])
            inf[state][0] += 0.1
            #print('to', inf[state][0])
        temp_inf = []
        day += 1