import os
import shutil
import matplotlib.pyplot as plt

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)

def save_plot_image(fig, folder_path, filename="plot.png"):
    clear_folder(folder_path)
    file_path = os.path.join(folder_path, filename)
    fig.savefig(file_path)
    plt.close(fig)
    return file_path
