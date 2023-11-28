
"""part of speech model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wntZTVBpkuhU7hy60nzog1HbKo6U-71Q

#Imports
"""

import torch
import json
import re
from torch import nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm


device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

BATCH_SIZE=64

"""#Data Preparation

##Tokinizer

###Tokinizer Util
"""

class TokinizerDatasetUtils():
  def __init__(self, maxDictLen=10000):
    self.maxDictLen=maxDictLen
    self.tokinizerDict=dict({"UNK":0, "PAD":1})

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
  def __init__(self, maxDictLen=10000, maxSquenceLength=100):
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

  def decode(self, encodedSentance: list[int])->list[str]:
    decodedString=""
    dictKeys=list(self.tokinizerDict.keys())

    for token in encodedSentance:
      try:
        wordPosition=list(self.tokinizerDict.values()).index(token)
        decodedString+=dictKeys[wordPosition]
      except ValueError:
        raise ValueError(f"token {token} was not found in dictionary")

    return decodedString


  def __len__(self):
    return len(self.tokinizerDict)

"""##Make Dataset"""

class PosDataset(Dataset):

  def __init__(self,filePaths: list):
    self.tokinizerSentance=Tokinizer(maxDictLen=2000)
    self.tokinizerLabel=Tokinizer(maxDictLen=2000)

    self.tokinizerSentance.extractSentanceText("tokinizerSentanceDict.json", "train.json", "test.json")
    self.tokinizerSentance.loadTokinizerDictionary("tokinizerSentanceDict.json")

    self.tokinizerLabel.extractSentanceText("tokinizerLabelDict.json", "train.json", "test.json")
    self.tokinizerLabel.loadTokinizerDictionary("tokinizerLabelDict.json")




    self.filePaths=filePaths

    self.datasetSentances=torch.tensor(self.unpackSentances())
    self.datasetLabels=torch.tensor(self.unpackLabels())

  def unpackSentances(self)->list[int]:
    sentanceList=[]

    for filePath in self.filePaths:
      jsonFile = open(filePath)
      jsonArray = json.load(jsonFile)


      for object in jsonArray:
        tokinizedSentace=self.tokinizedSentace(object["sentence"])

        sentanceList.append(tokinizedSentace)

    return sentanceList

  def unpackLabels(self)->list[int]:

    labelsList=[]

    for filePath in self.filePaths:
      jsonFile = open(filePath)
      jsonArray = json.load(jsonFile)


      for object in jsonArray:
        tokinizedLabels=self.tokinizedLabels(object["labels"])

        labelsList.append(tokinizedLabels)

    return labelsList

  def tokinizedSentace(self, sentance: list[str])->list[int]:
    return self.tokinizerSentance.encode(sentance)

  def tokinizedLabels(self, labels: list[str])->list[int]:
    return self.tokinizerLabel.encode(labels)

  def __getitem__(self,idx):
    return self.datasetSentances[idx],self.datasetLabels[idx]

  def __len__(self)->int:
    return len(self.datasetSentances);

dataset=PosDataset(["test.json","test.json"])

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

"""##Model"""

class PosModel(nn.Module):
  def __init__(self, vocabilarySize, hiddenSize, output):
    super().__init__()
    self.squential=nn.Sequential(
      nn.Embedding(vocabilarySize, hiddenSize),
      nn.RNN(hiddenSize, output, 10)
    )

  def forward(self, sentance: torch.tensor):
    return self.squential(sentance)


inputSize=len(dataset.tokinizerSentance.tokinizerDict)
outputSize=len(dataset.tokinizerLabel.tokinizerDict)


posModel=PosModel(inputSize,5,outputSize).to(device)

"""#Optimizer and loss"""

def parametersCount(model):
  return sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"model parameters: {parametersCount(posModel):,}")


optimizer=torch.optim.Adam(posModel.parameters(),lr=0.001)
loss=nn.CrossEntropyLoss()

"""#Training"""

class ModelTrainer():
  def __init__(self, model, optimizer, loss, dataset, epochs, device):
    self.model=model
    self.optimizer=optimizer
    self.loss=loss
    self.epochs=epochs
    self.device=device

    self.trainDataloader, self.testDataloader = Dataloader(dataset,0.8).trainTestDataloader()

    self.startTraining()

  def startTraining(self)->None:
    for epoch in tqdm(range(self.epochs)):

      trainGenerator=self.train()
      trainLoss, trainAccuracy=self.unpackGenerator(trainGenerator)
      
      testGenerator=self.test()
      testLoss, testAccuracy=self.unpackGenerator(testGenerator)

      print(f"epoch {epoch} | train loss: {trainLoss:.2f}, train accuracy: {trainAccuracy:.2f} | test loss: {testLoss:.2f}, test accuracy: {testAccuracy:.2f}")

  def train(self):
    for input, target in self.trainDataloader:
      self.optimizer.zero_grad()

      prediction=self.model(input)

      loss, accuracy=self.getLossAndAccuracy(prediction, target)
      loss.requires_grad = True
      loss.backward()

      self.optimizer.step()

      yield loss, accuracy

  def test(self):
    for input, target in self.testDataloader:
      self.optimizer.zero_grad()

      prediction=self.model(input)


      loss, accuracy=self.getLossAndAccuracy(prediction, target)

      yield loss, accuracy

  def unpackGenerator(self, generator):
    generator=next(iter(generator))
    loss, accuracy=generator[0],generator[1]
    return loss, accuracy

  def getLossAndAccuracy(self,prediction,target):

    prediction=prediction[0].argmax(2).float()
    target=target.float()

    prediction_loss=self.loss(prediction,target)
    prediction_acc=self.accuracy(prediction,target)

    return prediction_loss,prediction_acc

  def accuracy(self,predictions,targets):
    assert predictions.shape == targets.shape, "Shapes of predictions and targets must match."

    num_correct = (predictions == targets).sum().item()

    total_samples = targets.numel()
    accuracy_value = num_correct / total_samples
    return accuracy_value*100



ModelTrainer(posModel, optimizer, loss, dataset, 100, device)