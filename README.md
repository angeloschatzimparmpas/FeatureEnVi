# FeatureEnVi: Visual Analytics for Feature Engineering Using Stepwise Selection and Semi-Automatic Extraction Approaches

This Git repository contains the code that accompanies the research paper "FeatureEnVi: Visual Analytics for Feature Engineering Using Stepwise Selection and Semi-Automatic Extraction Approaches". The details of the experiments and the research outcome are described in [the paper](https://doi.org/10.1109/TVCG.2022.3141040).

**Note:** FeatureEnVi is optimized to work better for standard resolutions (such as 1440p/QHD (Quad High Definition) and 1080p). Any other resolution might need manual adjustment of your browser's zoom level to work properly.

**Note:** The tag `paper-version` matches the implementation at the time of the paper's publication. The current version might look significantly different depending on how much time has passed since then.

**Note:** This software is based on the [XGBoost](https://github.com/dmlc/xgboost) and [Bayesian Optimization](https://github.com/fmfn/BayesianOptimization) libraries. Using the exact same input data, different systems might generate slightly different outputs due to the use of these libraries, and such differences will propagate to our software.

**Note:** As any other software, the code is not bug free. There might be limitations in the views and functionalities of the tool that could be addressed in a future code update.

# Data Sets #
All publicly available data sets used in the paper are in the `data` folder, formatted as comma separated values (csv). 
They are based on the data sets available online from the [UCI Machine Learning Repository](http://archive.ics.uci.edu/ml/index.php): Red Wine Quality, Vehicle Recognition, QSAR Biodegradation, and Iris Flower.

# Requirements #
For the backend:
- [Python 3](https://www.python.org/downloads/) (Version: 3.8.x)
- [Flask](https://palletsprojects.com/p/flask/)
- [MongoDB](https://www.mongodb.com/try/download/community) (Version: 4.x)
- Other packages: `pymongo`, `Flask-PyMongo`, `flask_cors`, `numpy`, `pandas`, `joblib`, `xgboost`, `bayesian-optimization`, `scikit-learn`, `eli5`, and `statsmodels`.

You can install all the backend requirements for Python with the following command:
```
pip install -r requirements.txt
```

For the frontend:
- [Node.js](https://nodejs.org/en/) (including Webpack; to install it, `npm install webpack-dev-server@3.10.3`)

There is no need to install anything further for the frontend (e.g., D3 and Plotly.js), since all modules are in the repository.

For the reproducibility of the first use case, the Red Wine Quality data set should be inserted to MongoDB by using the commands below:
```
# recommendation: use insertMongo script to add a data set in Mongo database
# for Python3
python3 insertMongo.py
```

# Usage #
Below is an example of how you can get FeatureEnVi running using Python and Node.js for the backend and frontend, respectively. The frontend is written in JavaScript/HTML with the help of Vue.js framework, so it could be hosted in any other web server of your preference. The only hard requirement (currently) is that both frontend and backend must be running on the same machine. 
```
# first terminal: hosting the visualization side (client)
# with Node.js
cd frontend
npm install webpack-dev-server@3.10.3
npm run dev
```

```
# second terminal: hosting the computational side (server)
FLASK_APP=run.py flask run
```

Then, open your browser and point it to `localhost:8080`. We recommend using an up-to-date version of Google Chrome.

# Reproducibility of the Results #
The following instructions describe how to reach the results present in Figure 1 of the article. The aforementioned figure is connected with the entire Section 4 (*FeatureEnVi: System Overview and Application*) except for Subsection 4.6, and it is the first use case described in the paper.

**Note:** We used OSX and Google Chrome in all our tests, so we cannot guarantee that it works in other OS or browser. However, since FeatureEnVi is written in JS and Python, it should work in all the most common platforms.

**Tip:** You will have to see a red loading bar on the very top of your browser whenever something is processing.

**Tip:** Our [demonstration video](https://vimeo.com/662536366) also presents the following steps, using the same data set (from 02:12 until 10:05).

- Step 1: Make sure the "Red wine quality" data set is selected (top-left corner), then reload/refresh the `localhost:8080` page open in your browser. **Please note** that the first time you execute the analysis and, consequently, run the hyperparameter search, it might take a few minutes before the XGBoost classifier's hyperparameters have been tuned, using Bayesian Optimization. After the first time, the results are cached and will be re-used to make the process faster.
- Step 2: When *Data Space* is populated with the beeswarm plot, press the *Feature exploration* button that is shown in Figure 1(a), top-left corner.
- Step 3: From the newly-drawn table heatmap view in the panel named as *Feature Selection Techniques* (cf. Figure 3(b)), you have to exclude/deselect the six features at the bottom: *chlorides F2, freeSulDi F10, totalSuDi F5, pH F8, resSu F7, and fixAc F4* features (Figure 3(c) and (e)). To confirm the removal/deactivation of these features, please consider pressing down on the right mouse button in this same view.
- Step 4: We continue by transforming *volAc F1, citAc F6, and sulphates F9* features. Starting with *volAc F1*, you have to click on *F1* in the graph visualization located at *Feature Space Detail* panel, as illustrated in Figure 4(b). 12 transformation options will be available to you; please select *F1\_l2* by clicking this specific node. The same process should be followed for the remaining features. You left-click on *F6* and then choose the *F6\_b* transformation. Finally, *F9* should become *F9\_l10*.
- Step 5: To receive the image shown in Figure 1, you have to switch to the *Feature Generation* mode from the layout panel below the graph visualization in *Feature Space Detail* panel. Initially click F1\_l2 and F6\_b, and wait until the table heatmap view got updated, and then click on *F9\_l10*. **Note that** these features should be highlighted in dark gray color compared to the rest (visible in light gray). At this moment, the table heatmap view should be updated with several newly-proposed combinations of features. To replicate Figure 1(a), you click two times the *Impurity-based FI* for sorting in descending order the features based on this particular technique. On the very top of the table heatmap view, the *F1\_l2xF6\_b* combination should appear. You can activate this combination of features by clicking the black/white striped box for this feature that is exactly below *# Action #* column, as shown in Figure 1(b). It should turn yellow instead of the black/white stripe pattern. 

**Note that:** The position and orientation of the nodes/features in the graph visualization is created with the use of a force-based layout algorithm, thus they do not play any role and are susceptible to change from one to another execution. For more details, please consider reading Subsection 4.4 (especially the paragraph with citation [92]).

**Outcome:** The above process describes how you will be able to reproduce precisely the results presented in Figure 1 of the paper. Thank you for your time!

# Corresponding Author #
For any questions with regard to the implementation or the paper, feel free to contact [Angelos Chatzimparmpas](mailto:angelos.chatzimparmpas@lnu.se).