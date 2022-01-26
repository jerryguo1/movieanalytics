# -*- coding: utf-8 -*-
"""data_project_ML_models_final_version_12_12_2021.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13Nx2OJRncSaZWSd3gw7drGOOKrBp1EIh

## Data preparation
"""

import pandas as pd
imdb = pd.read_csv('movies.csv')

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

imdb = imdb.astype({'name': 'string', 'rating':'string','genre':'string', 'released':'string','director':'string','writer':'string','star':'string','country':'string','company':'string',})
# drop any row with nan values
imdb =imdb.dropna()
imdb[['released_date','released_country']] = imdb['released'].str.slice(stop=-1).str.split(" \(",n=1,expand = True)
imdb['genre'] = imdb['genre'].str.lower()
imdb.drop('released',axis=1,inplace=True)
imdb['released_date'] = pd.to_datetime(imdb['released_date'])#,format="%B %d, %Y")
imdb['released_month'] = imdb['released_date'].dt.month
imdb['released_day'] = imdb['released_date'].dt.day
imdb['released_year'] = imdb['released_date'].dt.year
imdb['released_day_of_week'] = imdb['released_date'].dt.dayofweek
imdb['GBratio'] = imdb["gross"]/imdb["budget"]

# (gross - budget )/ budget is bigger than 20%  we call successful
imdb['success'] =imdb['GBratio']>1.2

""" Get popular directors, actors, actresses from IMDB"""

from bs4 import BeautifulSoup
import requests
import math
def get_popular_director_list():
    url = "https://www.imdb.com/list/ls026411399/?sort=list_order,asc&mode=detail"
    response = requests.get(url)

    results_page = BeautifulSoup(response.content)
    temp =results_page.find('span',{"class":"pagination-range"}).get_text()
    last_page_temp = temp.strip().split(' ')
    last_page_number = math.ceil(int(last_page_temp[4])/int(last_page_temp[2]))
    
    director_list = list()
    for i in range(last_page_number):
        durl = url+"&page="+str(i+1)
        response = requests.get(durl)
        soup = BeautifulSoup(response.text)
        director_list_temp=[j.find('a').get_text()[1:].replace('\n','') for j in soup.find_all('h3',{"class":"lister-item-header"})]
        director_list.extend(director_list_temp)
    return director_list

from bs4 import BeautifulSoup
import requests
import math
def get_popular_actor_list():
    url = "https://www.imdb.com/list/ls022928819/?sort=list_order,asc&mode=detail"
    response = requests.get(url)

    results_page = BeautifulSoup(response.content)
    temp =results_page.find('span',{"class":"pagination-range"}).get_text()
    last_page_temp = temp.strip().split(' ')
    last_page_number = math.ceil(int(last_page_temp[4])/int(last_page_temp[2]))
    
    actor_list = list()
    for i in range(last_page_number):
        acturl = url+"&page="+str(i+1)
        response = requests.get(acturl)
        soup = BeautifulSoup(response.text)
        actor_list_temp=[j.find('a').get_text()[1:].replace('\n','') for j in soup.find_all('h3',{"class":"lister-item-header"})]
        actor_list.extend(actor_list_temp)
        
    return actor_list

from bs4 import BeautifulSoup
import requests
import math
def get_popular_actress_list():
    url = "https://www.imdb.com/list/ls022928836/?sort=list_order,asc&mode=detail"
    response = requests.get(url)

    results_page = BeautifulSoup(response.content)
    temp =results_page.find('span',{"class":"pagination-range"}).get_text()
    last_page_temp = temp.strip().split(' ')
    last_page_number = math.ceil(int(last_page_temp[4])/int(last_page_temp[2]))
    actress_list = list()
    for i in range(last_page_number):
        actrssurl = url+"&page="+str(i+1)
        response = requests.get(actrssurl)
        soup = BeautifulSoup(response.text)
        actress_list_temp=[j.find('a').get_text()[1:].replace('\n','') for j in soup.find_all('h3',{"class":"lister-item-header"})]
        actress_list.extend(actress_list_temp)
    return actress_list

# we choose top 200 popular directors from popular director list, and categorize our directors in our dataset into popular and popular directors
# likewise, we do this for popular actors and actresses. 

popular_directors = get_popular_director_list()[:200]
star_list = get_popular_actor_list()[:200] + get_popular_actress_list()[:200]

imdb['director_popularity'] = np.array([1 if i in popular_directors else 0 for i in imdb.director])
imdb['star_popularity'] = np.array([1 if i in star_list else 0 for i in imdb.star])

imdb.drop(['director','star','gross','budget'],axis=1,inplace=True)

imdb

# Commented out IPython magic to ensure Python compatibility.
from sklearn.metrics import r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import scale
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
# statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf

from group_lasso.utils import extract_ohe_groups
# %matplotlib inline
np.random.seed(42)

# drop released_year because we cant go back. also drop score, votes because these are consequence once a movie is released
# imdb_temp_bf_le is the dataset for Machine learning before labelencoding
imdb_temp_bf_le =  imdb.drop(['name', 'score', 'votes', 'year','released_year', 'writer', 'released_date'], inplace = False, axis=1)
imdb_temp_bf_le.info()

# imdb_temp_bf_le

"""Labelencoding Mapping"""

from sklearn import preprocessing
le = preprocessing.LabelEncoder()
le.fit(imdb['rating'])
le_name_mapping_rating = dict(zip(le.classes_, le.transform(le.classes_)))
le.fit(imdb['genre'])
le_name_mapping_genre = dict(zip(le.classes_, le.transform(le.classes_)))
le.fit(imdb['country'])
le_name_mapping_country = dict(zip(le.classes_, le.transform(le.classes_)))
le.fit(imdb['company'])
le_name_mapping_company = dict(zip(le.classes_, le.transform(le.classes_)))
le.fit(imdb['released_country'])
le_name_mapping_released_country = dict(zip(le.classes_, le.transform(le.classes_)))
day_of_week_mapping = {'Monday':0, 'Tuesday':1, 'Wednesday': 2, 'Thursday':3, 'Friday': 4, 'Saturday': 5, 'Sunday':6}

"""## Label Encoder and one-hot encoding"""

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

imdb['rating'] = le.fit_transform(imdb['rating'])
imdb['genre'] = le.fit_transform(imdb['genre'])
imdb['country'] = le.fit_transform(imdb['country'])
imdb['company'] = le.fit_transform(imdb['company'])
imdb['released_country'] = le.fit_transform(imdb['released_country'])

categorical_column = ['rating','genre','country','company', 'released_country','director_popularity','star_popularity']
non_categorical_column =['runtime','released_month','released_day','released_day_of_week']
# imdb_temp_af_le is the dataset we use for machine learning after label encoding
imdb_temp_af_le =  imdb.drop(['name', 'score', 'votes', 'year','released_year', 'writer', 'released_date'], inplace = False, axis=1)

x = imdb_temp_af_le.loc[:,categorical_column +non_categorical_column]

x = imdb_temp_af_le.loc[:,categorical_column+non_categorical_column]

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer, make_column_transformer

#The code below makes a column transformer object that scales the non-categorical columns
# and one hot encodes the categorical columns
preprocess = make_column_transformer((StandardScaler(),non_categorical_column), 
    (OneHotEncoder(categories="auto",drop=
                   'first'), categorical_column)

)

#The next step prepares the independent variables
X = preprocess.fit_transform(x).toarray()
y1 = imdb['GBratio']

# imdb_temp_af_le

"""## Train/test split"""

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(X, y1, test_size=0.30, random_state=42)
y_train = y_train
y_test = y_test

"""## Lasso regression"""

lasso_re = LassoCV(cv=5, random_state=0)
lasso_re.fit(x_train, y_train)

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn.metrics import r2_score
pred_test_lasso= lasso_re.predict(x_test)
print("Mean squared error: ",np.sqrt(mean_squared_error(y_test,pred_test_lasso))) 
print("r squared: ",r2_score(y_test, pred_test_lasso))

"""## SGD Classifier"""

#y = imdb['success']
y2 = imdb['success'].to_numpy()

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test = train_test_split(X,y2,test_size=0.30, random_state=42)
print(x_train.shape,y_train.shape)
print(x_test.shape,y_test.shape)

from sklearn.linear_model import SGDClassifier
model_1 = SGDClassifier(random_state=42,max_iter=1000)
model_1.fit(x_train,y_train)

#get training and testing data accuracy
train_acc_model_1 = model_1.score(x_train,y_train)
test_acc_model_1 = model_1.score(x_test,y_test)
                        
print("training accuracy: ",train_acc_model_1)
print("testing accuracy: ",test_acc_model_1)
print("confusion matrix:")

from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score,recall_score,precision_score

#Get testing predictions
test_pred_model_1 = model_1.predict(x_test)

#Get confusion matrix
cfm_model_1 = confusion_matrix(y_test,test_pred_model_1)
print(cfm_model_1)

#Get f1 score, precision and recall
f1_model_1 = f1_score(y_test,test_pred_model_1)
precision_model_1 = precision_score(y_test,test_pred_model_1)
recall_model_1 = recall_score(y_test,test_pred_model_1)

print("precision: ",precision_model_1)
print("recall: ",recall_model_1)
print("f1 score: ",f1_model_1)

"""## Random forest grid search"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import average_precision_score,make_scorer
from sklearn.metrics import confusion_matrix,f1_score,precision_score,recall_score

parameters = {
     'n_estimators':(100,200), #the number of trees
     'min_samples_split': (200, 400),
    'class_weight': [{1:5}]
     #'min_samples_leaf': (20,40,60)
}
gs_clf = GridSearchCV(RandomForestClassifier(random_state=42),parameters,cv=5,n_jobs=-1,
                      scoring='f1')
#                     scoring=make_scorer(average_precision_score))
gs_clf.fit(x_train, np.ravel(y_train))

gs_clf.best_params_

"""## Random forest classifier"""

#Parameterize the random forest model and fit the data
model_2 = RandomForestClassifier(random_state=42,n_estimators=200,min_samples_split=400,class_weight={1:5})#,max_depth=5,min_samples_leaf=2000,min_samples_split=4000,class_weight={1:5})
model_2.fit(x_train,y_train)

#get training and testing data accuracy
train_acc_model_2 = model_2.score(x_train,y_train)
test_acc_model_2 = model_2.score(x_test,y_test)
                        
print("training accuracy: ",train_acc_model_2)
print("testing accuracy: ",test_acc_model_2)
print("confusion matrix:")

from sklearn.metrics import confusion_matrix

#Get testing predictions
test_pred_model_2 = model_2.predict(x_test)

#Get confusion matrix
cfm_model_2 = confusion_matrix(y_test,test_pred_model_2)
print(cfm_model_2)

#Get f1 score, precision and recall
f1_model_2 = f1_score(y_test,test_pred_model_2)
precision_model_2 = precision_score(y_test,test_pred_model_2)
recall_model_2 = recall_score(y_test,test_pred_model_2)

print("precision: ",precision_model_2)
print("recall: ",recall_model_2)
print("f1 score: ",f1_model_2)

"""## ROC curves"""

from bokeh.io import output_notebook, show 
from bokeh.plotting import figure
from bokeh.layouts import gridplot

def draw_one_roc_curve(fpr,tpr,thresholds,auc,model):
    #Set up the ColumnDataSource object
    from bokeh.models import LabelSet, ColumnDataSource,HoverTool
    import pandas as pd
    df_d = pd.DataFrame([fpr,tpr,thresholds]).transpose()
    df_d.columns = ["fpr","tpr","threshold"]
    source = ColumnDataSource(df_d)    
    
    
    # Create custom HoverTool -- we'll make one for each curve
    hover_ROC = HoverTool(names=['ROC'], tooltips=[("TPR", "@tpr"), 
                                                   ("FPR", "@fpr"), 
                                                   ("Thresh", "@threshold"),
                                                  ])

    # Create the tools
    p_tools_ROC = [hover_ROC, 'crosshair', 'zoom_in', 'zoom_out', 'save', 'reset', 'tap', 'box_zoom']

    p1 = figure(title="ROC Curve for "+model, tools=p_tools_ROC,x_range=(0,1),y_range=(0,1))

    p1.xaxis.axis_label = 'False Positive Rate' 
    p1.yaxis.axis_label = 'True Positive Rate'

    # plot curve and datapts
    p1.line('fpr', 'tpr', line_width=1, color="blue", source=source)
    p1.circle('fpr', 'tpr', size=3, color="orange", legend_label='auc='+auc, source=source, name='ROC')

    # Plot chance (tpr = fpr 45 degrees line)
    p1.line([0, 1], [0, 1], line_dash='dashed', line_width=0.5, color='black', name='Chance')

    # Keep the legend at the bottom 
    p1.legend.location = "bottom_right"
    
    #Return the figure
    return p1
    
    
def draw_roc_curves():
  
    #Get the predicted probabilities for each model
    #Note that we can't just use predictions because they will be 0,1 values
    from sklearn.model_selection import cross_val_predict
    predic_prob_model_1 = cross_val_predict(model_1,x_test,y_test,cv=5,method="decision_function")
    predic_prob_model_2 = model_2.predict_proba(x_test)


    #Get the AUC for each model
    from sklearn.metrics import roc_curve, roc_auc_score
    auc_m1 = roc_auc_score(y_test,predic_prob_model_1)
    auc_m2 = roc_auc_score(y_test,predic_prob_model_2[:,1])
    
    #Format auc to two decimal places
    auc_m1 = "%1.2f"%auc_m1
    auc_m2 = "%1.2f"%auc_m2
  
    #Using the predicted probabilities, get the roc curves
    #fpr = false positive rate
    #tpr = true positive rate
    #thresholds = threshold choices
    #The ROC curve reports the fpr and tpr for each chosen threshold
    fpr_m1,tpr_m1,thresholds_m1 = roc_curve(y_test,predic_prob_model_1)
    fpr_m2,tpr_m2,thresholds_m2 = roc_curve(y_test,predic_prob_model_2[:,1])

    #Draw the various ROC Curves
    p1=draw_one_roc_curve(fpr_m1,tpr_m1,thresholds_m1,auc_m1,"SGD Model")
    p2=draw_one_roc_curve(fpr_m2,tpr_m2,thresholds_m2,auc_m2,"Random Forest Model")

    #Set up the grid for all the curves
    grid = gridplot([[p1,p2]],sizing_mode="scale_both",merge_tools=True)

    #Show the curves
    show(grid)

#Call the function
draw_roc_curves()

"""## PR curves"""

def draw_one_PR_curve(precision,recall,thresholds,f1_score ,model):
    from bokeh.models import LabelSet, ColumnDataSource, Label
    import pandas as pd

    df_d = pd.DataFrame([recall,precision,thresholds]).transpose()
    df_d.columns = ["recall","precision","threshold"]

    source = ColumnDataSource(df_d)

    p_tools = ['crosshair', 'zoom_in', 'zoom_out', 'save', 'reset', 'tap', 'box_zoom']

    #Figure
    p = figure(title="PR Curve for "+model, tools=p_tools)
    p.xaxis.axis_label = 'threshold' 
    p.yaxis.axis_label = 'precision/recall'
    
    #Add lines for precision and recall
    p.line('threshold', 'precision', line_width=1, color="blue", source=source,legend_label="precision")
    p.line('threshold', 'recall', line_width=1, color="red", source=source,legend_label="recall")
    
    f1_label = Label(x=1.0, y=.70, x_units='screen', y_units='screen', text='F1 Score='+f1_score, render_mode='css',
      border_line_color='black', border_line_alpha=0.0,
      background_fill_color='white', background_fill_alpha=1.0)
    
    p.add_layout(f1_label)
   
    # legend location
    p.legend.location = "bottom_left"
    return p

def draw_pr_curves():
    #Get the predicted probabilities for each model
    #Note that we can't just use predictions because they will be 0,1 values
    from sklearn.model_selection import cross_val_predict
    from sklearn.metrics import precision_recall_curve

    predic_prob_model_1 = cross_val_predict(model_1,x_test,y_test,cv=5,method="decision_function")
    predic_prob_model_2 = model_2.predict_proba(x_test)

    #Get precisions and recalls
    precision_1,recall_1,thresholds_1 = precision_recall_curve(y_test,predic_prob_model_1)
    precision_2,recall_2,thresholds_2 = precision_recall_curve(y_test,predic_prob_model_2[:,1])

    #draw the curves
    p1 = draw_one_PR_curve(precision_1,recall_1,thresholds_1,str("%1.3f"%f1_model_1),"SGD Model")
    p2 = draw_one_PR_curve(precision_2,recall_2,thresholds_2,str("%1.3f"%f1_model_2),"Random Forest Model")

    #Set up the grid for all the curves
    grid = gridplot([[p1,p2]],sizing_mode="scale_both",merge_tools=True)

    #Show the curves
    show(grid)

draw_pr_curves()

"""## Future Movie Prediciton"""

# since Random Forest gives us better F1 score, we'll use Random Forest to do prediciton.

"""input all the info as a datapoint, labelencoding using the mapping list and run the ranmdom forest to predict if a movie would be successful"""

#We are predict Spider Man: No Way Home, the info is the following: 
# Rating: PG-13; Genre : Action; Runtime: 2 hours 30 min;
# Release date: December 17, 2021 (United States); Countries of origin: United States; Production companies: Columbia Pictures;
# Director:Jon Watts; Star: Zendaya, Benedict Cumberbatch, Tom Holland
rating_0 = str(input('Input the rating: '))
rating_0 = int(le_name_mapping_rating[rating_0])
genre_0 =  str(input('Input the genre: ')).lower()
genre_0 = int(le_name_mapping_genre[genre_0])
country_0 = str(input('Which country made this movie: ')) 
country_0 = int(le_name_mapping_country[country_0])
company_0 = str(input('Input the production company: '))
company_0 = int(le_name_mapping_company[company_0])
released_country_0 = str(input('Where is this movie released: '))
released_country_0 = int(le_name_mapping_released_country[released_country_0])
director_0 = str(input('Who is the director: '))
director_popularity_0 = int(1 if director_0 in popular_directors else 0)    
star_01 = str(input('Who is the first main actor or actress:'))
star_01 = 1 if star_01 in star_list else 0
star_02 = str(input('Who is the second main actor or actress: '))
star_02 = 1 if star_02 in star_list else 0
star_popularity_0 = int(1 if (star_01 + star_02) >=1 else 0)  
runtime_0 = float(input('How long is the movie in minutes, please only type number:  '))
released_month_0 = int(input('Which month is the movie released, please type number: '))
released_day_0 = int(input('Which day of that month is the movie released, please type number: '))
released_day_of_week_0 = str(input('Which day of week is the movie released: '))
released_day_of_week_0 = int(day_of_week_mapping[released_day_of_week_0])

import numpy as np
data_point = np.array([(rating_0, genre_0,country_0,company_0,released_country_0,director_popularity_0,star_popularity_0,runtime_0, released_month_0, released_day_0,released_day_of_week_0)],
    dtype = [('rating','int64'),('genre', 'int64'),('country','int64'),('company','int64'),('released_country','int64'),('director_popularity','int32'),('star_popularity','int32'),
    ('runtime','float64'),('released_month','int64'),('released_day','int64'),('released_day_of_week','int64')])
pd_data_point = pd.DataFrame(data_point)
x_new =x.append(pd_data_point, ignore_index=True)

# one-hot encode the new datapoint and standardize it
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer, make_column_transformer
import numpy as np
#The code below makes a column transformer object that scales the non-categorical columns
# and one hot encodes the categorical columns
preprocess = make_column_transformer((StandardScaler(),non_categorical_column), 
    (OneHotEncoder(categories="auto",drop='first'), categorical_column))

#The next step prepares the independent variables
X = preprocess.fit_transform(x_new).toarray()
datapoint_x = X[-1].reshape(1,-1)

test_pred_model_2 = model_2.predict(datapoint_x)

print('Successful Movie?', np.array2string(test_pred_model_2))

