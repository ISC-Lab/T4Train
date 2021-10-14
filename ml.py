#!/usr/bin/env python3
# ============================================================================
""" 
Detailed but concise file description here
"""
# ============================================================================

import os
import sys
import time
import signal
import configparser
from datetime import timedelta

# Data processing
import numpy as np
import json

### SKLEARN Stuff
from sklearn.ensemble import VotingClassifier, VotingRegressor
from sklearn import preprocessing
from sklearn.metrics import confusion_matrix as sk_confusion

### Classifiers
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

### Regressors
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor

### Kfold
from sklearn.model_selection import KFold

# Self-define functions
import utils

from timeloop import Timeloop


def save_model(curr_time):
    global model
    print("ml.py: saving model")
    """Saves model when user presses 'S'."""
    np.save('saved_files/{}/model.npy'.format(curr_time), model)

def init_machine_learning(algo='voting', mode='classifier'):
    """Initializes machine learning algorithm."""

    # Based on algo variable, determines respective classifer and regressor
    if algo=='voting':
        mlpclf=MLPClassifier()
        mlpreg=MLPRegressor()
        svmclf=SVC(kernel='rbf')
        svmreg=SVR(kernel='rbf')
        rfclf =RandomForestClassifier(n_jobs=-1, n_estimators=500)
        rfreg =RandomForestRegressor( n_jobs=-1, n_estimators=500)
        clf   =VotingClassifier(estimators=[('mlp', mlpclf),
                                            ('svm', svmclf),
                                            ('rf' , rfclf)],
                               voting     ='hard')
        reg   =VotingRegressor([('mlp', mlpreg),
                                ('svm', svmreg),
                                ('rf' , rfreg)])
    elif algo=='mlp':
        clf   =MLPClassifier()
        reg   =MLPRegressor()
    elif algo=='svm (linear)':
        clf   =SVC(kernel='linear')
        reg   =SVR(kernel='linear')
    elif algo=='svm (poly)':
        clf   =SVC(kernel='poly')
        reg   =SVR(kernel='poly')
    elif algo=='svm (rbf)':
        clf   =SVC(kernel='rbf')
        reg   =SVR(kernel='rbf')
    elif algo=='rf':
        clf   =RandomForestClassifier(n_jobs=-1, n_estimators=500)
        reg   =RandomForestRegressor( n_jobs=-1, n_estimators=500)
    else:
        clf   =RandomForestClassifier(n_jobs=-1, n_estimators=500)
        reg   =RandomForestRegressor( n_jobs=-1, n_estimators=500)

    # Based on mode specified, returns classifier or regressor
    if mode=='classifier':
        return clf
    if mode=='regressor':
        return reg

def confusion_matrix():
    global tmp_path
    global algos, curr_algo_index, mode

    clf_conf=init_machine_learning(algos[curr_algo_index], mode)
    print("init ml for confusion")
    
    # Load training data
    try:
        training_data  =np.load(tmp_path+'training_data.npy').astype('float')
        training_labels=np.load(tmp_path+'training_labels.npy')
    except Exception as e:
        print(e)
        return
    X_train=[]
    Y_train=[]
    
    # Featurizes the data
    global feat, NUM_BINS, SAMPLE_RATE
    for i in range(0, np.shape(training_data)[0]):
        for j in range(0, np.shape(training_data)[1]):
            tmptrain=training_data[i, j, :, :-2]
            tmptrain=np.ravel(tmptrain)
            tmptrain=utils.featurize(tmptrain, featurization_type=feat, numbins=NUM_BINS, sample_rate=SAMPLE_RATE)
            X_train.append(tmptrain)
            Y_train.append(training_labels[i])

    X =np.array(X_train)[:, :, 0]
    y =np.array(Y_train)

    le=preprocessing.LabelEncoder()
    le.fit(y)
    y =le.transform(y)
    numclasses=len(le.classes_)
    kf=KFold(n_splits=10, shuffle=True)
    kf.get_n_splits(X)
    acc=[]
    cnf=[]
    
    # Test train split
    for train_index, test_index in kf.split(X):
        X_train, X_test=X[train_index], X[test_index]
        y_train, y_test=y[train_index], y[test_index]
        
        clf_conf.fit(X_train, y_train.ravel())   # Trains the model
        tmpacc=clf_conf.score(X_test, y_test)    # Gets the accuracy of the classifier
        y_pred=clf_conf.predict(X_test)          # Classification
        cnf.append(sk_confusion(y_test, y_pred)) # Creates confusion matrix
        acc.append(tmpacc)

    finalacc, finalcnf=[], []
    finalacc.append(np.mean(acc))
    totalcnf=np.sum(cnf, axis=0)

    newcnf=np.copy(totalcnf)
    for i in range(0, numclasses):
        newcnf[i, :]=newcnf[i, :]*100/np.sum(totalcnf[i, :]) # Converts to percentages
    finalcnf.append(newcnf)
    finalcnf=np.mean(finalcnf, axis=0)
    np.savetxt(tmp_path+'confusion_matrix.csv', finalcnf, delimiter=',')

    return

def feature_importances():
    global tmp_path

    # Load training data
    try:
        training_data  =np.load(tmp_path+'training_data.npy').astype(np.float)
        training_labels=np.load(tmp_path+'training_labels.npy')
    except Exception as e:
        print(e)
        return

    X_train=[]
    Y_train=[]
    # featurizes the data
    global feat, NUM_BINS, SAMPLE_RATE
    for i in range(0, np.shape(training_data)[0]):
        for j in range(0, np.shape(training_data)[1]):
            tmptrain=training_data[i, j, :, :-2] # Cut out channel index flags
            tmptrain=utils.featurize(tmptrain, featurization_type=feat, numbins=NUM_BINS, sample_rate=SAMPLE_RATE)
            X_train.append(tmptrain)
            Y_train.append(training_labels[i])

    X_train=np.array(X_train)[:, :, 0]
    Y_train=np.array(Y_train)

    le=preprocessing.LabelEncoder()
    le.fit(Y_train)
    Y_train=le.transform(Y_train)

    model=init_machine_learning('rf', 'classifier') # Initializes the machine learning model learning classifier to rf 
    model.fit(X_train, Y_train) # trains the model
    np.savetxt(tmp_path+'feature_importances.csv', model.feature_importances_, delimiter=',')


def read_message():
    """Handles ML commands written by ui.py."""
    global is_training, is_inferencing
    global curr_algo_index, algos, algo
    global le, model

    global tmp_path

    # Tests to see if the file can be open  
    try:
        f=open(tmp_path+"ml_cmd.txt", "r")
        cmd=f.read()
        f.close()
    except Exception as e:
        return

    # print("ml cmd:", cmd)

    try:
        with open(tmp_path+"feat.txt", "r") as f:
            feat=utils.Featurization(f.read())
    except Exception as e:
        # If no file, assume raw by default
        # print("Error: unable to read featurization method ml.py")
        feat=utils.Featurization.Raw

    if   cmd=='TRAIN':
        is_training    =True
        le             =None
        model          =None
    elif cmd=='FEATURE_IMPORTANCE':
        feature_importances()
    elif cmd.find('TOGGLE_ALGO')>-1:
        curr_algo_index=int(cmd[-1])
        algo           =algos[curr_algo_index]
        model          =None
        is_inferencing =False
        is_training    =False
    elif cmd=='CONFUSION':
        confusion_matrix()
    elif cmd=='STOP PREDICTING':
        is_inferencing =False
    elif cmd=='BYE':
        os._exit(0)
    elif 'SAVE' in cmd:
        curr_time      =cmd.split()[1].strip()
        save_model(curr_time)

    try:
        f=open(tmp_path+"ml_cmd.txt", "w")
        f.write("") 
        f.close()
    except Exception as e:
        return

def receive_interrupt(signum, stack):
    """Catches signals from ui.py and handles ml commands."""
    read_message()

def ml_train():
    """Trains the ml algorithm."""
    global tmp_path
    global feat_from_last_train, feat
    global NUM_BINS, SAMPLE_RATE

    try:
        training_data=np.load(tmp_path+'training_data.npy').astype(np.float)
    except Exception as e:
        print(e)
        return None, None

    if "Camera" not in ds_handler:
        # Cut out channel indices stored in last two cols of all rows
        training_data=training_data[:, :, :, :-2]

    training_labels=np.load(tmp_path+'training_labels.npy')
    X_train=[]
    Y_train=[]

    # Featurizes the data     
    for i in range(0, np.shape(training_data)[0]):
        for j in range(0, np.shape(training_data)[1]):
            tmptrain = training_data[i, j, :, :-2] # cut out columns with channel indices
            tmptrain = utils.featurize(tmptrain, featurization_type=feat, numbins=NUM_BINS, sample_rate=SAMPLE_RATE)
            X_train.append(tmptrain)
            Y_train.append(training_labels[i])
    
    X_train=np.array(X_train)[:, :, 0]
    Y_train=np.array(Y_train)
    
    # print(X_train.shape)
    # print(Y_train.shape)

    le=preprocessing.LabelEncoder()
    le.fit(Y_train)
    Y_train=le.transform(Y_train)
    
    # Initializes machine learning classifier/regressor
    print("ML", algos[curr_algo_index], mode)
    model=init_machine_learning(algos[curr_algo_index], mode)
    # Trains the model
    model.fit(X_train, Y_train) 
    feat_from_last_train=feat

    return [le, model]

def ml_main():
    """Handles training and predicting of ml algorithm."""
    global is_training, is_inferencing
    global le, model, feat_from_last_train
    global tmp_path

    if is_training:
        le, model     =ml_train()
        is_training   =False
        is_inferencing=True
        print("ml.py: DONE training")
    
    if is_inferencing:
        try:
            X_test=np.load(tmp_path+'tmp_frame.npy').astype(np.float)
            assert(X_test.size!=0)
            assert(le is not None)
            assert(model is not None)
        except Exception as e:
            return
        
        # Cut out columns with channel indices
        X_test=X_test[:,:-2] 
        
        X_test=utils.featurize(X_test, featurization_type=feat_from_last_train, numbins=NUM_BINS, sample_rate=SAMPLE_RATE)
        
        # write prediction to file
        prediction=le.inverse_transform(model.predict(X_test.T))
        np.save(tmp_path+'prediction', np.array(prediction))

if __name__=="__main__":
    print('ml.py: Started')

    global tmp_path
    tmp_path="tmp/"
    if sys.platform.startswith('win'):
        tmp_path=os.path.join("tmp", "")
    # tmp_path=""

    # Write PID to file
    pidnum=os.getpid()
    with open(tmp_path+"ml_pidnum.txt", "w") as f:
        f.write(str(pidnum))

    # Clear command txt
    with open(tmp_path+"ml_cmd.txt", "w") as f:
        f.write("")

    # ================================================================
    # Read in configurations
    config=configparser.ConfigParser()
    config.read('config.ini')

    global INSTANCES, FRAME_LENGTH
    global NUM_BINS, SAMPLE_RATE
    global curr_algo_index
    global ds_handler

    INSTANCES      =int(config['GLOBAL']['INSTANCES'      ])  # Number of instances recorded when spacebar is hit
    FRAME_LENGTH   =int(config['GLOBAL']['FRAME_LENGTH'   ])  # Fixed size, need to adjust

    NUM_BINS       =int(config['ML'    ]['NUM_BINS'       ])  # Feturization bins
    SAMPLE_RATE    =int(config['DS'    ]['SAMPLE_RATE'    ])

    DS_HANDLERS    =    config['DS'    ]['DS_HANDLERS'    ][1:-1].split(',')
    DS_FILE_NUM    =int(config['DS'    ]['DS_FILE_NUM'    ])

    curr_algo_index=int(config['GLOBAL']['CURR_ALGO_INDEX'])

    # Get data collection method
    ds_handler     =DS_HANDLERS[DS_FILE_NUM]

    # ================================================================

    global is_training, is_inferencing
    global model, algos
    global algo, mode

    is_training   =False
    is_inferencing=False
    model         =None
    algos         =['voting', 'mlp', 'svm (linear)', 'svm (poly)', 'svm (rbf)', 'rf']

    # Algorithm and mode to run
    algo          =algos[curr_algo_index]
    mode          ='classifier'

    # Set featurization type
    global feat, feat_from_last_train
    feat=utils.Featurization.Variance
    if "Microphone" in ds_handler:
        feat=utils.Featurization.FFT
    if "Camera" in ds_handler:
        feat=utils.Featurization.Raw
    feat_from_last_train=feat

    # # Setup crtl+c catch function
    # signal.signal(signal.SIGINT, receive_interrupt)

    # print("ml.py: Start ml forloop")
    # while True:
    #     ml_main()

    # sys.exit()


    print("ml.py: Start ml forloop")
    if utils.does_support_signals():
        signal.signal(signal.SIGINT, receive_interrupt)

        while True:
            ml_main()
    else:
        timeloop_ml=Timeloop()
        
        # adds timeloop job for checking for ml commans
        @timeloop_ml.job(interval=timedelta(seconds=0.3))
        def read_message_wrapper():
            read_message()

        # adds timeloop job for training and predicting
        @timeloop_ml.job(interval=timedelta(seconds=0.2))
        def ml_main_wrapper():
            ml_main()

        timeloop_ml.start(block=True)

    sys.exit()