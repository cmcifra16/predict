# Importing essential libraries
import numpy as np
import pandas as pd
import pickle

# Loading the dataset
df = pd.read_csv(r'C:\Users\chris\Desktop\capstone final\covid.csv')

# Renaming DiabetesPedigreeFunction as DPF
df = df.rename(columns={'corona_result':'DPF'})
df=df.drop(columns=['test_date'])
# Replacing the 0 values from ['Glucose','BloodPressure','SkinThickness','Insulin','BMI'] by NaN
df_copy = df.copy(deep=True)
 
# Model Building
from sklearn.model_selection import train_test_split
X = df.drop(columns='test_indication')
y = df['test_indication']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

# Creating Random Forest Model
from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(n_estimators=20)
classifier.fit(X_train, y_train)

# Creating a pickle file for the classifier
filename = 'covid.pkl'
pickle.dump(classifier, open(filename, 'wb'))