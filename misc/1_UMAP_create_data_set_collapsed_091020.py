import os, glob
import pandas as pd

########### READ IN DATA ###########
filesFolder =
outputPath = 
features2removeFile = 
classifierName =

filesFound = glob.glob(filesFolder + '/*.csv')
counter = 0
concatDf = pd.DataFrame()
features2remove = pd.read_csv(features2removeFile)
features2removeList = list(features2remove['Column_name'])

for file in filesFound:
    filename = os.path.basename(file)
    currDf = pd.read_csv(file, index_col=0)
    groupDf = pd.DataFrame()
    v = (currDf[classifierName] != currDf[classifierName].shift()).cumsum()
    u = currDf.groupby(v)[classifierName].agg(['all', 'count'])
    m = u['all'] & u['count'].ge(1)
    groupDf['groups'] = currDf.groupby(v).apply(lambda x: (x.index[0], x.index[-1]))[m]
    differenceList = []
    for row in groupDf.itertuples():
        difference = row[1][1] - row[1][0]
        differenceList.append(difference)
    groupDf['boutLength'] = differenceList
    frameWindowListStart, frameWindowListEnd = [], []
    for row in groupDf.itertuples():
        frameWindowListStart.append(int(row[1][0]))
        frameWindowListEnd.append(int(row[1][1]))
    currDf = currDf.drop(features2removeList, axis=1)
    for startFrame, endFrame in zip(frameWindowListStart, frameWindowListEnd):
        relRows = currDf.loc[startFrame:endFrame]
        meanVals = relRows.mean(axis=0)
        meanVals = pd.DataFrame(meanVals).transpose()
        meanVals['frame_no_start'] = startFrame
        meanVals['frame_no_end'] = endFrame
        meanVals['video'] = os.path.basename(file).replace('.csv', '')
        if "Video" in filename:
            sex, group = 'Female', 'Female'
        if "Video" not in filename:
            sex = 'Male'
        if "CSDS" in filename:
            group = 'CSDS_Male'
        if ("RI" in filename) or ('SA_0' in filename):
            group = 'RI_Male'
        meanVals['group'] = group
        meanVals['sex'] = sex
        concatDf = pd.concat([concatDf, meanVals], axis=0)
        concatDf.reset_index(drop=True, inplace=True)
        counter += 1
        print('Processed ' + str(os.path.basename(file)) + ' ' + str(counter))

concatDf = concatDf.drop([classifierName], axis=1, errors='ignore')
concatDf[classifierName] = classifierName
concatDf.to_pickle(os.path.join(outputPath, classifierName + '.pkl'))
print('Annotations for UMAP saved.')

