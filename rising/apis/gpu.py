import GPUtil as GPU

def get_gpu():
    return GPU.getGPUs()[0]
