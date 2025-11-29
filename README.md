# Group G Final Project - AI Animal and Species Identifier  

<ins> CSC 4444 - Artificial Intelligence with Professor Dong Lao </ins>

This is **Group G's** github repository for our project "Animal+Species Identifier AI Model"

<ins> Team Members </ins>

**Steven Nguyen**  
**Andy Tran**  
**Nathan Soto**  
**Gray Barrow**  
**Kevin Ray**  
**Thomas Shimer**  


## <ins> **Abstract** </ins>

Create/train a Residual Convolutional Neural Network AI model that can take an image from a user, scan it, and accurately guess what animal it is as well as its specific species. The model will be trained on multiple animal image datasets to improve accuracy. We will also develop a web frontend interface/website where users can input images and the AI model will output its guess. If we have enough time, the website will also display an infographic about the inner workings of the model. The collection and preprocessing of the high quality image datasets will take up a large amount of time. Trying to maintain high prediction accuracy across multiple animals and species will be difficult. Connecting the AI-model to the web-based interface will also be a challenge. Since we can’t train our AI model on all the animals and their species due to time and processing power, we could narrow down the list to a reasonable amount of animals/species such as cats, dogs, birds, and lizards. To maintain accuracy, we will tune our model with selected datasets based on the previously mentioned animals instead of using generalized datasets. 


## <ins> **Instructions to run AI MODEL** </ins>

Unfortunately, it was planned to host the backend python AI model on a free website such as railway.app or render.com but the model was too large to be hosted for free. We were able to host a frontend website with netlify but it wouldn't matter since we can't connect the backend. We wanted to simulate real world AI websites. Instead of having to pay, we decided to have a user run the AI model locally on their computer. 

1. Visual Studio Code
2. Download files from github repo or git clone https://github.com/sngu114/CSC-4444-AI-Group-G-Final-Project.git
3. cd CSC-4444-AI-Group-G-Final-Project
4. Recommended to create a virtual environment. 
python -m venv .venv
.\.venv\Scripts\activate
5. Could be run from the VS code terminal. After creating environment, activate it. 
6. Install backend dependencies. (flask, pytorch, tmm, pillow, etc)
cd Model
pip install -r requirements.txt
7. To run the backend flask+ ai model.
enter python app.py
8. Should see lines like "Loading SpeciesClassifier..." etc. etc.
9. Go to frontend.html and click "Go Live" if you have the go live extension where you can see the html live.
10. Python model runs in the back and you can paste in your image on the website and a result will display after the image is processed by the model.

