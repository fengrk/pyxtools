# cpu so
- 1.4.0 fail
- 1.2.1 fail

# gpu so

# faiss prebuilt
- 1.4GPU + prebuilt.cpu.so: cpu work


# install pytorch
- install `pip3 install torch torchvision`
- not work

# build
- ref: [faiss install](https://github.com/facebookresearch/faiss/blob/master/INSTALL.md)
- ref: [faiss_prebuilt](https://github.com/onfido/faiss_prebuilt)

# pip install package from conda
- 1.2.1 gpu work
``` 
wget -O faiss_gpu.tar.bz2 https://anaconda.org/pytorch/faiss-gpu/1.2.1/download/linux-64/faiss-gpu-1.2.1-py36_cuda9.1.85_2.tar.bz2
tar xvjf faiss_gpu.tar.bz2 && cp -r lib/python3.6/site-packages/faiss  ~/awsmlenv/lib/python3.6/site-packages/ -R && rm lib/ -R && rm info/ -R

```
- 1.3.0 gpu not work
``` 
wget -O faiss_gpu1.3.0.tar.bz2 https://anaconda.org/pytorch/faiss-gpu/1.3.0/download/linux-64/faiss-gpu-1.3.0-py36_cuda9.1.85_1.tar.bz2
tar xvjf faiss_gpu1.3.0.tar.bz2 && cp -r lib/python3.6/site-packages/faiss  ~/awsmlenv/lib/python3.6/site-packages/ -R && rm lib/ -R && rm info/ -R

# ERROR
# Intel MKL FATAL ERROR: Cannot load libmkl_avx2.so or libmkl_def.so.

# conda
# conda install nomkl
# pip fail: not found nomkl; upgrade mkl; install pytorch; 

```

- 1.4.0 gpu not work
``` 
wget -O faiss_gpu1.4.0.tar.bz2 https://anaconda.org/pytorch/faiss-gpu/1.4.0/download/linux-64/faiss-gpu-1.4.0-py36_cuda9.2.148_1.tar.bz2
tar xvjf faiss_gpu1.4.0.tar.bz2 && cp -r lib/python3.6/site-packages/faiss  ~/awsmlenv/lib/python3.6/site-packages/ -R && rm lib/ -R && rm info/ -R

# ERROR
# Intel MKL FATAL ERROR: Cannot load libmkl_avx2.so or libmkl_def.so.

# conda
# conda install nomkl
# pip fail: not found nomkl; upgrade mkl; install pytorch; 

```

- 1.2.1 gpu cp to ml_tools: not work
``` 
wget -O faiss_gpu.tar.bz2 https://anaconda.org/pytorch/faiss-gpu/1.2.1/download/linux-64/faiss-gpu-1.2.1-py36_cuda9.1.85_2.tar.bz2
tar xvjf faiss_gpu.tar.bz2 && cp -r lib/python3.6/site-packages/faiss  ml_tools/faiss/ -R && rm lib/ -R && rm info/ -R
```