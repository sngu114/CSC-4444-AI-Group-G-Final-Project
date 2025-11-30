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

Installations:
1. Python Anaconda (recommended for smoother operations). https://www.anaconda.com/download. Verify install with conda --version.
2. "Live Server" by Ritwick Dey
3. Visual Studio Code

1. Open Visual Studio Code
2. Download files from github repo or do "git clone https://github.com/sngu114/CSC-4444-AI-Group-G-Final-Project.git"
The files are large so cloning will take a nice amount of time to load.
3. Open terminal
4. Create a virtual anaconda environment. "conda create -n (EnterEnvironmentName) python=3.11 -y" then to activate you enter "conda activate (EnterEnvironmentName)"
5. enter "conda install pytorch torchvision cpuonly -c pytorch -y"
6. enter "cd Model" to get into the Model folder.
7. enter "pip install -r requirements.txt".
8. To start the backend flask+ ai model. enter "python app.py" while still under "Model" folder
9. Should see lines like "Loading SpeciesClassifier..." etc. etc.
10. Go to frontend.html under folder "/CSC4444 Frontend" and click the "Go Live" button at the bottom right or right click frontend.html and click "Open with Live Server", a tab will automatically open and you will be able to see the website live.
11. The Python model runs in the back so you can enter in your image on the website and a result will display after the image is processed by the model.

