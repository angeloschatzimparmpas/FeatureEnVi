# first line: 880
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
