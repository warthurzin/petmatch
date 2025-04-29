import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import io
import os

class PlotManager:
    def __init__(self,  confusion_matrix_path ='./plot/confusion_matrix_images', format_image='png'):
        self.confusion_matrix_path = confusion_matrix_path
        self.format_image = format_image
        self.confusion_matrix_fig = None
        self.confusion_matrix_images = []

    def transform_figure_to_image(self):
        buf = io.BytesIO()
        plt.savefig(buf, format=self.format_image)
        buf.seek(0)
        return buf
        
    def plot_confusion_matrix(self, categories_name, values_by_category, estimated_conditions, evaluated_targets):
        self.categories_name = categories_name
        for idx, category_name in enumerate(self.categories_name):
            if self.confusion_matrix_fig is None:
                 self.confusion_matrix_fig = plt.figure()
            cm = confusion_matrix([evaluated_target[idx] for evaluated_target in evaluated_targets], [estimated_condition[idx] for estimated_condition in estimated_conditions])
            ConfusionMatrixDisplay(cm, display_labels=values_by_category[idx]).plot(ax=plt.gca(), xticks_rotation=35.0)
            plt.title(category_name)
            self.confusion_matrix_images.append(self.transform_figure_to_image())
            self.confusion_matrix_fig = None
    
    def erase_folder(self, folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'Failed to delect {file_path}: {e}')
    
    def save_files_by_folder(self, files_main_name, images, output_folder_path):
        for idx, image_buf in enumerate(images):
            image = Image.open(image_buf)
            image_path = os.path.join(output_folder_path, f"{files_main_name}_{idx+1}.{self.format_image}")
            image.save(image_path)
    
    def save_all_images(self):
        self.erase_folder(self.confusion_matrix_path)
        self.save_files_by_folder('confusion_matrix_images', self.confusion_matrix_images, self.confusion_matrix_path)