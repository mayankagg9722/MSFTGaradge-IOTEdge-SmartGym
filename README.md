# Smart Gym

Overview: https://youtu.be/0-dl__J98mo

<img src="https://github.com/mayankagg9722/MSFTGaradge-IOTEdge-SmartGym/blob/master/Poster.jpeg" height="280" width="180" >
  
## Description
By coming in contact with the gym equipment, the weight, seat and various other settings are auto adjusted as per the user's body and training plan.
The equipment will also measure the work out details like reps, sets, weights and store in the cloud.
By analysing the pattern, the app will also provide personlised training plan.
On equipping the gym with cameras, user will also get recommendations to improve posture and prevent injuries
As part of the hackathon, based on the skill sets of the team members, idea is to get at least 2 of the above to a POC stage.

## Inspiration
That which is not measured is not improved. Although there are many apps to record and analyse gym workouts, they need user input. By connecting the equipments at the gym, we can democratise having a personal trainer.

## How it will work / How it will be built
By coming in contact with the gym equipment, the weight, seat and various other settings are auto adjusted as per the user's body and training plan.
The equipment will also measure the work out details like reps, sets, weights and store in the cloud.
By analysing the pattern, the app will also provide personlised training plan.
On equipping the gym with cameras, user will also get recommendations to improve posture and prevent injuries
As part of the hackathon, based on the skill sets of the team members, idea is to get at least 2 of the above to a POC stage.


<img src="https://github.com/mayankagg9722/MSFTGaradge-IOTEdge-SmartGym/blob/master/810111557939455914.jpg">
  

## How To  Run Code
- Install Yarn
- Go to the directory of the project and type "yarn watch"
- We have also added the Azure Smart Trainer Bot for the integration of the user interface. You can use Azure Bot by running "python    GymTrainerBot.py" inside the directory of "AzureGymTrainer".

> Or else you can also use the GUI created for this project in the Microsoft Hackathon by opening the folder "edgehack-final-project"
> Install the required modules in the requirements.txt in the local or the conda virtual enviroment.
> Then you can direclty execute the GUI by typing "python main.py" which will run the video through the integration with the Azure Bot.

## Azure Conginitive Service And GUI
We have used the Azure Congnitive Services for the Speech to Text and LUIS integration for the language and the intent analyzation.
GUI is created using the flask and UI bindings are done using socket.io asynchronous queues.

## Working prototype
YouTube Link: https://youtu.be/cdahPdXMMyI
