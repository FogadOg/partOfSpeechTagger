# -*- coding: utf-8 -*-
"""part of speech model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wntZTVBpkuhU7hy60nzog1HbKo6U-71Q

#Imports
"""

import torch
import json
import re
import numpy
from torch import nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm


device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device

BATCH_SIZE=64

"""#Data Preparation

##Tokinizer

###Tokinizer Util
"""

class TokinizerDatasetUtils():
  def __init__(self, maxDictLen=100000):
    self.maxDictLen=maxDictLen
    self.tokinizerDict=dict({"PAD":0, "UNK":1})

  def loadTokinizerDictionary(self, filePath)->None:
    jsonfile=open(filePath)
    jsonObject=json.load(jsonfile)
    self.tokinizerDict=jsonObject

  def createDataset(self, dataset: list[list[str]], fileSavePath=None)->None:
    for sentance in dataset:
      for word in sentance:
        if self.maxDictLen==len(self.tokinizerDict):
          break

        if word not in self.tokinizerDict:
          self.tokinizerDict[word]=len(self.tokinizerDict)

    if fileSavePath !=None:
      self._saveDictionary(fileSavePath)

  def extractSentanceText(self, fileSavePath=None, *DatasetfilePaths)->None:

    dataset=self._extractData("sentence", DatasetfilePaths)
    self.createDataset(dataset, fileSavePath)

  def extractLabelText(self, fileSavePath=None, *DatasetfilePaths)->None:
    dataset=self._extractData("labels", DatasetfilePaths)
    self.createDataset(dataset, fileSavePath)

    self.createDataset(dataset, fileSavePath)

  def _extractData(self, field: str, DatasetfilePaths):
    dataset=[]

    for DatasetfilePath in DatasetfilePaths:
      jsonFile = open(DatasetfilePath)
      jsonArray = json.load(jsonFile)


      for object in jsonArray:
        dataset.append(object[field])
    return dataset

  def _saveDictionary(self, savePath):
    with open(savePath, "w") as outfile:
      json.dump(self.tokinizerDict, outfile)

"""###Tokinizer Class"""

class Tokinizer(TokinizerDatasetUtils):
  def __init__(self, maxDictLen=100000, maxSquenceLength=20):
    super().__init__(maxDictLen)
    self.maxSquenceLength=maxSquenceLength

  def encode(self, sentanceList: list[str])->list[int]:
    encodedSentance=[]

    for word in sentanceList:
      if len(encodedSentance)>=self.maxSquenceLength:
        break

      if word in self.tokinizerDict.keys():
        encodedSentance.append(self.tokinizerDict[word])
      else:
        encodedSentance.append(self.tokinizerDict["UNK"])


    return self.addPaddingToEncoding(encodedSentance)

  def addPaddingToEncoding(self, encoding: list[int])->list[int]:
    paddingLengthRequired=self.maxSquenceLength-len(encoding)
    paddingArray=[self.tokinizerDict["PAD"]]*paddingLengthRequired

    return encoding+paddingArray

  def decode(self, encodedSentance: torch.tensor)->list[str]:
    decodedString=""
    dictKeys=list(self.tokinizerDict.keys())

    for token in encodedSentance.cpu().detach().numpy():
      try:
        wordPosition=list(self.tokinizerDict.values()).index(token)
        decodedString+=dictKeys[wordPosition]+" "
      except ValueError:
        raise ValueError(f"token {token} was not found in dictionary")

    return decodedString

  def __len__(self):
    return len(self.tokinizerDict)

  def __getitem__(self, word)->int:
    return self.tokinizerDict[word]

"""##Dataset"""

class PosDataset(Dataset):
  def __init__(self,filePaths: list):
    self.tokinizerSentance=Tokinizer(maxDictLen=46606)
    self.tokinizerLabel=Tokinizer(maxDictLen=47)

    self.tokinizerSentance.extractSentanceText("/content/drive/MyDrive/posTagging/tokinizerSentanceDict.json", "/content/drive/MyDrive/posTagging/train.json", "/content/drive/MyDrive/posTagging/test.json")
    self.tokinizerSentance.loadTokinizerDictionary("/content/drive/MyDrive/posTagging/tokinizerSentanceDict.json")

    self.tokinizerLabel.extractLabelText("/content/drive/MyDrive/posTagging/tokinizerLabelDict.json", "/content/drive/MyDrive/posTagging/train.json", "/content/drive/MyDrive/posTagging/test.json")
    self.tokinizerLabel.loadTokinizerDictionary("/content/drive/MyDrive/posTagging/tokinizerLabelDict.json")

    self.filePaths=filePaths

    self.datasetSentances=torch.tensor(self.unpackSentances())
    self.datasetLabels=torch.tensor(self.unpackLabels())

  def unpackSentances(self)->list[int]:
    sentanceList=[]

    for filePath in self.filePaths:
      jsonFile = open(filePath)
      jsonArray = json.load(jsonFile)


      for object in jsonArray:
        tokinizedSentace=self.tokinizSentace(object["sentence"])

        sentanceList.append(tokinizedSentace)

    return sentanceList

  def unpackLabels(self)->list[int]:

    labelsList=[]

    for filePath in self.filePaths:
      jsonFile = open(filePath)
      jsonArray = json.load(jsonFile)


      for object in jsonArray:
        tokinizedLabels=self.tokinizLabels(object["labels"])

        labelsList.append(tokinizedLabels)

    return labelsList

  def tokinizSentace(self, sentance: list[str])->list[int]:
    return self.tokinizerSentance.encode(sentance)

  def tokinizLabels(self, labels: list[str])->list[int]:
    return self.tokinizerLabel.encode(labels)

  def detokinizSentace(self, sentance: torch.tensor)->str:
    return self.tokinizerSentance.decode(sentance)

  def detokinizLabels(self, labels: torch.tensor)->str:
    return self.tokinizerLabel.decode(labels)

  def __getitem__(self,idx):
    return self.datasetSentances[idx],self.datasetLabels[idx]

  def __len__(self)->int:
    return len(self.datasetSentances);

dataset=PosDataset(["/content/drive/MyDrive/posTagging/test.json","/content/drive/MyDrive/posTagging/test.json"])

"""##Dataloader"""

class Dataloader():
  def __init__(self, dataset, trainSize: float):
    self.dataset=dataset
    self.trainSize=trainSize

  def trainTestDataloader(self):
    trainDataset, testDataset=self.splitDataset(self.dataset)

    trainDataloader=DataLoader(trainDataset,batch_size=BATCH_SIZE,shuffle=True)
    testDataloader=DataLoader(testDataset,batch_size=BATCH_SIZE,shuffle=True)
    return trainDataloader, testDataloader

  def splitDataset(self, dataset):
    trainSize = int(self.trainSize * len(self.dataset))
    testSize = len(self.dataset) - trainSize
    trainDataset, testDataset = torch.utils.data.random_split(dataset, [trainSize, testSize])

    return trainDataset, testDataset

"""#Model"""

class PosModel(nn.Module):
  def __init__(self, inputSize, hiddenSize, outputSize, padIdx):
    super(PosModel, self).__init__()
    self.embeddingAndDropout=nn.Sequential(
      nn.Embedding(inputSize, hiddenSize, padding_idx=padIdx),
    )
    self.rnn = nn.RNN(hiddenSize, hiddenSize, num_layers=2)
    self.fcSequence = nn.Sequential(
      nn.ReLU(),
      nn.Linear(hiddenSize, outputSize),

    )

  def forward(self, sentence):
    embedded = self.embeddingAndDropout(sentence)
    output, _ = self.rnn(embedded)
    output=self.fcSequence(output)

    return output


inputSize=len(dataset.tokinizerSentance.tokinizerDict)
outputSize=len(dataset.tokinizerLabel.tokinizerDict)


posModel=PosModel(inputSize, 64, outputSize, dataset.tokinizerSentance["PAD"]).to(device)
posModel

"""#Optimizer and loss"""

def parametersCount(model):
  return sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"model parameters: {parametersCount(posModel):,}")

import torch.nn.init as init

def init_weights(m):
    if isinstance(m, nn.Linear):
        init.xavier_normal_(m.weight)

posModel.apply(init_weights)


optimizer = torch.optim.Adam(posModel.parameters(), lr=0.001)

from torch.optim.lr_scheduler import ReduceLROnPlateau
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=20, verbose=True)

loss=nn.CrossEntropyLoss()

"""#Training"""

class ModelTrainer():
  def __init__(self, model, optimizer, loss, dataset, epochs, printEpoch, device, savePathName=None):
    self.model=model
    self.optimizer=optimizer
    self.loss=loss
    self.epochs=epochs
    self.printEpoch=printEpoch
    self.device=device
    self.savePathName=savePathName

    self.currentEpoch=0

    self.trainDataloader, self.testDataloader = Dataloader(dataset,0.8).trainTestDataloader()

    self.startTraining()

  def startTraining(self)->None:
    for epoch in tqdm(range(self.epochs)):
      self.currentEpoch=epoch

      trainGenerator=self.train()
      trainLoss, trainAccuracy=self.unpackGenerator(trainGenerator)

      testGenerator=self.test()
      testLoss, testAccuracy=self.unpackGenerator(testGenerator)

      self.saveModel()
      print(f" epoch {epoch} | train loss: {trainLoss:.2f}, train accuracy: {trainAccuracy:.2f}% | test loss: {testLoss:.2f}, test accuracy: {testAccuracy:.2f}%")

  def train(self) -> torch.tensor:
    self.model.train()
    for input, target in self.trainDataloader:
        self.optimizer.zero_grad()
        input = input.to(self.device, dtype=torch.float32).requires_grad_()
        target = target.to(self.device, dtype=torch.float32).requires_grad_()

        prediction = self.model(input.long())

        loss, accuracy = self.getLossAndAccuracy(prediction, target)
        loss.backward()

        # if self.currentEpoch % self.printEpoch == 0:
        #   print("loss: ",loss.item())
        #   print(f"input:{input.dtype}, target:{target.dtype}, prediction:{prediction.dtype}")
        #   print(f"input: requires_grad={input.requires_grad}, target: requires_grad={target.requires_grad}, prediction: requires_grad={prediction.requires_grad}")
        #   print(f"input: grad={input.grad}, target: grad={target.grad}, prediction: grad={prediction.grad}")
        #   for name, param in self.model.named_parameters():
        #     print(f'{name}: requires_grad={param.requires_grad}, dtype={param.dtype}, grad={param.grad.shape}')


        self.optimizer.step()

        yield loss, accuracy

  def test(self)->torch.tensor:
    self.model.eval()
    for input, target in self.testDataloader:
      self.optimizer.zero_grad()
      input = input.to(self.device, dtype=torch.float32).requires_grad_()
      target = target.to(self.device, dtype=torch.float32).requires_grad_()

      prediction=self.model(input.long())

      if self.currentEpoch%self.printEpoch==0:

        print("\n input: ",dataset.detokinizSentace(input[0]))
        print("\n target:     ",dataset.detokinizLabels(target[0]))
        print("\n prediction: ",dataset.detokinizLabels(prediction.argmax(2)[0]))


      loss, accuracy=self.getLossAndAccuracy(prediction, target)

      yield loss, accuracy

  def saveModel(self)->None:
    if self.savePathName!=None:
      torch.save(self.model.state_dict(), f"/content/drive/MyDrive/pytorchModels/{self.savePathName}.pth")

  def unpackGenerator(self, generator)->torch.tensor:
    generator=next(iter(generator))
    loss, accuracy=generator[0],generator[1]
    return loss, accuracy

  def getLossAndAccuracy(self,prediction,target)->torch.tensor:
    target = target.long()

    prediction_loss = self.loss(prediction.view(-1, 47), target.view(-1))
    prediction_acc = self.accuracy(prediction.argmax(2), target)

    return prediction_loss, prediction_acc

  def accuracy(self,predictions,targets)->torch.tensor:
    assert predictions.shape == targets.shape, "Shapes of predictions and targets must match."

    num_correct = (predictions == targets).sum().item()

    total_samples = targets.numel()
    accuracy_value = num_correct / total_samples
    return accuracy_value*100



# ModelTrainer(posModel, optimizer, loss, dataset, 11, 10, device, "posModel")
ModelTrainer(posModel, optimizer, loss, dataset, 2000, 50, device, "posModel")