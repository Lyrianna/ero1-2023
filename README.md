# ero1-2023

## Virtual Environment

---

To create the virtual environment containing every packages needed for this APP_ERO to run smoothly, please run the
following commands :

1. Create the venv folder at the root of the project :
   ```python3 -m venv venv/```

2. Launch the venv :  ```source 'venv/bin/activate'```
3. Install all the required packages: ```pip3 install -r requirements.txt```
4. Launch the practical program with the following
   command : ```python ./src/pratical_app/main.py  <"city, country"> [render=True]```

5. To launch the theorical solution to the problem : ```python ./src/theorical_app/main.py```

## Demo

---
To run a demo on Montreal, run the following bash script without running the commands from the "Virtual Environment"
section :
```./demo.sh```

## Arborescence

---
Our project has the following arborescence :

```
ero1-2023
├── src
│   ├── former_solutions
│   ├── practical_app
│   │     ├── cache
│   │     └── __pycache__
│   └── theoric_app
│          ├── cache
│          ├── output_files
│          └── __pycache__
└── tests
```

The main part of the project is in the src folder where you can find 3 different packages:

- The former solutions package which contains all the idea that we tried to implement.
- The practical_app package which contains the EROhic solution
- The theoric_app package which contains the theorical application of the problem