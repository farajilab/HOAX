#!/usr/bin/env python
# coding: utf-8

# In[1]:





# In[2]:


import torch
import math
import numpy as np
import pickle
from torch.utils.data import Subset
from torch.utils.data import TensorDataset, DataLoader
from torchvision import datasets
import shutil
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import tables as tb

class NeuralNetwork():
    def __init__(self, config, train_input,train_output,val_input,val_output,
                 hiddenlayer_size,hiddenlayer_number, learning_rate,batch_size ): 
       
        self.dataset = NNDataset(train_input,train_output)
        self.validationset = NNDataset(val_input,val_output)
        self.dataloader = DataLoader(self.dataset, batch_size=batch_size,shuffle= 'True')
        self.hiddenlayer_size = hiddenlayer_size
        self.batch_size = batch_size
        self.hiddenlayer_number = hiddenlayer_number
        self.learning_rate = learning_rate
        #self.dataset.output_shape()
        self.epochs = config['config']['neural_network']['epochs']
        self.epoch_step = config['config']['neural_network']['epoch_step']
        self.weights_file = "pytorchweights.ph"
        self.model_filename = config['config']['neural_network']['model_filename']

        self.loggingfile = config['config']['neural_network']['logging_file']
        self.printingfile = config['config']['neural_network']['plotting_file']
        network = NeuralNet( len(train_input[0]), hiddenlayer_size, hiddenlayer_number, len(train_output[0]),  
                              config['config']['neural_network']['activation'])
        self.model = network.model
        self.loss_fn = self.get_loss_function(config['config']['neural_network']['loss_function'])
        self.model.double()
    # Use the optim package to define an Optimizer that will update the weights of
    # the model for us. Here we will use Adam; the optim package contains many other
    # optimization algoriths. The first argument to the Adam constructor tells the
    # optimizer which Tensors it should update.
        self.learning_rate = learning_rate
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # N is batch size; D_in is input dimension;
        # H is hidden dimension; D_out is output dimension.
        # create your dataset
        # create your dataloade






    def get_interpolators(self, db, properties):
        print("test")

    def save(self, filename):
        torch.save(self.model, filename)
    
    def _save(self):
        torch.save(self.model, self.weights_file)

    def loadweights(self, filename):
        self.model = torch.load(filename)
        self.model.eval()

    def get_interpolators_from_file(self, filename, properties):
        """Properties contains a tuple of [energy,gradient] """
        return {prop_name: self.db[prop_name].shape[1:] for prop_name in properties}


    def get(self, request):
        """Gives object with coordinates and desired properties"""
        pass
    def export(self):
        shutil.copy(self.weights_file, self.model_filename)
    def train(self):
        minimum_loss = math.inf
        printinglog = []
        for t in range(self.epochs):

            for index, data in enumerate(self.dataloader,0):
                local_batch, local_labels = data
                #print(local_batch)
                # Forward pass: compute predicted y by passing x to the model.
                y_pred = self.model(local_batch)

                # Compute and print loss.
                #print(y_pred)
                #print(local_labels)
                loss = self.loss_fn(y_pred, local_labels)
                #print(loss)

                # Before the backward pass, use the optimizer object to zero all of the
                # gradients for the variables it will update (which are the learnable
                # weights of the model). This is because by default, gradients are
                # accumulated in buffers( i.e, not overwritten) whenever .backward()
                # is called. Checkout docs of torch.autograd.backward for more details.
                self.optimizer.zero_grad()
                # Backward pass: compute gradient of the loss with respect to model
                # parameters
                loss.backward()

                # Calling the step function on an Optimizer makes an update to its
                # parameters
                self.optimizer.step()
                

            if t % self.epoch_step == 0:
                
                lossprint = np.sqrt(self.validate_model(t)/len(self.validationset))
                if lossprint < minimum_loss:
                    minimum_loss = lossprint
                    self._save()
                print(f"{lossprint} {t} {self.hiddenlayer_size} {self.hiddenlayer_number} {self.learning_rate} {self.batch_size}")
                printinglog.append(lossprint)
                with open(self.printingfile, 'wb') as f:
                    pickle.dump(printinglog,f)
                #file = open(self.loggingfile,"a")
                #file.write(f"Loss = {lossprint} \n Epochs = {self.epochs} \n Hiddenlayer Size = {self.hiddenlayer_size}  \n Hiddenlayer Number = {self.hiddenlayer_number} \n Learningrate = {self.learning_rate} \n Lowest error = {minimum_loss}\n \n")
                #file.close()

        print("Done Training")
        filesaving = tb.open_file(self.loggingfile,mode="a")
        print(filesaving)
        root = filesaving.root
        idnumber = 0
        table = root.NeuralNetworkRun.NeuralNetworkRun1
        for row in table.iterrows():
            idnumber +=1

        addTable=table.row 
        addTable['idNumber'] = idnumber
        addTable['hiddenLayers'] = self.hiddenlayer_number
        addTable['nodesPerLayer'] = self.hiddenlayer_size
        addTable['batchsize'] = self.batch_size
        addTable['learningRate'] = self.learning_rate
        addTable['validationError'] =np.array(printinglog)
        addTable.append()
        table.flush()
        filesaving.close()

        return minimum_loss
        
        

    def validate_model(self,n):
        model_predictions = []
        testpoint_positions = []
        losssquared = 0
        for local_batch, local_labels in self.validationset:
                # Forward pass: compute predicted y by passing x to the model.
                y_pred = self.model(torch.flatten(local_batch))
                #print(y_pred)
                model_predictions.append(y_pred.tolist())
                # Compute and print loss
                testpoint_positions.append(local_batch.tolist())
                loss = self.loss_fn(y_pred, local_labels)
                losssquared += loss.item()
        #print(model_predictions)
        valLoss =np.sqrt(losssquared /len(self.validationset))
        if valLoss < 0.01 :
            print(valLoss)
            #plt.plot(self.validationset.energyCurves.numpy()-np.amin(self.validationset.energyCurves.numpy()))
            #plt.show()
            #plt.close()
            #plt.plot(model_predictions)
            
            #plt.savefig(f"graph{valLoss}{self.hiddenlayer_size}l{self.hiddenlayer_number}.png")
           # plt.show()
           # plt.close()
        return losssquared
    
    def get_loss_function(self,loss):
        if loss == 'MSE':
            return torch.nn.MSELoss()
class NNDataset(torch.utils.data.Dataset):
    """Molecule Data set"""

    def __init__(self, coordinates, energyCurves):
        self.coordinates =torch.tensor(coordinates)
        self.energyCurves = torch.tensor(energyCurves)

    def __getitem__(self,index):
        coordinate = self.coordinates[index]
        curve = self.energyCurves[index]

        return coordinate, curve

    def __len__(self):
        return len(self.coordinates)
        
    def input_shape(self):
        return list(self.coordinates[0].size())[0] *3
    def output_shape(self):
        return list(self.energyCurves[0].size())[0]

class NeuralNet(torch.nn.Module):
    def __init__(self, inputsize, hiddensize, hiddennumber, outputsize, normalizer="tanh"):
        super(NeuralNet, self).__init__()
        self.hidden = torch.nn.ModuleList()
        if normalizer == "tanh":
            self.hidden.append(torch.nn.Linear(inputsize, hiddensize))
            self.hidden.append(torch.nn.Tanh())
            for k in range(hiddennumber):
                self.hidden.append(torch.nn.Linear(hiddensize, hiddensize))
                self.hidden.append(torch.nn.Tanh())
            self.hidden.append(torch.nn.Linear(hiddensize,outputsize))
        self.model = torch.nn.Sequential(*self.hidden)
        
        


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:



