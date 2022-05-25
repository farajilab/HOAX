#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json 
from netCDF4 import Dataset
import numpy as np
from scipy.spatial.distance import pdist
import random
from sklearn.model_selection import train_test_split
import NeuralNetwork
from SimulatedAnnealing import SimulatedAnnealing
from GridSearch import GridSearch
import tables as tb

import math
print("hello") 
with open('configSO.json') as f:
  print(f)
  config = json.loads(f.read())
import random

print(config)


# In[2]:



lowest_error, best_network = math.inf, None
sizebounds = config['config']['simulated_annealing']['hiddenlayer_size']
layerbounds = config['config']['simulated_annealing']['hiddenlayer_number']
learningbounds = config['config']['simulated_annealing']['learning_rates']
batchsize = config['config']['simulated_annealing']['batch_size']



print(random.randint(sizebounds[0],sizebounds[1]))
print(random.choice(learningbounds))

#for n in range(self.config['config']['simulated_annealing']['iterations']) :

    


# In[3]:


database = config['config']["database"]["file"]
data = Dataset(database, mode='r')
if config['config']["database"]["crdmode"] == "cartesian":
    dbset = np.copy(data['crd'])
    coordinatesout = []
    for j,i in enumerate(dbset):
        if j == 0:
            coordinatesout = [pdist(i)]
        else:
            coordinatesout = np.concatenate((coordinatesout,[pdist(i)]))
            
energyout =np.copy(data['energy'])-np.amin(data['energy'])     
print(coordinatesout)
print(energyout)


# In[4]:


coordinates, val_coordinates, output, val_output = train_test_split(coordinatesout, energyout , test_size=config['config']['simulated_annealing']['validation_ratio'])

print(output,val_output)
print(coordinates, val_coordinates)


# In[5]:


#if (any(i == 'simulated_annealing' for i in config['config'])):
#    if (any(j == 'neural_network' for j in config['config'])):
#        optimizer = SimulatedAnnealing(config,coordinates,  output,val_coordinates, val_output)
#        optimizer.run()



num = config['config']["neural_network"]["epochs"]/config['config']["neural_network"]["epoch_step"]
print(num)
class NeuralNetworkRun(tb.IsDescription):
    idNumber  = tb.Int64Col()
    hiddenLayers = tb.Int64Col()
    nodesPerLayer = tb.Int64Col()
    batchsize = tb.Int64Col()
    learningRate = tb.Int64Col()
    validationError = tb.Float64Col(shape=(num,))
    
     
    

filesaving = tb.open_file(config['config']["neural_network"]["logging_file"],mode="w")
root = filesaving.root
group = filesaving.create_group(root,"NeuralNetworkRun")
     
gRuns = root.NeuralNetworkRun 
table = filesaving.create_table("/NeuralNetworkRun","NeuralNetworkRun1",NeuralNetworkRun,"Runs:"+"NeuralNetworkRun1")
table.flush()
print(filesaving)
filesaving.close()

if (any(i == 'simulated_annealing' for i in config['config'])):
    if (any(j == 'simulated_annealing' for j in config['config'])):
        optimizer = SimulatedAnnealing(config,coordinates,  output,val_coordinates, val_output)
        optimizer.run()
        
        


# In[ ]:




# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:



