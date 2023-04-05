# GMD Project
Group members :
- Léo Taverne
- Clément Couchevellou
- Louis-Vincent Capelli

## Context
Project is available here : https://gitlab.telecomnancy.univ-lorraine.fr/Louis-Vincent.Capelli/gmd_project


Creates, fills and uses full-text indexes from differents sources listed in the 'data' directory using Whoosh python library. 


The goal of the project was to create a integrating system using the mediation approach to get, from a list of symptoms:
- the drugs that could cause them ALL as side_effects
- the drugs that could cure them ALL
- the diseases that could cause them ALL


Since it uses local data sources, the downloading of all the files could take a minute.

## How to use
### Install requirements
```bash
python3 -m pip install -r requirements.txt
```

### Run the program
You need to first run init_index.py to create the indexes.

Then you can run script.py to use the CLI.
```bash
python3 script.py 'symptom1;symptom2;...'
```

![image](https://user-images.githubusercontent.com/96493391/230121818-eeb15b87-4f46-43a2-b45a-092e383d349d.png)


You can also run UI.py to use the GUI.
```bash
python3 UI.py
```
![image](https://user-images.githubusercontent.com/96493391/230121852-867c97e0-36d5-42a5-beb2-1e4130f11c26.png)
