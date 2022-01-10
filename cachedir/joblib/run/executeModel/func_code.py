# first line: 473
@memory.cache
# check this issue later because we are not getting the same results
def executeModel(exeCall, flagEx, nodeTransfName):

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
    columnsNames = []
    scores = []

    if (len(exeCall) == 0):
        if (flagEx == 3):
            XDataStored = XData.copy()
        else:
            XData = XDataStored.copy()
            XDataStoredOriginal = XDataStored.copy()
    else:
        if (flagEx == 4):
            XDataStored = XData.copy()
        else:    
            XData = XDataStored.copy()
            XDataStoredOriginal = XDataStored.copy()
    columnsNewGen = keepOriginalFeatures.columns.values.tolist()
    # Bayesian Optimization for 150 iterations
    if (keyFirstTime):
        create_global_function()
        params = {"C": (0.0001, 10000), "gamma": (0.0001, 10000)}
        svc_bayesopt = BayesianOptimization(estimator, params, random_state=RANDOM_SEED)
        svc_bayesopt.maximize(init_points=130, n_iter=20, acq='ucb')
        bestParams = svc_bayesopt.max['params']
        estimator = SVC(C=bestParams.get('C'), gamma=bestParams.get('gamma'), probability=True, random_state=RANDOM_SEED)

    if (len(exeCall) != 0):
        if (flagEx == 1):
            XData = XData.drop(XData.columns[exeCall], axis=1)
            XDataStoredOriginal = XDataStoredOriginal.drop(XDataStoredOriginal.columns[exeCall], axis=1)
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
        elif (flagEx == 4):
            splittedCol = nodeTransfName.split('_')
            XData.rename(columns={ XData.columns[exeCall[0]]: nodeTransfName }, inplace = True)
            currentColumn = columnsNewGen[exeCall[0]]
            subString = currentColumn[currentColumn.find("(")+1:currentColumn.find(")")]
            replacement = currentColumn.replace(subString, nodeTransfName)
            storePositions.append(exeCall[0])
            storeReplacements.append(replacement)
            pos = 0
            for repl in storeReplacements:
                columnsNewGen[storePositions[pos]] = repl
                pos += 1
            if (len(splittedCol) == 1):
                XData[nodeTransfName] = XDataStoredOriginal[nodeTransfName]
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
                    zScore = (XData[nodeTransfName]-XData[nodeTransfName].mean())/XData[nodeTransfName].std()
                    XData[nodeTransfName] = abs(zScore.min()) + zScore
                elif (splittedCol[1] == 'mms'):
                    XData[nodeTransfName] = (XData[nodeTransfName]-XData[nodeTransfName].min())/(XData[nodeTransfName].max()-XData[nodeTransfName].min())
                elif (splittedCol[1] == 'l2'):
                    dfTemp = np.log10(XData[nodeTransfName])
                    if (dfTemp < 0).values.any():
                        XData[nodeTransfName] = abs(dfTemp.min()) + dfTemp
                    else:
                        XData[nodeTransfName] = dfTemp
                elif (splittedCol[1] == 'l1p'):
                    XData[nodeTransfName] = np.log1p(XData[nodeTransfName])
                elif (splittedCol[1] == 'l10'):
                    dfTemp = np.log10(XData[nodeTransfName])
                    if (dfTemp < 0).values.any():
                        XData[nodeTransfName] = abs(dfTemp.min()) + dfTemp
                    else:
                        XData[nodeTransfName] = dfTemp
                elif (splittedCol[1] == 'e2'):
                    XData[nodeTransfName] = np.exp2(XData[nodeTransfName])
                elif (splittedCol[1] == 'em1'):
                    XData[nodeTransfName] = np.expm1(XData[nodeTransfName])
                elif (splittedCol[1] == 'p2'):
                    XData[nodeTransfName] = np.power(XData[nodeTransfName], 2)
                elif (splittedCol[1] == 'p3'):
                    XData[nodeTransfName] = np.power(XData[nodeTransfName], 3)
                else:
                    XData[nodeTransfName] = np.power(XData[nodeTransfName], 4)
            XDataStored = XData.copy()     
            
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
    featureImportanceData = estimatorFeatureSelection(XData, estimator)
    estimator.fit(XData, yData)
    yPredict = estimator.predict(XData)
    yPredictProb = cross_val_predict(estimator, XData, yData, cv=crossValidation, method='predict_proba')
    print(XData)
    num_cores = multiprocessing.cpu_count()
    inputsSc = ['accuracy','precision_macro','recall_macro']

    flat_results = Parallel(n_jobs=num_cores)(delayed(solve)(estimator,XData,yData,crossValidation,item,index) for index, item in enumerate(inputsSc))
    scoresAct = [item for sublist in flat_results for item in sublist]

    howMany = 0

    if (keyFirstTime):
        previousState = scoresAct
        keyFirstTime = False
        howMany = 3
    
    if (((scoresAct[0]-scoresAct[1]) + (scoresAct[2]-scoresAct[3]) + (scoresAct[4]-scoresAct[5])) >= ((previousState[0]-previousState[1]) + (previousState[2]-previousState[3]) + (previousState[4]-previousState[5]))):
        finalResultsData = XData.copy()
        print('improved')

    if (keyFirstTime == False):
        if ((scoresAct[0]-scoresAct[1]) > (previousState[0]-previousState[1])):
            previousState[0] = scoresAct[0]
            previousState[1] = scoresAct[1]
            howMany = howMany + 1
        elif ((scoresAct[2]-scoresAct[3]) > (previousState[2]-previousState[3])):
            previousState[2] = scoresAct[2]
            previousState[3] = scoresAct[3]
            howMany = howMany + 1
        elif ((scoresAct[4]-scoresAct[5]) > (previousState[4]-previousState[5])):
            previousState[4] = scoresAct[4]
            previousState[5] = scoresAct[5]
            howMany = howMany + 1
        else:
            pass

    scores = scoresAct + previousState

    if (howMany == 3):
        scores.append(1)
    else:
        scores.append(0)

    return 'Everything Okay'
