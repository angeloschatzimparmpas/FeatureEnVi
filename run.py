from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin

import json
import copy
import warnings
import re
import random
import math  
import pandas as pd 
pd.set_option('use_inf_as_na', True)
import numpy as np
import multiprocessing

from joblib import Memory

from xgboost import XGBClassifier
from sklearn import model_selection
from bayes_opt import BayesianOptimization
from sklearn.model_selection import cross_validate
from sklearn.model_selection import cross_val_predict
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import RFECV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

import eli5
from eli5.sklearn import PermutationImportance

from joblib import Parallel, delayed
import multiprocessing

from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

# this block of code is for the connection between the server, the database, and the client (plus routing)

# access MongoDB 
app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/mydb"
mongo = PyMongo(app)

cors = CORS(app, resources={r"/data/*": {"origins": "*"}})

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/Reset', methods=["GET", "POST"])
def reset():
    global DataRawLength
    global DataResultsRaw
    global previousState
    previousState = []\

    global StanceTest
    StanceTest = False

    global filterActionFinal
    filterActionFinal = ''

    global keySpecInternal
    keySpecInternal = 1

    global RANDOM_SEED
    RANDOM_SEED = 42

    global keyData
    keyData = 0

    global keepOriginalFeatures
    keepOriginalFeatures = []

    global XData
    XData = []
    global yData
    yData = []

    global XDataNoRemoval
    XDataNoRemoval = []

    global XDataNoRemovalOrig
    XDataNoRemovalOrig = []

    global XDataStored
    XDataStored = []
    global yDataStored
    yDataStored = []
    
    global finalResultsData
    finalResultsData = []

    global detailsParams
    detailsParams = []

    global algorithmList
    algorithmList = []

    global ClassifierIDsList
    ClassifierIDsList = ''

    global RetrieveModelsList
    RetrieveModelsList = []

    global allParametersPerfCrossMutr
    allParametersPerfCrossMutr = []

    global all_classifiers
    all_classifiers = []

    global crossValidation
    crossValidation = 8
    #crossValidation = 5
    #crossValidation = 3

    global resultsMetrics
    resultsMetrics = []

    global parametersSelData
    parametersSelData = []

    global target_names
    target_names = []

    global keyFirstTime
    keyFirstTime = True

    global target_namesLoc
    target_namesLoc = []

    global featureCompareData
    featureCompareData = []

    global columnsKeep
    columnsKeep = []

    global columnsNewGen
    columnsNewGen = []

    global columnsNames
    columnsNames = []

    global fileName
    fileName = []

    global listofTransformations
    listofTransformations = ["r","b","zs","mms","l2","l1p","l10","e2","em1","p2","p3","p4"]

    return 'The reset was done!'

# retrieve data from client and select the correct data set
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/ServerRequest', methods=["GET", "POST"])
def retrieveFileName():
    global DataRawLength
    global DataResultsRaw
    global DataResultsRawTest
    global DataRawLengthTest
    global DataResultsRawExternal
    global DataRawLengthExternal

    global fileName
    fileName = []
    fileName = request.get_data().decode('utf8').replace("'", '"')

    global keySpecInternal
    keySpecInternal = 1

    global filterActionFinal
    filterActionFinal = ''

    global dataSpacePointsIDs
    dataSpacePointsIDs = []

    global RANDOM_SEED
    RANDOM_SEED = 42

    global keyData
    keyData = 0

    global keepOriginalFeatures
    keepOriginalFeatures = []

    global XData
    XData = []

    global XDataNoRemoval
    XDataNoRemoval = []

    global XDataNoRemovalOrig
    XDataNoRemovalOrig = []

    global previousState
    previousState = []

    global yData
    yData = []

    global XDataStored
    XDataStored = []

    global yDataStored
    yDataStored = []

    global finalResultsData
    finalResultsData = []

    global ClassifierIDsList
    ClassifierIDsList = ''

    global algorithmList
    algorithmList = []

    global detailsParams
    detailsParams = []

    # Initializing models

    global RetrieveModelsList
    RetrieveModelsList = []

    global resultsList
    resultsList = []

    global allParametersPerfCrossMutr
    allParametersPerfCrossMutr = []

    global HistoryPreservation
    HistoryPreservation = []

    global all_classifiers
    all_classifiers = []

    global crossValidation
    crossValidation = 8
    #crossValidation = 5
    #crossValidation = 3

    global parametersSelData
    parametersSelData = []

    global StanceTest
    StanceTest = False

    global target_names
    
    target_names = []

    global keyFirstTime
    keyFirstTime = True

    global target_namesLoc
    target_namesLoc = []

    global featureCompareData
    featureCompareData = []

    global columnsKeep
    columnsKeep = []

    global columnsNewGen
    columnsNewGen = []

    global columnsNames
    columnsNames = []

    global listofTransformations
    listofTransformations = ["r","b","zs","mms","l2","l1p","l10","e2","em1","p2","p3","p4"]

    DataRawLength = -1
    DataRawLengthTest = -1
    data = json.loads(fileName)  
    if data['fileName'] == 'HeartC':
        CollectionDB = mongo.db.HeartC.find()
        target_names.append('Healthy')
        target_names.append('Diseased')
    elif data['fileName'] == 'biodegC':
        StanceTest = True
        CollectionDB = mongo.db.biodegC.find()
        CollectionDBTest = mongo.db.biodegCTest.find()
        CollectionDBExternal = mongo.db.biodegCExt.find()
        target_names.append('Non-biodegr.')
        target_names.append('Biodegr.')
    elif data['fileName'] == 'BreastC':
        CollectionDB = mongo.db.breastC.find()
    elif data['fileName'] == 'DiabetesC':
        CollectionDB = mongo.db.diabetesC.find()
        target_names.append('Negative')
        target_names.append('Positive')
    elif data['fileName'] == 'MaterialC':
        CollectionDB = mongo.db.MaterialC.find()
        target_names.append('Cylinder')
        target_names.append('Disk')
        target_names.append('Flatellipsold')
        target_names.append('Longellipsold')
        target_names.append('Sphere')
    elif data['fileName'] == 'ContraceptiveC':
        CollectionDB = mongo.db.ContraceptiveC.find()
        target_names.append('No-use')
        target_names.append('Long-term')
        target_names.append('Short-term')
    elif data['fileName'] == 'VehicleC':
        CollectionDB = mongo.db.VehicleC.find()
        target_names.append('Van')
        target_names.append('Car')
        target_names.append('Bus')
    elif data['fileName'] == 'WineC':
        CollectionDB = mongo.db.WineC.find()
        target_names.append('Fine')
        target_names.append('Superior')
        target_names.append('Inferior')
    else:
        CollectionDB = mongo.db.IrisC.find()
    DataResultsRaw = []
    for index, item in enumerate(CollectionDB):
        item['_id'] = str(item['_id'])
        item['InstanceID'] = index
        DataResultsRaw.append(item)
    DataRawLength = len(DataResultsRaw)

    DataResultsRawTest = []
    DataResultsRawExternal = []
    if (StanceTest):
        for index, item in enumerate(CollectionDBTest):
            item['_id'] = str(item['_id'])
            item['InstanceID'] = index
            DataResultsRawTest.append(item)
        DataRawLengthTest = len(DataResultsRawTest)
        for index, item in enumerate(CollectionDBExternal):
            item['_id'] = str(item['_id'])
            item['InstanceID'] = index
            DataResultsRawExternal.append(item)
        DataRawLengthExternal = len(DataResultsRawExternal)

    dataSetSelection()
    return 'Everything is okay'

# Retrieve data set from client
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/SendtoSeverDataSet', methods=["GET", "POST"])
def sendToServerData():

    uploadedData = request.get_data().decode('utf8').replace("'", '"')
    uploadedDataParsed = json.loads(uploadedData)
    DataResultsRaw = uploadedDataParsed['uploadedData']

    DataResults = copy.deepcopy(DataResultsRaw)

    for dictionary in DataResultsRaw:
        for key in dictionary.keys():
            if (key.find('*') != -1):
                target = key
                continue
        continue
    DataResultsRaw.sort(key=lambda x: x[target], reverse=True)
    DataResults.sort(key=lambda x: x[target], reverse=True)

    for dictionary in DataResults:
        del dictionary[target]

    global AllTargets
    global target_names
    global target_namesLoc
    AllTargets = [o[target] for o in DataResultsRaw]
    AllTargetsFloatValues = []

    global fileName
    data = json.loads(fileName) 

    previous = None
    Class = 0
    for i, value in enumerate(AllTargets):
        if (i == 0):
            previous = value
            if (data['fileName'] == 'IrisC' or data['fileName'] == 'BreastC'):
                target_names.append(value)
            else:
                pass
        if (value == previous):
            AllTargetsFloatValues.append(Class)
        else:
            Class = Class + 1
            if (data['fileName'] == 'IrisC' or data['fileName'] == 'BreastC'):
                target_names.append(value)
            else:
                pass
            AllTargetsFloatValues.append(Class)
            previous = value

    ArrayDataResults = pd.DataFrame.from_dict(DataResults)

    global XData, yData, RANDOM_SEED
    XData, yData = ArrayDataResults, AllTargetsFloatValues

    global XDataStored, yDataStored
    XDataStored = XData.copy()
    yDataStored = yData.copy()

    global XDataStoredOriginal
    XDataStoredOriginal = XData.copy()

    global finalResultsData
    finalResultsData = XData.copy()

    global XDataNoRemoval 
    XDataNoRemoval = XData.copy()

    global XDataNoRemovalOrig
    XDataNoRemovalOrig = XData.copy()

    return 'Processed uploaded data set'

def dataSetSelection():
    global XDataTest, yDataTest
    XDataTest = pd.DataFrame()
    global XDataExternal, yDataExternal
    XDataExternal = pd.DataFrame()
    global StanceTest
    global AllTargets
    global target_names
    target_namesLoc = []
    if (StanceTest):
        DataResultsTest = copy.deepcopy(DataResultsRawTest)

        for dictionary in DataResultsRawTest:
            for key in dictionary.keys():
                if (key.find('*') != -1):
                    target = key
                    continue
            continue

        DataResultsRawTest.sort(key=lambda x: x[target], reverse=True)
        DataResultsTest.sort(key=lambda x: x[target], reverse=True)

        for dictionary in DataResultsTest:
            del dictionary['_id']
            del dictionary['InstanceID']
            del dictionary[target]

        AllTargetsTest = [o[target] for o in DataResultsRawTest]
        AllTargetsFloatValuesTest = []

        previous = None
        Class = 0
        for i, value in enumerate(AllTargetsTest):
            if (i == 0):
                previous = value
                target_namesLoc.append(value)
            if (value == previous):
                AllTargetsFloatValuesTest.append(Class)
            else:
                Class = Class + 1
                target_namesLoc.append(value)
                AllTargetsFloatValuesTest.append(Class)
                previous = value

        ArrayDataResultsTest = pd.DataFrame.from_dict(DataResultsTest)

        XDataTest, yDataTest = ArrayDataResultsTest, AllTargetsFloatValuesTest

        DataResultsExternal = copy.deepcopy(DataResultsRawExternal)

        for dictionary in DataResultsRawExternal:
            for key in dictionary.keys():
                if (key.find('*') != -1):
                    target = key
                    continue
            continue

        DataResultsRawExternal.sort(key=lambda x: x[target], reverse=True)
        DataResultsExternal.sort(key=lambda x: x[target], reverse=True)

        for dictionary in DataResultsExternal:
            del dictionary['_id']
            del dictionary['InstanceID']
            del dictionary[target]

        AllTargetsExternal = [o[target] for o in DataResultsRawExternal]
        AllTargetsFloatValuesExternal = []

        previous = None
        Class = 0
        for i, value in enumerate(AllTargetsExternal):
            if (i == 0):
                previous = value
                target_namesLoc.append(value)
            if (value == previous):
                AllTargetsFloatValuesExternal.append(Class)
            else:
                Class = Class + 1
                target_namesLoc.append(value)
                AllTargetsFloatValuesExternal.append(Class)
                previous = value

        ArrayDataResultsExternal = pd.DataFrame.from_dict(DataResultsExternal)

        XDataExternal, yDataExternal = ArrayDataResultsExternal, AllTargetsFloatValuesExternal

    DataResults = copy.deepcopy(DataResultsRaw)

    for dictionary in DataResultsRaw:
        for key in dictionary.keys():
            if (key.find('*') != -1):
                target = key
                continue
        continue

    DataResultsRaw.sort(key=lambda x: x[target], reverse=True)
    DataResults.sort(key=lambda x: x[target], reverse=True)

    for dictionary in DataResults:
        del dictionary['_id']
        del dictionary['InstanceID']
        del dictionary[target]

    AllTargets = [o[target] for o in DataResultsRaw]
    AllTargetsFloatValues = []

    global fileName
    data = json.loads(fileName) 

    previous = None
    Class = 0
    for i, value in enumerate(AllTargets):
        if (i == 0):
            previous = value
            if (data['fileName'] == 'IrisC' or data['fileName'] == 'BreastC'):
                target_names.append(value)
            else:
                pass
        if (value == previous):
            AllTargetsFloatValues.append(Class)
        else:
            Class = Class + 1
            if (data['fileName'] == 'IrisC' or data['fileName'] == 'BreastC'):
                target_names.append(value)
            else:
                pass
            AllTargetsFloatValues.append(Class)
            previous = value

    ArrayDataResults = pd.DataFrame.from_dict(DataResults)

    global XData, yData, RANDOM_SEED
    XData, yData = ArrayDataResults, AllTargetsFloatValues

    global keepOriginalFeatures
    global OrignList
    if (data['fileName'] == 'biodegC'):
        keepOriginalFeatures = XData.copy()
        storeNewColumns = []
        for col in keepOriginalFeatures.columns:
            newCol = col.replace("-", "_")
            storeNewColumns.append(newCol.replace("_",""))

        keepOriginalFeatures.columns = [str(col) + ' F'+str(idx+1)+'' for idx, col in enumerate(storeNewColumns)]
        columnsNewGen = keepOriginalFeatures.columns.values.tolist()
        OrignList = keepOriginalFeatures.columns.values.tolist()   
    else:
        keepOriginalFeatures = XData.copy()
        keepOriginalFeatures.columns = [str(col) + ' F'+str(idx+1)+'' for idx, col in enumerate(keepOriginalFeatures.columns)]
        columnsNewGen = keepOriginalFeatures.columns.values.tolist()
        OrignList = keepOriginalFeatures.columns.values.tolist()

    XData.columns = ['F'+str(idx+1) for idx, col in enumerate(XData.columns)]
    XDataTest.columns = ['F'+str(idx+1) for idx, col in enumerate(XDataTest.columns)]
    XDataExternal.columns = ['F'+str(idx+1) for idx, col in enumerate(XDataExternal.columns)]

    global XDataStored, yDataStored
    XDataStored = XData.copy()
    yDataStored = yData.copy()

    global XDataStoredOriginal
    XDataStoredOriginal = XData.copy()

    global finalResultsData
    finalResultsData = XData.copy()

    global XDataNoRemoval 
    XDataNoRemoval = XData.copy()

    global XDataNoRemovalOrig
    XDataNoRemovalOrig = XData.copy()

    warnings.simplefilter('ignore')

    executeModel([], 0, '')
    
    return 'Everything is okay'

def create_global_function():
    global estimator
    location = './cachedir'
    memory = Memory(location, verbose=0)

    # calculating for all algorithms and models the performance and other results
    @memory.cache
    def estimator(n_estimators, eta, max_depth, subsample, colsample_bytree):
        # initialize model
        print('loopingQSAR')
        n_estimators = int(n_estimators)
        max_depth = int(max_depth)
        model = XGBClassifier(n_estimators=n_estimators, eta=eta, max_depth=max_depth, subsample=subsample, colsample_bytree=colsample_bytree, n_jobs=-1, random_state=RANDOM_SEED, silent=True, verbosity = 0, use_label_encoder=False)
        # set in cross-validation
        result = cross_validate(model, XData, yData, cv=crossValidation, scoring='accuracy')
        # result is mean of test_score
        return np.mean(result['test_score'])

# check this issue later because we are not getting the same results
def executeModel(exeCall, flagEx, nodeTransfName):

    global XDataTest, yDataTest
    global XDataExternal, yDataExternal
    global keyFirstTime
    global estimator
    global yPredictProb
    global scores
    global featureImportanceData
    global XData
    global XDataStored
    global previousState
    global columnsNewGen
    global columnsNames
    global listofTransformations
    global XDataStoredOriginal
    global finalResultsData
    global OrignList
    global tracker

    global XDataNoRemoval
    global XDataNoRemovalOrig

    columnsNames = []
    scores = []
    if (len(exeCall) == 0):
        if (flagEx == 3):
            XDataStored = XData.copy()
            XDataNoRemovalOrig = XDataNoRemoval.copy()
            OrignList = columnsNewGen
        elif (flagEx == 2):
            XData = XDataStored.copy()
            XDataStoredOriginal = XDataStored.copy()
            XDataNoRemoval = XDataNoRemovalOrig.copy()
            columnsNewGen = OrignList
        else:
            XData = XDataStored.copy()
            XDataNoRemoval = XDataNoRemovalOrig.copy()
            XDataStoredOriginal = XDataStored.copy()
    else:
        if (flagEx == 4):
            XDataStored = XData.copy()
            XDataNoRemovalOrig = XDataNoRemoval.copy()
            #XDataStoredOriginal = XDataStored.copy()
        elif (flagEx == 2):
            XData = XDataStored.copy()
            XDataStoredOriginal = XDataStored.copy()
            XDataNoRemoval = XDataNoRemovalOrig.copy()
            columnsNewGen = OrignList
        else:    
            XData = XDataStored.copy()
            #XDataNoRemoval = XDataNoRemovalOrig.copy()
            XDataStoredOriginal = XDataStored.copy()

    # Bayesian Optimization CHANGE INIT_POINTS!
    if (keyFirstTime):
        create_global_function()
        params = {"n_estimators": (5, 200), "eta": (0.05, 0.3), "max_depth": (6,12), "subsample": (0.8,1), "colsample_bytree": (0.8,1)}
        bayesopt = BayesianOptimization(estimator, params, random_state=RANDOM_SEED)
        bayesopt.maximize(init_points=20, n_iter=5, acq='ucb') # 20 and 5
        bestParams = bayesopt.max['params']
        estimator = XGBClassifier(n_estimators=int(bestParams.get('n_estimators')), eta=bestParams.get('eta'), max_depth=int(bestParams.get('max_depth')), subsample=bestParams.get('subsample'), colsample_bytree=bestParams.get('colsample_bytree'), probability=True, random_state=RANDOM_SEED, silent=True, verbosity = 0, use_label_encoder=False)
        columnsNewGen = OrignList

    if (len(exeCall) != 0):
        if (flagEx == 1):
            currentColumnsDeleted = []
            for uniqueValue in exeCall:
                currentColumnsDeleted.append(tracker[uniqueValue])
            for column in XData.columns:
                if (column in currentColumnsDeleted):
                    XData = XData.drop(column, axis=1)
                    XDataStoredOriginal = XDataStoredOriginal.drop(column, axis=1)
        elif (flagEx == 2):
            columnsKeepNew = []
            columns = XDataGen.columns.values.tolist()
            for indx, col in enumerate(columns):
                if indx in exeCall:
                    columnsKeepNew.append(col)
                    columnsNewGen.append(col)

            XDataTemp = XDataGen[columnsKeepNew]
            XData[columnsKeepNew] = XDataTemp.values
            XDataStoredOriginal[columnsKeepNew] = XDataTemp.values
            XDataNoRemoval[columnsKeepNew] = XDataTemp.values
        elif (flagEx == 4):
            splittedCol = nodeTransfName.split('_')
            for col in XDataNoRemoval.columns:
                splitCol = col.split('_')
                if ((splittedCol[0] in splitCol[0])):
                    newSplitted = re.sub("[^0-9]", "", splittedCol[0])
                    newCol = re.sub("[^0-9]", "", splitCol[0])
                    if (newSplitted == newCol):
                        storeRenamedColumn = col
            XData.rename(columns={ storeRenamedColumn: nodeTransfName }, inplace = True)
            XDataNoRemoval.rename(columns={ storeRenamedColumn: nodeTransfName }, inplace = True)
            currentColumn = columnsNewGen[exeCall[0]]
            subString = currentColumn[currentColumn.find("(")+1:currentColumn.find(")")]
            replacement = currentColumn.replace(subString, nodeTransfName)
            for ind, column in enumerate(columnsNewGen):
                splitCol = column.split('_')
                if ((splittedCol[0] in splitCol[0])):
                    newSplitted = re.sub("[^0-9]", "", splittedCol[0])
                    newCol = re.sub("[^0-9]", "", splitCol[0])
                    if (newSplitted == newCol):
                        columnsNewGen[ind] = columnsNewGen[ind].replace(storeRenamedColumn, nodeTransfName)
            if (len(splittedCol) == 1):
                XData[nodeTransfName] = XDataStoredOriginal[nodeTransfName]
                XDataNoRemoval[nodeTransfName] = XDataStoredOriginal[nodeTransfName]
            else:
                if (splittedCol[1] == 'r'):
                    XData[nodeTransfName] = XData[nodeTransfName].round()
                elif (splittedCol[1] == 'b'):
                    number_of_bins = np.histogram_bin_edges(XData[nodeTransfName], bins='auto')
                    emptyLabels = []
                    for index, number in enumerate(number_of_bins):
                        if (index == 0):
                            pass
                        else:
                            emptyLabels.append(index)
                    XData[nodeTransfName] = pd.cut(XData[nodeTransfName], bins=number_of_bins, labels=emptyLabels, include_lowest=True, right=True)
                    XData[nodeTransfName] = pd.to_numeric(XData[nodeTransfName], downcast='signed')
                elif (splittedCol[1] == 'zs'):
                    XData[nodeTransfName] = (XData[nodeTransfName]-XData[nodeTransfName].mean())/XData[nodeTransfName].std()
                elif (splittedCol[1] == 'mms'):
                    XData[nodeTransfName] = (XData[nodeTransfName]-XData[nodeTransfName].min())/(XData[nodeTransfName].max()-XData[nodeTransfName].min())
                elif (splittedCol[1] == 'l2'):
                    dfTemp = []
                    dfTemp = np.log2(XData[nodeTransfName])
                    dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
                    dfTemp = dfTemp.fillna(0)
                    XData[nodeTransfName] = dfTemp
                elif (splittedCol[1] == 'l1p'):
                    dfTemp = []
                    dfTemp = np.log1p(XData[nodeTransfName])
                    dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
                    dfTemp = dfTemp.fillna(0)
                    XData[nodeTransfName] = dfTemp       
                elif (splittedCol[1] == 'l10'):
                    dfTemp = []
                    dfTemp = np.log10(XData[nodeTransfName])
                    dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
                    dfTemp = dfTemp.fillna(0)
                    XData[nodeTransfName] = dfTemp
                elif (splittedCol[1] == 'e2'):
                    dfTemp = []
                    dfTemp = np.exp2(XData[nodeTransfName])
                    dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
                    dfTemp = dfTemp.fillna(0)
                    XData[nodeTransfName] = dfTemp
                elif (splittedCol[1] == 'em1'):
                    dfTemp = []
                    dfTemp = np.expm1(XData[nodeTransfName])
                    dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
                    dfTemp = dfTemp.fillna(0)
                    XData[nodeTransfName] = dfTemp
                elif (splittedCol[1] == 'p2'):
                    XData[nodeTransfName] = np.power(XData[nodeTransfName], 2)
                elif (splittedCol[1] == 'p3'):
                    XData[nodeTransfName] = np.power(XData[nodeTransfName], 3)
                else:
                    XData[nodeTransfName] = np.power(XData[nodeTransfName], 4)
                XDataNoRemoval[nodeTransfName] = XData[nodeTransfName]
            XDataStored = XData.copy()
            XDataNoRemovalOrig = XDataNoRemoval.copy()
            
    columnsNamesLoc = XData.columns.values.tolist()

    for col in columnsNamesLoc:
        splittedCol = col.split('_')
        if (len(splittedCol) == 1):
            for tran in listofTransformations:
                columnsNames.append(splittedCol[0]+'_'+tran)
        else:
            for tran in listofTransformations:
                if (splittedCol[1] == tran):
                    columnsNames.append(splittedCol[0])
                else:
                    columnsNames.append(splittedCol[0]+'_'+tran)

    featureImportanceData = estimatorFeatureSelection(XDataNoRemoval, estimator)

    tracker = []
    for value in columnsNewGen:
        value = value.split(' ')
        if (len(value) > 1):
            tracker.append(value[1])
        else:
            tracker.append(value[0])

    estimator.fit(XData, yData)
    yPredict = estimator.predict(XData)
    yPredictProb = cross_val_predict(estimator, XData, yData, cv=crossValidation, method='predict_proba')

    num_cores = multiprocessing.cpu_count()
    inputsSc = ['accuracy','precision_weighted','recall_weighted']

    flat_results = Parallel(n_jobs=num_cores)(delayed(solve)(estimator,XData,yData,crossValidation,item,index) for index, item in enumerate(inputsSc))
    scoresAct = [item for sublist in flat_results for item in sublist]

    #print(scoresAct)

    # if (StanceTest):
    #     y_pred = estimator.predict(XDataTest)
    #     print('Test data set')
    #     print(classification_report(yDataTest, y_pred))

    #     y_pred = estimator.predict(XDataExternal)
    #     print('External data set')
    #     print(classification_report(yDataExternal, y_pred))

    howMany = 0

    if (keyFirstTime):
        previousState = scoresAct
        keyFirstTime = False
        howMany = 3
    
    if (((scoresAct[0]-scoresAct[1]) + (scoresAct[2]-scoresAct[3]) + (scoresAct[4]-scoresAct[5])) >= ((previousState[0]-previousState[1]) + (previousState[2]-previousState[3]) + (previousState[4]-previousState[5]))):
        finalResultsData = XData.copy()

    if (keyFirstTime == False):
        if (((scoresAct[0]-scoresAct[1]) + (scoresAct[2]-scoresAct[3]) + (scoresAct[4]-scoresAct[5])) >= ((previousState[0]-previousState[1]) + (previousState[2]-previousState[3]) + (previousState[4]-previousState[5]))):
            previousState[0] = scoresAct[0]
            previousState[1] = scoresAct[1]
            howMany = 3
        #elif ((scoresAct[2]-scoresAct[3]) > (previousState[2]-previousState[3])):
            previousState[2] = scoresAct[2]
            previousState[3] = scoresAct[3]
            #howMany = howMany + 1
        #elif ((scoresAct[4]-scoresAct[5]) > (previousState[4]-previousState[5])):
            previousState[4] = scoresAct[4]
            previousState[5] = scoresAct[5]
            #howMany = howMany + 1
        #else:
            #pass

    scores = scoresAct + previousState

    if (howMany == 3):
        scores.append(1)
    else:
       scores.append(0)

    return 'Everything Okay'

@app.route('/data/RequestBestFeatures', methods=["GET", "POST"])
def BestFeat():
    global finalResultsData
    finalResultsDataJSON = finalResultsData.to_json()

    response = {    
        'finalResultsData': finalResultsDataJSON
    }
    return jsonify(response)

def featFun (clfLocalPar,DataLocalPar,yDataLocalPar):
    PerFeatureAccuracyLocalPar = []
    scores = model_selection.cross_val_score(clfLocalPar, DataLocalPar, yDataLocalPar, cv=None, n_jobs=-1)
    PerFeatureAccuracyLocalPar.append(scores.mean())
    return PerFeatureAccuracyLocalPar


location = './cachedir'
memory = Memory(location, verbose=0)

# calculating for all algorithms and models the performance and other results
@memory.cache
def estimatorFeatureSelection(Data, clf):

    resultsFS = []
    permList = []
    PerFeatureAccuracy = []
    PerFeatureAccuracyAll = []
    ImpurityFS = []
    RankingFS = []
    estim = clf.fit(Data, yData)

    importances = clf.feature_importances_
    # std = np.std([tree.feature_importances_ for tree in estim.feature_importances_],
    #             axis=0)

    maxList = max(importances)
    minList = min(importances)

    for f in range(Data.shape[1]):
        ImpurityFS.append((importances[f] - minList) / (maxList - minList))

    estim = LogisticRegression(n_jobs = -1, random_state=RANDOM_SEED)

    selector = RFECV(estimator=estim, n_jobs = -1, step=1, cv=crossValidation)
    selector = selector.fit(Data, yData)
    RFEImp = selector.ranking_

    for f in range(Data.shape[1]):
        if (RFEImp[f] == 1):
            RankingFS.append(0.95)
        elif (RFEImp[f] == 2):
            RankingFS.append(0.85)
        elif (RFEImp[f] == 3):
            RankingFS.append(0.75)
        elif (RFEImp[f] == 4):
            RankingFS.append(0.65)
        elif (RFEImp[f] == 5):
            RankingFS.append(0.55)
        elif (RFEImp[f] == 6):
            RankingFS.append(0.45)
        elif (RFEImp[f] == 7):
            RankingFS.append(0.35)
        elif (RFEImp[f] == 8):
            RankingFS.append(0.25)
        elif (RFEImp[f] == 9):
            RankingFS.append(0.15)
        else: 
            RankingFS.append(0.05)

    perm = PermutationImportance(clf, cv=None, refit = True, n_iter = 25).fit(Data, yData)
    permList.append(perm.feature_importances_)
    n_feats = Data.shape[1]

    num_cores = multiprocessing.cpu_count()
    print("Parallelization Initilization")
    flat_results = Parallel(n_jobs=num_cores)(delayed(featFun)(clf,Data.values[:, i].reshape(-1, 1),yData) for i in range(n_feats))
    PerFeatureAccuracy = [item for sublist in flat_results for item in sublist]
    # for i in range(n_feats):
    #     scoresHere = model_selection.cross_val_score(clf, Data.values[:, i].reshape(-1, 1), yData, cv=None, n_jobs=-1)
    #     PerFeatureAccuracy.append(scoresHere.mean())
    PerFeatureAccuracyAll.append(PerFeatureAccuracy)

    clf.fit(Data, yData) 
    yPredict = clf.predict(Data)
    yPredict = np.nan_to_num(yPredict)

    RankingFSDF = pd.DataFrame(RankingFS)
    RankingFSDF = RankingFSDF.to_json()

    ImpurityFSDF = pd.DataFrame(ImpurityFS)
    ImpurityFSDF = ImpurityFSDF.to_json()

    perm_imp_eli5PD = pd.DataFrame(permList)
    if (perm_imp_eli5PD.empty):
        for col in Data.columns:
            perm_imp_eli5PD.append({0:0})
    perm_imp_eli5PD = perm_imp_eli5PD.to_json()

    PerFeatureAccuracyPandas = pd.DataFrame(PerFeatureAccuracyAll)
    PerFeatureAccuracyPandas = PerFeatureAccuracyPandas.to_json()

    bestfeatures = SelectKBest(score_func=f_classif, k='all')
    fit = bestfeatures.fit(Data,yData)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(Data.columns)
    featureScores = pd.concat([dfcolumns,dfscores],axis=1)
    featureScores.columns = ['Specs','Score']  #naming the dataframe columns
    featureScores = featureScores.to_json()

    resultsFS.append(featureScores) 
    resultsFS.append(ImpurityFSDF)
    resultsFS.append(perm_imp_eli5PD) 
    resultsFS.append(PerFeatureAccuracyPandas)
    resultsFS.append(RankingFSDF) 

    return resultsFS

@app.route('/data/sendFeatImp', methods=["GET", "POST"])
def sendFeatureImportance():
    global featureImportanceData

    response = {    
        'Importance': featureImportanceData
    }
    return jsonify(response)

@app.route('/data/sendFeatImpComp', methods=["GET", "POST"])
def sendFeatureImportanceComp():
    global featureCompareData
    global columnsKeep

    response = {    
        'ImportanceCompare': featureCompareData,
        'FeatureNames': columnsKeep
    }
    return jsonify(response)

def solve(sclf,XData,yData,crossValidation,scoringIn,loop):
    scoresLoc = []
    temp = model_selection.cross_val_score(sclf, XData, yData, cv=crossValidation, scoring=scoringIn, n_jobs=-1)

    scoresLoc.append(temp.mean())
    scoresLoc.append(temp.std())

    return scoresLoc

@app.route('/data/sendResults', methods=["GET", "POST"])
def sendFinalResults():
    global scores

    response = {    
        'ValidResults': scores
    }
    return jsonify(response)

def Transformation(quadrant1, quadrant2, quadrant3, quadrant4, quadrant5):

    # XDataNumericColumn = XData.select_dtypes(include='number')
    XDataNumeric = XDataStoredOriginal.select_dtypes(include='number')

    columns = list(XDataNumeric)  

    global packCorrTransformed
    packCorrTransformed = []

    for count, i in enumerate(columns): 
        dicTransf = {}
        
        splittedCol = columnsNames[(count)*len(listofTransformations)+0].split('_')
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf1"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            XDataNumericCopy[i] = XDataNumericCopy[i].round()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf1"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)          
        splittedCol = columnsNames[(count)*len(listofTransformations)+1].split('_')
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf2"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            number_of_bins = np.histogram_bin_edges(XDataNumericCopy[i], bins='auto')
            emptyLabels = []
            for index, number in enumerate(number_of_bins):
                if (index == 0):
                    pass
                else:
                    emptyLabels.append(index)
            XDataNumericCopy[i] = pd.cut(XDataNumericCopy[i], bins=number_of_bins, labels=emptyLabels, include_lowest=True, right=True)
            XDataNumericCopy[i] = pd.to_numeric(XDataNumericCopy[i], downcast='signed')
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf2"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)          
        splittedCol = columnsNames[(count)*len(listofTransformations)+2].split('_')        
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf3"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            XDataNumericCopy[i] = (XDataNumericCopy[i]-XDataNumericCopy[i].mean())/XDataNumericCopy[i].std()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf3"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)          
        splittedCol = columnsNames[(count)*len(listofTransformations)+3].split('_')        
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf4"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            XDataNumericCopy[i] = (XDataNumericCopy[i]-XDataNumericCopy[i].min())/(XDataNumericCopy[i].max()-XDataNumericCopy[i].min())
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf4"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)          
        splittedCol = columnsNames[(count)*len(listofTransformations)+4].split('_')
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf5"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            dfTemp = []
            dfTemp = np.log2(XDataNumericCopy[i])
            dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
            dfTemp = dfTemp.fillna(0)
            XDataNumericCopy[i] = dfTemp
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf5"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        splittedCol = columnsNames[(count)*len(listofTransformations)+5].split('_')
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf6"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            dfTemp = []
            dfTemp = np.log1p(XDataNumericCopy[i])
            dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
            dfTemp = dfTemp.fillna(0)
            XDataNumericCopy[i] = dfTemp
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf6"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        splittedCol = columnsNames[(count)*len(listofTransformations)+6].split('_')
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf7"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            dfTemp = []
            dfTemp = np.log10(XDataNumericCopy[i])
            dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
            dfTemp = dfTemp.fillna(0)
            XDataNumericCopy[i] = dfTemp
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf7"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        splittedCol = columnsNames[(count)*len(listofTransformations)+7].split('_')   
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf8"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            dfTemp = []
            dfTemp = np.exp2(XDataNumericCopy[i])
            dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
            dfTemp = dfTemp.fillna(0)
            XDataNumericCopy[i] = dfTemp
            if (np.isinf(dfTemp.var())):
                flagInf = True
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf8"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        splittedCol = columnsNames[(count)*len(listofTransformations)+8].split('_')   
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf9"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            dfTemp = []
            dfTemp = np.expm1(XDataNumericCopy[i])
            dfTemp = dfTemp.replace([np.inf, -np.inf], np.nan)
            dfTemp = dfTemp.fillna(0)
            XDataNumericCopy[i] = dfTemp
            if (np.isinf(dfTemp.var())):
                flagInf = True
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf9"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        splittedCol = columnsNames[(count)*len(listofTransformations)+9].split('_')   
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf10"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            XDataNumericCopy[i] = np.power(XDataNumericCopy[i], 2)
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf10"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        splittedCol = columnsNames[(count)*len(listofTransformations)+10].split('_')   
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf11"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            XDataNumericCopy[i] = np.power(XDataNumericCopy[i], 3)
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf11"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        splittedCol = columnsNames[(count)*len(listofTransformations)+11].split('_')   
        if(len(splittedCol) == 1):
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf12"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        else:
            d={}
            flagInf = False
            XDataNumericCopy = XDataNumeric.copy()
            XDataNumericCopy[i] = np.power(XDataNumericCopy[i], 4)
            for number in range(1,6):
                quadrantVariable = str('quadrant%s' % number)
                illusion = locals()[quadrantVariable]
                d["DataRows{0}".format(number)] = XDataNumericCopy.iloc[illusion, :]
            dicTransf["transf12"] = NewComputationTransf(d['DataRows1'], d['DataRows2'], d['DataRows3'], d['DataRows4'], d['DataRows5'], quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, i, count, flagInf)
        packCorrTransformed.append(dicTransf)

    return 'Everything Okay'

def NewComputationTransf(DataRows1, DataRows2, DataRows3, DataRows4, DataRows5, quadrant1, quadrant2, quadrant3, quadrant4, quadrant5, feature, count, flagInf):

    corrMatrix1 = DataRows1.corr()
    corrMatrix1 = corrMatrix1.abs()
    corrMatrix2 = DataRows2.corr()
    corrMatrix2 = corrMatrix2.abs()
    corrMatrix3 = DataRows3.corr()
    corrMatrix3 = corrMatrix3.abs()
    corrMatrix4 = DataRows4.corr()
    corrMatrix4 = corrMatrix4.abs()
    corrMatrix5 = DataRows5.corr()
    corrMatrix5 = corrMatrix5.abs()
    corrMatrix1 = corrMatrix1.loc[[feature]]
    corrMatrix2 = corrMatrix2.loc[[feature]]
    corrMatrix3  = corrMatrix3.loc[[feature]]
    corrMatrix4 = corrMatrix4.loc[[feature]]
    corrMatrix5 = corrMatrix5.loc[[feature]]

    DataRows1 = DataRows1.reset_index(drop=True)
    DataRows2 = DataRows2.reset_index(drop=True)
    DataRows3 = DataRows3.reset_index(drop=True)
    DataRows4 = DataRows4.reset_index(drop=True)
    DataRows5 = DataRows5.reset_index(drop=True)

    targetRows1 = [yData[i] for i in quadrant1] 
    targetRows2 = [yData[i] for i in quadrant2] 
    targetRows3 = [yData[i] for i in quadrant3] 
    targetRows4 = [yData[i] for i in quadrant4] 
    targetRows5 = [yData[i] for i in quadrant5] 

    targetRows1Arr = np.array(targetRows1)
    targetRows2Arr = np.array(targetRows2)
    targetRows3Arr = np.array(targetRows3)
    targetRows4Arr = np.array(targetRows4)
    targetRows5Arr = np.array(targetRows5)

    uniqueTarget1 = unique(targetRows1)
    uniqueTarget2 = unique(targetRows2)
    uniqueTarget3 = unique(targetRows3)
    uniqueTarget4 = unique(targetRows4)
    uniqueTarget5 = unique(targetRows5)

    if (len(targetRows1Arr) > 0):
        onehotEncoder1 = OneHotEncoder(sparse=False)
        targetRows1Arr = targetRows1Arr.reshape(len(targetRows1Arr), 1)
        onehotEncoder1 = onehotEncoder1.fit_transform(targetRows1Arr)
        hotEncoderDF1 = pd.DataFrame(onehotEncoder1)
        concatDF1 = pd.concat([DataRows1, hotEncoderDF1], axis=1)
        corrMatrixComb1 = concatDF1.corr()
        corrMatrixComb1 = corrMatrixComb1.abs()
        corrMatrixComb1 = corrMatrixComb1.iloc[:,-len(uniqueTarget1):]
        DataRows1 = DataRows1.replace([np.inf, -np.inf], np.nan)
        DataRows1 = DataRows1.fillna(0)
        X1 = add_constant(DataRows1)
        X1 = X1.replace([np.inf, -np.inf], np.nan)
        X1 = X1.fillna(0)
        VIF1 = pd.Series([variance_inflation_factor(X1.values, i) 
            for i in range(X1.shape[1])], 
            index=X1.columns)
        if (flagInf == False):
            VIF1 = VIF1.replace([np.inf, -np.inf], np.nan)
            VIF1 = VIF1.fillna(0)
            VIF1 = VIF1.loc[[feature]]
        else:
            VIF1 = pd.Series()
        if ((len(targetRows1Arr) > 2) and (flagInf == False)):
            MI1 = mutual_info_classif(DataRows1, targetRows1Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI1List = MI1.tolist()
            MI1List = MI1List[count]
        else:
            MI1List = []
    else:
        corrMatrixComb1 = pd.DataFrame()
        VIF1 = pd.Series()
        MI1List = []

    if (len(targetRows2Arr) > 0):
        onehotEncoder2 = OneHotEncoder(sparse=False)
        targetRows2Arr = targetRows2Arr.reshape(len(targetRows2Arr), 1)
        onehotEncoder2 = onehotEncoder2.fit_transform(targetRows2Arr)
        hotEncoderDF2 = pd.DataFrame(onehotEncoder2)
        concatDF2 = pd.concat([DataRows2, hotEncoderDF2], axis=1)
        corrMatrixComb2 = concatDF2.corr()
        corrMatrixComb2 = corrMatrixComb2.abs()
        corrMatrixComb2 = corrMatrixComb2.iloc[:,-len(uniqueTarget2):]
        DataRows2 = DataRows2.replace([np.inf, -np.inf], np.nan)
        DataRows2 = DataRows2.fillna(0)
        X2 = add_constant(DataRows2)
        X2 = X2.replace([np.inf, -np.inf], np.nan)
        X2 = X2.fillna(0)
        VIF2 = pd.Series([variance_inflation_factor(X2.values, i) 
                for i in range(X2.shape[1])], 
                index=X2.columns)
        if (flagInf == False):
            VIF2 = VIF2.replace([np.inf, -np.inf], np.nan)
            VIF2 = VIF2.fillna(0)
            VIF2 = VIF2.loc[[feature]]
        else:
            VIF2 = pd.Series()
        if ((len(targetRows2Arr) > 2) and (flagInf == False)):
            MI2 = mutual_info_classif(DataRows2, targetRows2Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI2List = MI2.tolist()
            MI2List = MI2List[count]
        else:
            MI2List = []
    else:
        corrMatrixComb2 = pd.DataFrame()
        VIF2 = pd.Series()
        MI2List = []

    if (len(targetRows3Arr) > 0):
        onehotEncoder3 = OneHotEncoder(sparse=False)
        targetRows3Arr = targetRows3Arr.reshape(len(targetRows3Arr), 1)
        onehotEncoder3 = onehotEncoder3.fit_transform(targetRows3Arr)
        hotEncoderDF3 = pd.DataFrame(onehotEncoder3)
        concatDF3 = pd.concat([DataRows3, hotEncoderDF3], axis=1)
        corrMatrixComb3 = concatDF3.corr()
        corrMatrixComb3 = corrMatrixComb3.abs()
        corrMatrixComb3 = corrMatrixComb3.iloc[:,-len(uniqueTarget3):]
        DataRows3 = DataRows3.replace([np.inf, -np.inf], np.nan)
        DataRows3 = DataRows3.fillna(0)
        X3 = add_constant(DataRows3)
        X3 = X3.replace([np.inf, -np.inf], np.nan)
        X3 = X3.fillna(0)
        if (flagInf == False):
            VIF3 = pd.Series([variance_inflation_factor(X3.values, i) 
                    for i in range(X3.shape[1])], 
                    index=X3.columns)
            VIF3 = VIF3.replace([np.inf, -np.inf], np.nan)
            VIF3 = VIF3.fillna(0)
            VIF3 = VIF3.loc[[feature]]
        else:
            VIF3 = pd.Series()
        if ((len(targetRows3Arr) > 2) and (flagInf == False)):
            MI3 = mutual_info_classif(DataRows3, targetRows3Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI3List = MI3.tolist()
            MI3List = MI3List[count]
        else:
            MI3List = []
    else:
        corrMatrixComb3 = pd.DataFrame()
        VIF3 = pd.Series()
        MI3List = []

    if (len(targetRows4Arr) > 0):
        onehotEncoder4 = OneHotEncoder(sparse=False)
        targetRows4Arr = targetRows4Arr.reshape(len(targetRows4Arr), 1)
        onehotEncoder4 = onehotEncoder4.fit_transform(targetRows4Arr)
        hotEncoderDF4 = pd.DataFrame(onehotEncoder4)
        concatDF4 = pd.concat([DataRows4, hotEncoderDF4], axis=1)
        corrMatrixComb4 = concatDF4.corr()
        corrMatrixComb4 = corrMatrixComb4.abs()
        corrMatrixComb4 = corrMatrixComb4.iloc[:,-len(uniqueTarget4):]
        DataRows4 = DataRows4.replace([np.inf, -np.inf], np.nan)
        DataRows4 = DataRows4.fillna(0)
        X4 = add_constant(DataRows4)
        X4 = X4.replace([np.inf, -np.inf], np.nan)
        X4 = X4.fillna(0)
        if (flagInf == False):
            VIF4 = pd.Series([variance_inflation_factor(X4.values, i) 
                    for i in range(X4.shape[1])], 
                    index=X4.columns)
            VIF4 = VIF4.replace([np.inf, -np.inf], np.nan)
            VIF4 = VIF4.fillna(0)
            VIF4 = VIF4.loc[[feature]]
        else:
            VIF4 = pd.Series()
        if ((len(targetRows4Arr) > 2) and (flagInf == False)):
            MI4 = mutual_info_classif(DataRows4, targetRows4Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI4List = MI4.tolist()
            MI4List = MI4List[count]
        else:
            MI4List = []
    else:
        corrMatrixComb4 = pd.DataFrame()
        VIF4 = pd.Series()
        MI4List = []

    if (len(targetRows5Arr) > 0):
        onehotEncoder5 = OneHotEncoder(sparse=False)
        targetRows5Arr = targetRows5Arr.reshape(len(targetRows5Arr), 1)
        onehotEncoder5 = onehotEncoder5.fit_transform(targetRows5Arr)
        hotEncoderDF5 = pd.DataFrame(onehotEncoder5)
        concatDF5 = pd.concat([DataRows5, hotEncoderDF5], axis=1)
        corrMatrixComb5 = concatDF5.corr()
        corrMatrixComb5 = corrMatrixComb5.abs()
        corrMatrixComb5 = corrMatrixComb5.iloc[:,-len(uniqueTarget5):]
        DataRows5 = DataRows5.replace([np.inf, -np.inf], np.nan)
        DataRows5 = DataRows5.fillna(0)
        X5 = add_constant(DataRows5)
        X5 = X5.replace([np.inf, -np.inf], np.nan)
        X5 = X5.fillna(0)
        if (flagInf == False):
            VIF5 = pd.Series([variance_inflation_factor(X5.values, i) 
                    for i in range(X5.shape[1])], 
                    index=X5.columns)
            VIF5 = VIF5.replace([np.inf, -np.inf], np.nan)
            VIF5 = VIF5.fillna(0)
            VIF5 = VIF5.loc[[feature]]
        else:
            VIF5 = pd.Series()
        if ((len(targetRows5Arr) > 2) and (flagInf == False)):
            MI5 = mutual_info_classif(DataRows5, targetRows5Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI5List = MI5.tolist()
            MI5List = MI5List[count]
        else:
            MI5List = []
    else:
        corrMatrixComb5 = pd.DataFrame()
        VIF5 = pd.Series()
        MI5List = []

    if(corrMatrixComb1.empty):
        corrMatrixComb1 = pd.DataFrame()
    else:
        corrMatrixComb1 = corrMatrixComb1.loc[[feature]]
    if(corrMatrixComb2.empty):
        corrMatrixComb2 = pd.DataFrame()
    else:
        corrMatrixComb2 = corrMatrixComb2.loc[[feature]]
    if(corrMatrixComb3.empty):
        corrMatrixComb3 = pd.DataFrame()
    else:
        corrMatrixComb3 = corrMatrixComb3.loc[[feature]]
    if(corrMatrixComb4.empty):
        corrMatrixComb4 = pd.DataFrame()
    else:
        corrMatrixComb4 = corrMatrixComb4.loc[[feature]]
    if(corrMatrixComb5.empty):
        corrMatrixComb5 = pd.DataFrame()
    else:
        corrMatrixComb5 = corrMatrixComb5.loc[[feature]]

    targetRows1ArrDF = pd.DataFrame(targetRows1Arr)
    targetRows2ArrDF = pd.DataFrame(targetRows2Arr)
    targetRows3ArrDF = pd.DataFrame(targetRows3Arr)
    targetRows4ArrDF = pd.DataFrame(targetRows4Arr)
    targetRows5ArrDF = pd.DataFrame(targetRows5Arr)

    concatAllDF1 = pd.concat([DataRows1, targetRows1ArrDF], axis=1)
    concatAllDF2 = pd.concat([DataRows2, targetRows2ArrDF], axis=1)
    concatAllDF3 = pd.concat([DataRows3, targetRows3ArrDF], axis=1)
    concatAllDF4 = pd.concat([DataRows4, targetRows4ArrDF], axis=1)
    concatAllDF5 = pd.concat([DataRows5, targetRows5ArrDF], axis=1)

    corrMatrixCombTotal1 = concatAllDF1.corr()
    corrMatrixCombTotal1 = corrMatrixCombTotal1.abs()
    corrMatrixCombTotal2 = concatAllDF2.corr()
    corrMatrixCombTotal2 = corrMatrixCombTotal2.abs()
    corrMatrixCombTotal3 = concatAllDF3.corr()
    corrMatrixCombTotal3 = corrMatrixCombTotal3.abs()
    corrMatrixCombTotal4 = concatAllDF4.corr()
    corrMatrixCombTotal4 = corrMatrixCombTotal4.abs()
    corrMatrixCombTotal5 = concatAllDF5.corr()
    corrMatrixCombTotal5 = corrMatrixCombTotal5.abs()

    corrMatrixCombTotal1 = corrMatrixCombTotal1.loc[[feature]]
    corrMatrixCombTotal1 = corrMatrixCombTotal1.iloc[:,-1]
    corrMatrixCombTotal2 = corrMatrixCombTotal2.loc[[feature]]
    corrMatrixCombTotal2 = corrMatrixCombTotal2.iloc[:,-1]
    corrMatrixCombTotal3 = corrMatrixCombTotal3.loc[[feature]]
    corrMatrixCombTotal3 = corrMatrixCombTotal3.iloc[:,-1]
    corrMatrixCombTotal4 = corrMatrixCombTotal4.loc[[feature]]
    corrMatrixCombTotal4 = corrMatrixCombTotal4.iloc[:,-1]
    corrMatrixCombTotal5 = corrMatrixCombTotal5.loc[[feature]]
    corrMatrixCombTotal5 = corrMatrixCombTotal5.iloc[:,-1]

    corrMatrixCombTotal1 = pd.concat([corrMatrixCombTotal1.tail(1)])
    corrMatrixCombTotal2 = pd.concat([corrMatrixCombTotal2.tail(1)])
    corrMatrixCombTotal3 = pd.concat([corrMatrixCombTotal3.tail(1)])
    corrMatrixCombTotal4 = pd.concat([corrMatrixCombTotal4.tail(1)])
    corrMatrixCombTotal5 = pd.concat([corrMatrixCombTotal5.tail(1)])

    packCorrLoc = []

    packCorrLoc.append(corrMatrix1.to_json())
    packCorrLoc.append(corrMatrix2.to_json())
    packCorrLoc.append(corrMatrix3.to_json())
    packCorrLoc.append(corrMatrix4.to_json())
    packCorrLoc.append(corrMatrix5.to_json())

    packCorrLoc.append(corrMatrixComb1.to_json())
    packCorrLoc.append(corrMatrixComb2.to_json())
    packCorrLoc.append(corrMatrixComb3.to_json())
    packCorrLoc.append(corrMatrixComb4.to_json())
    packCorrLoc.append(corrMatrixComb5.to_json())

    packCorrLoc.append(corrMatrixCombTotal1.to_json())
    packCorrLoc.append(corrMatrixCombTotal2.to_json())
    packCorrLoc.append(corrMatrixCombTotal3.to_json())
    packCorrLoc.append(corrMatrixCombTotal4.to_json())
    packCorrLoc.append(corrMatrixCombTotal5.to_json())

    packCorrLoc.append(VIF1.to_json())
    packCorrLoc.append(VIF2.to_json())
    packCorrLoc.append(VIF3.to_json())
    packCorrLoc.append(VIF4.to_json())
    packCorrLoc.append(VIF5.to_json())

    packCorrLoc.append(json.dumps(MI1List))
    packCorrLoc.append(json.dumps(MI2List))
    packCorrLoc.append(json.dumps(MI3List))
    packCorrLoc.append(json.dumps(MI4List))
    packCorrLoc.append(json.dumps(MI5List))

    return packCorrLoc

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/thresholdDataSpace', methods=["GET", "POST"])
def Seperation():

    thresholds = request.get_data().decode('utf8').replace("'", '"')
    thresholds = json.loads(thresholds)
    thresholdsPos = thresholds['PositiveValue']
    thresholdsNeg = thresholds['NegativeValue']

    getCorrectPrediction = []

    for index, value in enumerate(yPredictProb):
        getCorrectPrediction.append(value[yData[index]]*100)

    quadrant1 = []
    quadrant2 = []
    quadrant3 = []
    quadrant4 = []
    quadrant5 = []

    probabilityPredictions = []

    for index, value in enumerate(getCorrectPrediction):
        if (value > 50 and value > thresholdsPos):
            quadrant1.append(index)
        elif (value > 50 and value <= thresholdsPos):
            quadrant2.append(index)
        elif (value <= 50 and value > thresholdsNeg):
            quadrant3.append(index)
        else:
            quadrant4.append(index)
        quadrant5.append(index)
        probabilityPredictions.append(value)

    # Main Features
    DataRows1 = XData.iloc[quadrant1, :]
    DataRows2 = XData.iloc[quadrant2, :]
    DataRows3 = XData.iloc[quadrant3, :]
    DataRows4 = XData.iloc[quadrant4, :]
    DataRows5 = XData.iloc[quadrant5, :]


    Transformation(quadrant1, quadrant2, quadrant3, quadrant4, quadrant5)
    
    corrMatrix1 = DataRows1.corr()
    corrMatrix1 = corrMatrix1.abs()
    corrMatrix2 = DataRows2.corr()
    corrMatrix2 = corrMatrix2.abs()
    corrMatrix3 = DataRows3.corr()
    corrMatrix3 = corrMatrix3.abs()
    corrMatrix4 = DataRows4.corr()
    corrMatrix4 = corrMatrix4.abs()
    corrMatrix5 = DataRows5.corr()
    corrMatrix5 = corrMatrix5.abs()

    DataRows1 = DataRows1.reset_index(drop=True)
    DataRows2 = DataRows2.reset_index(drop=True)
    DataRows3 = DataRows3.reset_index(drop=True)
    DataRows4 = DataRows4.reset_index(drop=True)
    DataRows5 = DataRows5.reset_index(drop=True)

    targetRows1 = [yData[i] for i in quadrant1] 
    targetRows2 = [yData[i] for i in quadrant2] 
    targetRows3 = [yData[i] for i in quadrant3] 
    targetRows4 = [yData[i] for i in quadrant4] 
    targetRows5 = [yData[i] for i in quadrant5] 

    targetRows1Arr = np.array(targetRows1)
    targetRows2Arr = np.array(targetRows2)
    targetRows3Arr = np.array(targetRows3)
    targetRows4Arr = np.array(targetRows4)
    targetRows5Arr = np.array(targetRows5)

    uniqueTarget1 = unique(targetRows1)
    uniqueTarget2 = unique(targetRows2)
    uniqueTarget3 = unique(targetRows3)
    uniqueTarget4 = unique(targetRows4)
    uniqueTarget5 = unique(targetRows5)

    if (len(targetRows1Arr) > 0):
        onehotEncoder1 = OneHotEncoder(sparse=False)
        targetRows1Arr = targetRows1Arr.reshape(len(targetRows1Arr), 1)
        onehotEncoder1 = onehotEncoder1.fit_transform(targetRows1Arr)
        hotEncoderDF1 = pd.DataFrame(onehotEncoder1)
        concatDF1 = pd.concat([DataRows1, hotEncoderDF1], axis=1)
        corrMatrixComb1 = concatDF1.corr()
        corrMatrixComb1 = corrMatrixComb1.abs()
        corrMatrixComb1 = corrMatrixComb1.iloc[:,-len(uniqueTarget1):]
        DataRows1 = DataRows1.replace([np.inf, -np.inf], np.nan)
        DataRows1 = DataRows1.fillna(0)
        X1 = add_constant(DataRows1)
        X1 = X1.replace([np.inf, -np.inf], np.nan)
        X1 = X1.fillna(0)
        VIF1 = pd.Series([variance_inflation_factor(X1.values, i) 
            for i in range(X1.shape[1])], 
            index=X1.columns)
        VIF1 = VIF1.replace([np.inf, -np.inf], np.nan)
        VIF1 = VIF1.fillna(0)
        if (len(targetRows1Arr) > 2):
            MI1 = mutual_info_classif(DataRows1, targetRows1Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI1List = MI1.tolist()
        else:
            MI1List = []
    else:
        corrMatrixComb1 = pd.DataFrame()
        VIF1 = pd.Series()
        MI1List = []

    if (len(targetRows2Arr) > 0):
        onehotEncoder2 = OneHotEncoder(sparse=False)
        targetRows2Arr = targetRows2Arr.reshape(len(targetRows2Arr), 1)
        onehotEncoder2 = onehotEncoder2.fit_transform(targetRows2Arr)
        hotEncoderDF2 = pd.DataFrame(onehotEncoder2)
        concatDF2 = pd.concat([DataRows2, hotEncoderDF2], axis=1)
        corrMatrixComb2 = concatDF2.corr()
        corrMatrixComb2 = corrMatrixComb2.abs()
        corrMatrixComb2 = corrMatrixComb2.iloc[:,-len(uniqueTarget2):]
        DataRows2 = DataRows2.replace([np.inf, -np.inf], np.nan)
        DataRows2 = DataRows2.fillna(0)
        X2 = add_constant(DataRows2)
        X2 = X2.replace([np.inf, -np.inf], np.nan)
        X2 = X2.fillna(0)
        VIF2 = pd.Series([variance_inflation_factor(X2.values, i) 
                for i in range(X2.shape[1])], 
                index=X2.columns)
        VIF2 = VIF2.replace([np.inf, -np.inf], np.nan)
        VIF2 = VIF2.fillna(0)
        if (len(targetRows2Arr) > 2):
            MI2 = mutual_info_classif(DataRows2, targetRows2Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI2List = MI2.tolist()
        else:
            MI2List = []
    else:
        corrMatrixComb2 = pd.DataFrame()
        VIF2 = pd.Series()
        MI2List = []

    if (len(targetRows3Arr) > 0):
        onehotEncoder3 = OneHotEncoder(sparse=False)
        targetRows3Arr = targetRows3Arr.reshape(len(targetRows3Arr), 1)
        onehotEncoder3 = onehotEncoder3.fit_transform(targetRows3Arr)
        hotEncoderDF3 = pd.DataFrame(onehotEncoder3)
        concatDF3 = pd.concat([DataRows3, hotEncoderDF3], axis=1)
        corrMatrixComb3 = concatDF3.corr()
        corrMatrixComb3 = corrMatrixComb3.abs()
        corrMatrixComb3 = corrMatrixComb3.iloc[:,-len(uniqueTarget3):]
        DataRows3 = DataRows3.replace([np.inf, -np.inf], np.nan)
        DataRows3 = DataRows3.fillna(0)
        X3 = add_constant(DataRows3)
        X3 = X3.replace([np.inf, -np.inf], np.nan)
        X3 = X3.fillna(0)
        VIF3 = pd.Series([variance_inflation_factor(X3.values, i) 
                for i in range(X3.shape[1])], 
                index=X3.columns)
        VIF3 = VIF3.replace([np.inf, -np.inf], np.nan)
        VIF3 = VIF3.fillna(0)
        if (len(targetRows3Arr) > 2):
            MI3 = mutual_info_classif(DataRows3, targetRows3Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI3List = MI3.tolist()
        else:
            MI3List = []
    else:
        corrMatrixComb3 = pd.DataFrame()
        VIF3 = pd.Series()
        MI3List = []

    if (len(targetRows4Arr) > 0):
        onehotEncoder4 = OneHotEncoder(sparse=False)
        targetRows4Arr = targetRows4Arr.reshape(len(targetRows4Arr), 1)
        onehotEncoder4 = onehotEncoder4.fit_transform(targetRows4Arr)
        hotEncoderDF4 = pd.DataFrame(onehotEncoder4)
        concatDF4 = pd.concat([DataRows4, hotEncoderDF4], axis=1)
        corrMatrixComb4 = concatDF4.corr()
        corrMatrixComb4 = corrMatrixComb4.abs()
        corrMatrixComb4 = corrMatrixComb4.iloc[:,-len(uniqueTarget4):]
        DataRows4 = DataRows4.replace([np.inf, -np.inf], np.nan)
        DataRows4 = DataRows4.fillna(0)
        X4 = add_constant(DataRows4)
        X4 = X4.replace([np.inf, -np.inf], np.nan)
        X4 = X4.fillna(0)
        VIF4 = pd.Series([variance_inflation_factor(X4.values, i) 
                for i in range(X4.shape[1])], 
                index=X4.columns)
        VIF4 = VIF4.replace([np.inf, -np.inf], np.nan)
        VIF4 = VIF4.fillna(0)
        if (len(targetRows4Arr) > 2):
            MI4 = mutual_info_classif(DataRows4, targetRows4Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI4List = MI4.tolist()
        else:
            MI4List = []
    else:
        corrMatrixComb4 = pd.DataFrame()
        VIF4 = pd.Series()
        MI4List = []

    if (len(targetRows5Arr) > 0):
        onehotEncoder5 = OneHotEncoder(sparse=False)
        targetRows5Arr = targetRows5Arr.reshape(len(targetRows5Arr), 1)
        onehotEncoder5 = onehotEncoder5.fit_transform(targetRows5Arr)
        hotEncoderDF5 = pd.DataFrame(onehotEncoder5)
        concatDF5 = pd.concat([DataRows5, hotEncoderDF5], axis=1)
        corrMatrixComb5 = concatDF5.corr()
        corrMatrixComb5 = corrMatrixComb5.abs()
        corrMatrixComb5 = corrMatrixComb5.iloc[:,-len(uniqueTarget5):]
        DataRows5 = DataRows5.replace([np.inf, -np.inf], np.nan)
        DataRows5 = DataRows5.fillna(0)
        X5 = add_constant(DataRows5)
        X5 = X5.replace([np.inf, -np.inf], np.nan)
        X5 = X5.fillna(0)
        VIF5 = pd.Series([variance_inflation_factor(X5.values, i) 
                for i in range(X5.shape[1])], 
                index=X5.columns)
        VIF5 = VIF5.replace([np.inf, -np.inf], np.nan)
        VIF5 = VIF5.fillna(0)
        if (len(targetRows5Arr) > 2):
            MI5 = mutual_info_classif(DataRows5, targetRows5Arr, n_neighbors=3, random_state=RANDOM_SEED)
            MI5List = MI5.tolist()
        else:
            MI5List = []
    else:
        corrMatrixComb5 = pd.DataFrame()
        VIF5 = pd.Series()
        MI5List = []

    targetRows1ArrDF = pd.DataFrame(targetRows1Arr)
    targetRows2ArrDF = pd.DataFrame(targetRows2Arr)
    targetRows3ArrDF = pd.DataFrame(targetRows3Arr)
    targetRows4ArrDF = pd.DataFrame(targetRows4Arr)
    targetRows5ArrDF = pd.DataFrame(targetRows5Arr)

    concatAllDF1 = pd.concat([DataRows1, targetRows1ArrDF], axis=1)
    concatAllDF2 = pd.concat([DataRows2, targetRows2ArrDF], axis=1)
    concatAllDF3 = pd.concat([DataRows3, targetRows3ArrDF], axis=1)
    concatAllDF4 = pd.concat([DataRows4, targetRows4ArrDF], axis=1)
    concatAllDF5 = pd.concat([DataRows5, targetRows5ArrDF], axis=1)

    corrMatrixCombTotal1 = concatAllDF1.corr()
    corrMatrixCombTotal1 = corrMatrixCombTotal1.abs()
    corrMatrixCombTotal2 = concatAllDF2.corr()
    corrMatrixCombTotal2 = corrMatrixCombTotal2.abs()
    corrMatrixCombTotal3 = concatAllDF3.corr()
    corrMatrixCombTotal3 = corrMatrixCombTotal3.abs()
    corrMatrixCombTotal4 = concatAllDF4.corr()
    corrMatrixCombTotal4 = corrMatrixCombTotal4.abs()
    corrMatrixCombTotal5 = concatAllDF5.corr()
    corrMatrixCombTotal5 = corrMatrixCombTotal5.abs()

    corrMatrixCombTotal1 = pd.concat([corrMatrixCombTotal1.tail(1)])
    corrMatrixCombTotal2 = pd.concat([corrMatrixCombTotal2.tail(1)])
    corrMatrixCombTotal3 = pd.concat([corrMatrixCombTotal3.tail(1)])
    corrMatrixCombTotal4 = pd.concat([corrMatrixCombTotal4.tail(1)])
    corrMatrixCombTotal5 = pd.concat([corrMatrixCombTotal5.tail(1)])

    global packCorr
    packCorr = []
    packCorr.append(json.dumps(columnsNewGen))
    packCorr.append(json.dumps(target_names))
    packCorr.append(json.dumps(probabilityPredictions))

    packCorr.append(corrMatrix1.to_json())
    packCorr.append(corrMatrix2.to_json())
    packCorr.append(corrMatrix3.to_json())
    packCorr.append(corrMatrix4.to_json())
    packCorr.append(corrMatrix5.to_json())

    packCorr.append(corrMatrixComb1.to_json())
    packCorr.append(corrMatrixComb2.to_json())
    packCorr.append(corrMatrixComb3.to_json())
    packCorr.append(corrMatrixComb4.to_json())
    packCorr.append(corrMatrixComb5.to_json())

    packCorr.append(corrMatrixCombTotal1.to_json())
    packCorr.append(corrMatrixCombTotal2.to_json())
    packCorr.append(corrMatrixCombTotal3.to_json())
    packCorr.append(corrMatrixCombTotal4.to_json())
    packCorr.append(corrMatrixCombTotal5.to_json())

    packCorr.append(json.dumps(uniqueTarget1))
    packCorr.append(json.dumps(uniqueTarget2))
    packCorr.append(json.dumps(uniqueTarget3))
    packCorr.append(json.dumps(uniqueTarget4))
    packCorr.append(json.dumps(uniqueTarget5))

    packCorr.append(VIF1.to_json())
    packCorr.append(VIF2.to_json())
    packCorr.append(VIF3.to_json())
    packCorr.append(VIF4.to_json())
    packCorr.append(VIF5.to_json())

    packCorr.append(json.dumps(MI1List))
    packCorr.append(json.dumps(MI2List))
    packCorr.append(json.dumps(MI3List))
    packCorr.append(json.dumps(MI4List))
    packCorr.append(json.dumps(MI5List))

    packCorr.append(list(tracker))
    packCorr.append(list(XData.columns.values.tolist()))
    packCorr.append(json.dumps(columnsNames))

    return 'Everything Okay'

@app.route('/data/returnCorrelationsTransformed', methods=["GET", "POST"])
def SendCorrelTransformed():
    global packCorrTransformed

    response = {    
        'correlResulTranformed': packCorrTransformed
    }
    return jsonify(response)

@app.route('/data/returnCorrelations', methods=["GET", "POST"])
def SendCorrel():
    global packCorr

    response = {    
        'correlResul': packCorr
    }
    return jsonify(response)

def unique(list1): 
  
    # intilize a null list 
    unique_list = [] 
      
    # traverse for all elements 
    for x in list1: 
        # check if exists in unique_list or not 
        if x not in unique_list: 
            unique_list.append(x) 
    return unique_list

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/AddRemFun', methods=["GET", "POST"])
def ManipulFeat():
    featureProcess = request.get_data().decode('utf8').replace("'", '"')
    featureProcess = json.loads(featureProcess)
    featureProcessExtract = featureProcess['featureAddRem']
    executeModel(featureProcessExtract, 1, '')
    return 'Okay'

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/AddRemGenFun', methods=["GET", "POST"])
def ManipulFeatGen():
    featureProcess = request.get_data().decode('utf8').replace("'", '"')
    featureProcess = json.loads(featureProcess)
    featureProcessExtract = featureProcess['featureAddRemGen']
    executeModel(featureProcessExtract, 2, '')
    return 'Okay'

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/compareFun', methods=["GET", "POST"])
def CompareFunPy():
    global featureCompareData
    global columnsKeep
    global XDataGen
    global IDsToCompare
    global columnsNewGen

    retrieveComparison = request.get_data().decode('utf8').replace("'", '"')
    retrieveComparison = json.loads(retrieveComparison)
    compareMode = retrieveComparison['compareNumber']
    IDsToCompare = retrieveComparison['getIDs']
    XDataGen = XDataStored.copy()
    columns = XData.columns.values.tolist()
    #columnsOriganl = XDataNoRemoval.columns.values.tolist()

    columnsKeep = []
    columnsKeepNonOrig = []
    columnsKeepID = []
    for indx, col in enumerate(columns):
        if indx in IDsToCompare:
            columnsKeepNonOrig.append(col)
            columnExtracted = re.findall('\d+', col)
            columnsKeep.append(columnsNewGen[int(columnExtracted[0]) - 1])
            columnsKeepID.append(str(col))
    if (compareMode == 1):
        XDataGen = XData[columnsKeepNonOrig]
        feat1 = XDataGen.iloc[:,0]
        feat2 = XDataGen.iloc[:,1]
        XDataGen[columnsKeepID[0]+'+'+columnsKeepID[1]] = feat1 + feat2
        XDataGen['|'+columnsKeepID[0]+'-'+columnsKeepID[1]+'|'] = abs(feat1 - feat2)
        XDataGen[columnsKeepID[0]+'x'+columnsKeepID[1]] = feat1 * feat2
        XDataGen[columnsKeepID[0]+'/'+columnsKeepID[1]] = feat1 / feat2
        XDataGen[columnsKeepID[1]+'/'+columnsKeepID[0]] = feat2 / feat1
        columnsKeep.append(columnsKeepID[0]+'+'+columnsKeepID[1])
        columnsKeep.append('|'+columnsKeepID[0]+'-'+columnsKeepID[1]+'|')
        columnsKeep.append(columnsKeepID[0]+'x'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[0]+'/'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[1]+'/'+columnsKeepID[0])
    elif (compareMode == 2):
        XDataGen = XData[columnsKeepNonOrig]
        feat1 = XDataGen.iloc[:,0]
        feat2 = XDataGen.iloc[:,1]
        feat3 = XDataGen.iloc[:,2]
        XDataGen[columnsKeepID[0]+'+'+columnsKeepID[1]] = feat1 + feat2
        XDataGen[columnsKeepID[1]+'+'+columnsKeepID[2]] = feat2 + feat3
        XDataGen[columnsKeepID[0]+'+'+columnsKeepID[2]] = feat1 + feat3
        XDataGen[columnsKeepID[0]+'+'+columnsKeepID[1]+'+'+columnsKeepID[2]] = feat1 + feat2 + feat3
        XDataGen['|'+columnsKeepID[0]+'-'+columnsKeepID[1]+'|'] = abs(feat1 - feat2)
        XDataGen['|'+columnsKeepID[1]+'-'+columnsKeepID[2]+'|'] = abs(feat2 - feat3)
        XDataGen['|'+columnsKeepID[0]+'-'+columnsKeepID[2]+'|'] = abs(feat1 - feat3)
        XDataGen['|'+columnsKeepID[0]+'-'+columnsKeepID[1]+'-'+columnsKeepID[2]+'|'] = abs(feat1 - feat2 - feat3)
        XDataGen[columnsKeepID[0]+'x'+columnsKeepID[1]] = feat1 * feat2
        XDataGen[columnsKeepID[1]+'x'+columnsKeepID[2]] = feat2 * feat3
        XDataGen[columnsKeepID[0]+'x'+columnsKeepID[2]] = feat1 * feat3
        XDataGen[columnsKeepID[0]+'x'+columnsKeepID[1]+'x'+columnsKeepID[2]] = feat1 * feat2 * feat3
        XDataGen[columnsKeepID[0]+'/'+columnsKeepID[1]] = feat1 / feat2
        XDataGen[columnsKeepID[1]+'/'+columnsKeepID[0]] = feat2 / feat1
        XDataGen[columnsKeepID[1]+'/'+columnsKeepID[2]] = feat2 / feat3
        XDataGen[columnsKeepID[2]+'/'+columnsKeepID[1]] = feat3 / feat2
        XDataGen[columnsKeepID[0]+'/'+columnsKeepID[2]] = feat1 / feat3
        XDataGen[columnsKeepID[2]+'/'+columnsKeepID[0]] = feat3 / feat1
        XDataGen[columnsKeepID[0]+'/'+columnsKeepID[1]+'/'+columnsKeepID[2]] = feat1 / feat2 / feat3
        XDataGen[columnsKeepID[0]+'/'+columnsKeepID[2]+'/'+columnsKeepID[1]] = feat1 / feat3 / feat2
        XDataGen[columnsKeepID[1]+'/'+columnsKeepID[2]+'/'+columnsKeepID[0]] = feat2 / feat3 / feat1
        XDataGen[columnsKeepID[1]+'/'+columnsKeepID[0]+'/'+columnsKeepID[2]] = feat2 / feat1 / feat3
        XDataGen[columnsKeepID[2]+'/'+columnsKeepID[0]+'/'+columnsKeepID[1]] = feat3 / feat1 / feat2
        XDataGen[columnsKeepID[2]+'/'+columnsKeepID[1]+'/'+columnsKeepID[0]] = feat3 / feat2 / feat1

        columnsKeep.append(columnsKeepID[0]+'+'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[1]+'+'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[0]+'+'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[0]+'+'+columnsKeepID[1]+'+'+columnsKeepID[2])
        columnsKeep.append('|'+columnsKeepID[0]+'-'+columnsKeepID[1]+'|')
        columnsKeep.append('|'+columnsKeepID[1]+'-'+columnsKeepID[2]+'|')
        columnsKeep.append('|'+columnsKeepID[0]+'-'+columnsKeepID[2]+'|')
        columnsKeep.append('|'+columnsKeepID[0]+'-'+columnsKeepID[1]+'-'+columnsKeepID[2]+'|')
        columnsKeep.append(columnsKeepID[0]+'x'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[1]+'x'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[0]+'x'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[0]+'x'+columnsKeepID[1]+'x'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[0]+'/'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[1]+'/'+columnsKeepID[0])
        columnsKeep.append(columnsKeepID[1]+'/'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[2]+'/'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[0]+'/'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[2]+'/'+columnsKeepID[0])
        columnsKeep.append(columnsKeepID[0]+'/'+columnsKeepID[1]+'/'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[0]+'/'+columnsKeepID[2]+'/'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[1]+'/'+columnsKeepID[2]+'/'+columnsKeepID[0])
        columnsKeep.append(columnsKeepID[1]+'/'+columnsKeepID[0]+'/'+columnsKeepID[2])
        columnsKeep.append(columnsKeepID[2]+'/'+columnsKeepID[0]+'/'+columnsKeepID[1])
        columnsKeep.append(columnsKeepID[2]+'/'+columnsKeepID[1]+'/'+columnsKeepID[0])
    else:
        pass
    #print(XDataGen)
    XDataGen = XDataGen.replace([np.inf, -np.inf], np.nan)
    XDataGen = XDataGen.fillna(0)
    featureCompareData = estimatorFeatureSelection(XDataGen, estimator)
    return 'Okay'

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/storeGeneratedFeatures', methods=["GET", "POST"])
def storeGeneratedFeat():
    print('Generate')
    executeModel([], 3, '')
    return 'Okay'

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/transformation', methods=["GET", "POST"])
def transformFeatures():
    print('Transform')
    retrieveTransform = request.get_data().decode('utf8').replace("'", '"')
    retrieveTransform = json.loads(retrieveTransform)
    clickedNodeName = retrieveTransform['nameClicked']
    removeNodeID = retrieveTransform['removeNode']
    executeModel([removeNodeID[1]], 4, clickedNodeName[0])
    return 'Okay'

@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
@app.route('/data/testResults', methods=["GET", "POST"])
def requestTestFun():
    global StanceTest
    global estimator
    global XData
    global XDataTest
    global XDataExternal

    # Feature Selection
    XData = XData.drop(['F35','F41','F33','F11','F18','F27','F40','F31','F9','F30','F38','F17','F15','F36','F25','F22', 'F23'], axis=1)
    XDataTest = XDataTest.drop(['F35','F41','F33','F11','F18','F27','F40','F31','F9','F30','F38','F17','F15','F36','F25','F22', 'F23'], axis=1)
    XDataExternal = XDataExternal.drop(['F35','F41','F33','F11','F18','F27','F40','F31','F9','F30','F38','F17','F15','F36','F25','F22', 'F23'], axis=1)

    # Transformation
    XData['F26'] = np.power(XData['F26'], 4)
    XDataTest['F26'] = np.power(XDataTest['F26'], 4)
    XDataExternal['F26'] = np.power(XDataExternal['F26'], 4)

    # XData['F34'] = np.log1p(XData['F34'])
    # XDataTest['F34'] = np.log1p(XDataTest['F34'])
    # XDataExternal['F34'] = np.log1p(XDataExternal['F34'])

    XData['F21'] = np.log1p(XData['F21'])
    XDataTest['F21'] = np.log1p(XDataTest['F21'])
    XDataExternal['F21'] = np.log1p(XDataExternal['F21'])

    XData['F8'] = np.log2(XData['F8'])
    XDataTest['F8'] = np.log2(XDataTest['F8'])
    XDataExternal['F8'] = np.log2(XDataExternal['F8'])

    XData['F3'] = np.log1p(XData['F3'])
    XDataTest['F3'] = np.log1p(XDataTest['F3'])
    XDataExternal['F3'] = np.log1p(XDataExternal['F3'])

    # XData['F12'] = np.power(XData['F12'], 4)
    # XDataTest['F12'] = np.power(XDataTest['F12'], 4)
    # XDataExternal['F12'] = np.power(XDataExternal['F12'], 4)

    XData['F20'] = np.log2(XData['F20'])
    XDataTest['F20'] = np.log2(XDataTest['F20'])
    XDataExternal['F20'] = np.log2(XDataExternal['F20'])

    # XData['F2'] = np.log2(XData['F2'])
    # XDataTest['F2'] = np.log2(XDataTest['F2'])
    # XDataExternal['F2'] = np.log2(XDataExternal['F2'])

    XData['F6'] = np.log1p(XData['F6'])
    XDataTest['F6'] = np.log1p(XDataTest['F6'])
    XDataExternal['F6'] = np.log1p(XDataExternal['F6'])

    XData['F32'] = np.log1p(XData['F32'])
    XDataTest['F32'] = np.log1p(XDataTest['F32'])
    XDataExternal['F32'] = np.log1p(XDataExternal['F32'])

    # XData['F5'] = np.expm1(XData['F5'])
    # XDataTest['F5'] = np.expm1(XDataTest['F5'])
    # XDataExternal['F5'] = np.expm1(XDataExternal['F5'])

    XData['F37'] = np.log2(XData['F37'])
    XDataTest['F37'] = np.log2(XDataTest['F37'])
    XDataExternal['F37'] = np.log2(XDataExternal['F37'])

    # XData['F29'] = np.log1p(XData['F29'])
    # XDataTest['F29'] = np.log1p(XDataTest['F29'])
    # XDataExternal['F29'] = np.log1p(XDataExternal['F29'])

    # XData['F10'] = np.log1p(XData['F10'])
    # XDataTest['F10'] = np.log1p(XDataTest['F10'])
    # XDataExternal['F10'] = np.log1p(XDataExternal['F10'])

    XData['F39'] = np.log2(XData['F39'])
    XDataTest['F39'] = np.log2(XDataTest['F39'])
    XDataExternal['F39'] = np.log2(XDataExternal['F39'])

    # XData['F7'] = np.log1p(XData['F7'])
    # XDataTest['F7'] = np.log1p(XDataTest['F7'])
    # XDataExternal['F7'] = np.log1p(XDataExternal['F7'])

    # XData['F24'] = np.log2(XData['F24'])
    # XDataTest['F24'] = np.log2(XDataTest['F24'])
    # XDataExternal['F24'] = np.log2(XDataExternal['F24'])

    # XData['F13'] = np.power(XData['F13'], 3)
    # XDataTest['F13'] = np.power(XDataTest['F13'], 3)
    # XDataExternal['F13'] = np.power(XDataExternal['F13'], 3)

    # XData['F4'] = np.log1p(XData['F4'])
    # XDataTest['F4'] = np.log1p(XDataTest['F4'])
    # XDataExternal['F4'] = np.log1p(XDataExternal['F4'])

    XData = XData.replace([np.inf, -np.inf], np.nan)
    XData = XData.fillna(0)
    XDataTest = XDataTest.replace([np.inf, -np.inf], np.nan)
    XDataTest = XDataTest.fillna(0)
    XDataExternal = XDataExternal.replace([np.inf, -np.inf], np.nan)
    XDataExternal = XDataExternal.fillna(0)

    # Generation

    # sum_column = XData["F3"] + XData["F39"]
    # XData["Gen1"] = sum_column
    # sum_columnTest = XDataTest["F3"] + XDataTest["F39"]
    # XDataTest["Gen1"] = sum_columnTest
    # sum_columnExt = XDataExternal["F3"] + XDataExternal["F39"]
    # XDataExternal["Gen1"] = sum_columnExt

    sum_column = XData["F7"] + XData["F10"]
    XData["Gen2"] = sum_column
    sum_columnTest = XDataTest["F7"] + XDataTest["F10"]
    XDataTest["Gen2"] = sum_columnTest
    sum_columnExt = XDataExternal["F7"] + XDataExternal["F10"]
    XDataExternal["Gen2"] = sum_columnExt

    sum_column = abs(XData["F2"] - XData["F8"])
    XData["Gen3"] = sum_column
    sum_columnTest = abs(XDataTest["F2"] - XDataTest["F8"])
    XDataTest["Gen3"] = sum_columnTest
    sum_columnExt = abs(XDataExternal["F2"] - XDataExternal["F8"])
    XDataExternal["Gen3"] = sum_columnExt

    # sum_column = XData["F5"] * XData["F26"]
    # XData["Gen4"] = sum_column
    # sum_columnTest = XDataTest["F5"] * XDataTest["F26"]
    # XDataTest["Gen4"] = sum_columnTest
    # sum_columnExt = XDataExternal["F5"] * XDataExternal["F26"]
    # XDataExternal["Gen4"] = sum_columnExt

    # sum_column = XData["F5"] * XData["F12"] * XData["F26"]
    # XData["Gen5"] = sum_column
    # sum_columnTest = XDataTest["F5"] * XDataTest["F12"] * XDataTest["F26"]
    # XDataTest["Gen5"] = sum_columnTest
    # sum_columnExt = XDataExternal["F5"] * XDataExternal["F12"] * XDataExternal["F26"]
    # XDataExternal["Gen5"] = sum_columnExt

    # num_cores = multiprocessing.cpu_count()
    # inputsSc = ['accuracy','precision_weighted','recall_weighted']

    # flat_results = Parallel(n_jobs=num_cores)(delayed(solve)(estimator,XData,yData,crossValidation,item,index) for index, item in enumerate(inputsSc))
    # scoresAct = [item for sublist in flat_results for item in sublist]

    # print(scoresAct)

    estimator.fit(XData, yData)
    if (StanceTest):
        y_pred = estimator.predict(XDataTest)
        print('Test data set')
        print(classification_report(yDataTest, y_pred))

        y_pred = estimator.predict(XDataExternal)
        print('External data set')
        print(classification_report(yDataExternal, y_pred))
    return 'Okay'