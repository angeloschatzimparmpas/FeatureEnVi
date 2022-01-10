# first line: 447
@memory.cache
def create_global_function():
    global estimator
    def estimator(C, gamma):
        # initialize model
        model = SVC(C=C, gamma=gamma, degree=1, random_state=RANDOM_SEED)
        # set in cross-validation
        result = cross_validate(model, XData, yData, cv=crossValidation)
        # result is mean of test_score
        return np.mean(result['test_score'])
