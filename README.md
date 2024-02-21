# Part of Speech Model

This Jupyter notebook contains a Python implementation of a part-of-speech (POS) tagging model using PyTorch. The model is trained to predict the part of speech for each word in a given sentence.

## Original Source
The original notebook is located at: [Part of Speech Model Notebook](https://colab.research.google.com/drive/1wntZTVBpkuhU7hy60nzog1HbKo6U-71Q)

## Imports
- torch
- json
- re
- numpy
- torch.nn
- torch.utils.data.Dataset, DataLoader
- tqdm
- google.colab.drive

## Data Preparation

### Tokinizer

#### Tokinizer Util

This section contains utility functions for tokenizing the dataset.

### Tokinizer Class

This class provides methods for tokenizing and encoding sentences.

## Dataset

The `PosDataset` class handles loading and processing of the dataset for POS tagging.

## Dataloader

The `Dataloader` class is responsible for splitting the dataset into training and testing sets and creating PyTorch dataloaders.

## Model

The `PosModel` class defines the architecture of the POS tagging model using PyTorch.

## Optimizer and Loss

This section initializes the optimizer and loss function for training the model.

## Training

The `ModelTrainer` class trains the POS tagging model using the provided dataset and evaluates its performance.

## Note
- Ensure to modify the file paths accordingly to load your dataset.
- This notebook assumes the availability of GPU for training. If GPU is not available, the training will be performed on CPU.
- Make sure to have necessary dependencies installed before running the notebook.
- This implementation is provided for educational purposes and can be further extended or optimized as needed.

