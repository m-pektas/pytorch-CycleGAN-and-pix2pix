import os
from data.base_dataset import BaseDataset, get_params, get_transform, get_transform_base
from data.image_folder import make_dataset
from PIL import Image
import pandas as pd
import numpy as np

class AlignedDataset(BaseDataset):
    """A dataset class for paired image dataset.

    It assumes that the directory '/path/to/data/train' contains image pairs in the form of {A,B}.
    During test time, you need to prepare a directory '/path/to/data/test'.
    """

    def __init__(self, opt):
        """Initialize this dataset class.

        Parameters:
            opt (Option class) -- stores all the experiment flags; needs to be a subclass of BaseOptions
        """
        BaseDataset.__init__(self, opt)
        self.dir_AB = os.path.join(opt.dataroot, opt.phase, opt.direction.split("to")[0])  # get the image directory
        self.AB_paths = sorted(make_dataset(self.dir_AB, opt.max_dataset_size))  # get image paths
        assert(self.opt.load_size >= self.opt.crop_size)   # crop_size should be smaller than the size of loaded image
        self.input_nc = self.opt.output_nc if self.opt.direction == 'BtoA' else self.opt.input_nc
        self.output_nc = self.opt.input_nc if self.opt.direction == 'BtoA' else self.opt.output_nc
        
        
        
        csv_path = os.path.join(self.opt.dataroot,"BoxInfos+Targets.csv")
        self.csv = pd.read_csv(csv_path)

    def __getitem__(self, index):
        """Return a data point and its metadata information.

        Parameters:
            index - - a random integer for data indexing

        Returns a dictionary that contains A, B, A_paths and B_paths
            A (tensor) - - an image in the input domain
            B (tensor) - - its corresponding image in the target domain
            A_paths (str) - - image paths
            B_paths (str) - - image paths (same as A_paths)
        """
        # read a image given a random integer index
        A_path = self.AB_paths[index]
        A = Image.open(A_path).convert('RGB')
        
        B_path = A_path.replace(self.opt.direction.split("to")[0],self.opt.direction.split("to")[1])
        B = Image.open(B_path).convert('RGB')
        
        
        try :
            A_name = A_path.split(" ")[-1]
            target_name = self.csv[self.csv["ImageNames"]==A_name]["Targets"].values[0]
            target_path =  os.path.join(self.opt.dataroot,"pool",target_name)
            target = Image.open(target_path).convert('RGB')
        except:
            print("Target image not found !!!")
            target_np = np.random.randn(*(list(A.size)+[3]))
            target = Image.fromarray(target_np.astype("uint8")).convert('RGB')
            
        # split AB image into A and B
        # w, h = AB.size
        # w2 = int(w / 2)
        # A = AB.crop((0, 0, w2, h))
        # B = AB.crop((w2, 0, w, h))

        # apply the same transform to both A and B
        # transform_params = get_params(self.opt, A.size)
        # A_transform = get_transform(self.opt, transform_params, grayscale=(self.input_nc == 1))
        # B_transform = get_transform(self.opt, transform_params, grayscale=(self.output_nc == 1))
        
        transform = get_transform_base()

        A = transform(A)
        B = transform(B)
        target = transform(target)

        return {'A': A, 'B': B, 'A_paths': A_path, 'B_paths': B_path, "target":target}

    def __len__(self):
        """Return the total number of images in the dataset."""
        return len(self.AB_paths)
