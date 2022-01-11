# first line: 595
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
