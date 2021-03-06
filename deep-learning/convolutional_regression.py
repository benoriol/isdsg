"""
@author: Benet Oriol
@license: MIT-license
"""

import random
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

import cv2

import time

# TRAIN_FOLDER = 'data/201811151325' # 1000
# TRAIN_FOLDER = 'data/201811151625' # 50
TRAIN_FOLDER = 'data/201811151751' # 5000
# VALID_FOLDER = 'data/201811151328' # 200
VALID_FOLDER = 'data/201811151325' # 1000

BATCH_SIZE = 20
N_EPOCHS = 10


class DataLoader:
    def __init__(self, metadata_path, device, shuffle=False):

        self.subpath = '/'.join(metadata_path.split('/')[:-1])

        self.metadata = [x[:-1].split(' ') for x in open(metadata_path)]

        self.device = device
        if shuffle:
            random.shuffle(self.metadata)

    def get_len(self):
        return len(self.metadata)

    def get_batch(self, size):

        src_batch = -1
        tgt_batch = -1


        for i, x in enumerate(self.metadata):

            if i == 0:
                tgt_batch = torch.tensor(float(x[2])).unsqueeze(0).unsqueeze(0).float()
                tgt_batch = tgt_batch.to(self.device)
                path = self.subpath + '/' + x[0]
                src_batch = torch.from_numpy(cv2.imread(path) / 255).permute(2, 0, 1).unsqueeze(0).float()
                src_batch = src_batch.to(self.device)
                self.metadata = self.metadata[1:]
            else:

                tgt_value = torch.tensor(float(x[2])).unsqueeze(0).unsqueeze(0).float()
                tgt_value = tgt_value.to(self.device)
                srcim = torch.from_numpy(cv2.imread(self.subpath + '/' + x[0])/255).permute(2, 0, 1).unsqueeze(0).float()
                srcim = srcim.to(self.device)
                tgt_batch = torch.cat((tgt_batch, tgt_value))
                src_batch = torch.cat((src_batch, srcim))
                self.metadata = self.metadata[1:]


            if i == size - 1:
                break
        return src_batch, tgt_batch


def error(prediction, target):

    return torch.mean(torch.abs(prediction - target)/target)

def validate(model, metadata_path, device):



    dataloader = DataLoader(metadata_path, device)
    src_batch, tgt_batch = dataloader.get_batch(BATCH_SIZE)
    tgt_batch /= 1000

    err = torch.tensor(0).float().to(device)
    n = 0

    while type(src_batch) != type(-1):
        with torch.no_grad():
            prediction = model(src_batch)

        err += error(prediction, tgt_batch)
        n += 1
        src_batch, tgt_batch = dataloader.get_batch(BATCH_SIZE)
        tgt_batch /= 1000

        optimizer.zero_grad()

    del src_batch
    del tgt_batch
    del dataloader

    return err/n




class Convnet(nn.Module):
    def __init__(self):
        super(Convnet, self).__init__()
        # Start
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU())
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 16, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU())
        self.layer3 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        # out size is 230 * 350


        # Level2
        self.layer4 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU())
        self.layer5 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU())
        self.layer6 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )

        # out size is 32 * 116 * 175
        # Level3
        self.layer7 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU())
        self.layer8 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU())
        self.layer9 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            # nn.MaxPool2d(kernel_size=2, stride=2)
        )

        # out size is 64 * 58 * 87


        # Level4
        self.layer10 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU())
        self.layer11 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU())
        self.layer12 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            #nn.MaxPool2d(kernel_size=2, stride=2)
        )

        # out size is 128 * 29 * 43


        self.denselayers = nn.Sequential(
            nn.Linear(32 * 116 * 175, 200),
            nn.ReLU(),
            nn.Linear(200, 200),
            nn.ReLU(),
            nn.Linear(200, 200),
            nn.ReLU(),
            nn.Linear(200, 200),
            nn.ReLU(),
            nn.Linear(200, 200),
            nn.ReLU(),
            nn.Linear(200, 1)
            )




    def forward(self, inp):

        out = self.layer1(inp)
        out = self.layer2(out)
        out = self.layer3(out)

        out = self.layer4(out)
        out = self.layer5(out)
        out = self.layer6(out)

        out = self.layer7(out)
        out = self.layer8(out)
        out = self.layer9(out)

        # out = self.layer10(out)
        # out = self.layer11(out)
        # out = self.layer12(out)

        out = out.reshape(out.size(0), -1)
        out = self.denselayers(out)



        return out

if __name__ == '__main__':

    device = torch. device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print('device', device)
    model = Convnet().to(device)

    loss_mse = nn.MSELoss()

    optimizer = optim.SGD(model.parameters(), lr=0.0005, momentum=0.5)

    train_metadata_path = TRAIN_FOLDER + '/metadata.txt'
    valid_metadata_path = VALID_FOLDER + '/metadata.txt'

    start_time = time.time()

    for i in (range(N_EPOCHS)):

        dataloader = DataLoader(train_metadata_path, device, shuffle=True)

        pbar = tqdm(total=dataloader.get_len())

        src_batch, tgt_batch = dataloader.get_batch(BATCH_SIZE)
        tgt_batch = tgt_batch/1000
        with torch.no_grad():
            err = torch.tensor(0).float().to(device)
        n = 0


        while type(src_batch) != type(-1):

            prediction = model(src_batch)

            loss = loss_mse(prediction, tgt_batch)
            err += error(prediction, tgt_batch)
            n += 1

            optimizer.zero_grad()

            loss.backward()

            optimizer.step()

            src_batch, tgt_batch = dataloader.get_batch(BATCH_SIZE)
            tgt_batch /= 1000

            pbar.update(BATCH_SIZE)


        del src_batch
        del tgt_batch
        del dataloader



        valid_error = validate(model, valid_metadata_path, device)
        print(('epoch n: ' + str(i + 1)))
        print('train MSE:' + str((err/n).item()).format())
        print('valid MSE:' + str((valid_error).item()))

        elapsed = time.time() - start_time
        # print('time spent: ' + str(elapsed) + '  time remaining: ' + str(elapsed/(i+1)*N_EPOCHS-elapsed))

    print('trained with 5000, eval with 1000')
    cp_name = 'models/convregression1-pt'
    print('Saving checkpoint to: ' + cp_name)
    torch.save(model, cp_name)
