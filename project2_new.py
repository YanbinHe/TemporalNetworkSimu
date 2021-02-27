import igraph
import xdrlib ,sys
import xlrd
import numpy as np
import tacoma as tc
import matplotlib.pyplot as pl
from tacoma.interactive import visualize
from tacoma.drawing import edge_activity_plot
import ssl
from collections import Counter
ssl._create_default_https_context = ssl._create_unverified_context

def illu(tn): #illustrate this network, credit to http://tacoma.benmaier.org/temporal_networks/
    edge_activity_plot(tn,
                   time_normalization_factor = 1/3600.,
                   time_unit='s',
                   alpha = 1.0,  # opacity
                   linewidth = 1.5,
                   )
    pl.show()

# read data
data = xlrd.open_workbook('manufacturing_emails_temporal_network.xlsx')

# pre-processing
table = data.sheet_by_index(0)
node1,node2 = table.col_values(0),table.col_values(1)
timestamp = table.col_values(2)#the first element is a string，then followed by time，starting from [1] to [82876] which is 57791
nrows = table.nrows-1
ncols = table.ncols
del node1[0],node2[0],timestamp[0]#delete all the string in the beginning of the column
node1 = [int(x) for x in node1]
node2 = [int(x) for x in node2]
# number of node
N = max([max(node1),max(node2)])
time_end = max([int(x) for x in timestamp])#57791

# build temporal network, based on examples in and credit to http://tacoma.benmaier.org/temporal_networks/
tn = tc.edge_changes()
tn.N = N
tn.t0 = 0.0# the initial time of experiment
time = list(range(time_end))
del time[0]
tn.t = time # 1 -> 57790
tn.tmax = time_end# 57791
tn.edges_initial = []# there is no link at t = 0
tn_edges_inforuse = []
tn_edges_outforuse = []# these two are used to create list descrbing the change of edges as time in our temporal network
time_flag = 0# a flag used in iteration in timestamp
for i in range(time_end):# 0 -> 57790; create tn.edges_in
    tuple_temporal = []
    while i+1 == timestamp[time_flag]:
        tuple_temporal.append(tuple([node1[time_flag]-1,node2[time_flag]-1]))
        if time_flag < 82875:
            time_flag += 1
        else:
            break
    tn_edges_inforuse.append(tuple_temporal)
# create tn.edges_out; first reverse the 'in list', and then add '[]' to it,then reverse it again, equal to move
# all the elements in 'in list' backward in one step, that is, create these links in t and delete them in t+1
tn_edges_outforuse = tn_edges_inforuse
tn_edges_outforuse = tn_edges_outforuse[::-1]
tn_edges_outforuse.append([])
tn_edges_outforuse = tn_edges_outforuse[::-1]
del tn_edges_outforuse[-1]
tn.edges_in = tn_edges_inforuse
tn.edges_out = tn_edges_outforuse
# illu(tn)
visualize(tn,frame_dt =0.001 )
# model has been built up, then start spreading process # 
# illu(tn)
# edge_activity_plot(tn,
#                    time_normalization_factor = 1/3600.,
#                    time_unit='s',
#                    alpha = 1.0,  # opacity
#                    linewidth = 1.5,
#                    )
# pl.show()
# visualize(tn, frame_dt = 1)
# the mark of nodes, healthy: 0, infected: 1

# seed = 1# starting node
# mark[seed-1] = 1# seed: the first one

def get_node_infected(l):# return the node which is infected
    return [index for (index,value) in enumerate(l) if value == 1]
def infected_process(tn,seed):
    mark[seed] = 1
    ill = get_node_infected(mark)
    infect_number = []
    tn_ed = tn.edges_in
    for time in range(int(tn.tmax)):
        temporal_edges = tn_ed[time]
        ill = get_node_infected(mark)
        for i in range(len(ill)):
            l = list(filter(lambda x: ill[i] in x, temporal_edges))
            for j in range(len(l)):
                mark[l[j][0]] = 1
                mark[l[j][1]] = 1
        infect_number.append(get_number_infected(mark))
    return infect_number
def get_number_infected(l):
    return l.count(1)

mark = [0]*N
data = []
for seed in range(167):# start at different node
    # seed = 1# starting node
    print(seed)
    num_ = infected_process(tn,seed)
    c = [num_[i] + average[i] for i in range(len(average))]
    average = c
    # with open("data_project2.txt","a") as output:
    #     output.write(str(num_)+'\n')
    mark = [0]*N


print('done!')