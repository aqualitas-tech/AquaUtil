import numpy as np
import datetime as dt
import pandas as pd


def crtParmDic(TblName, con, FiltrDic={}, TOCtbl=False, ParamFld='Parameter'):
    """
    This function takes table name and a filter dictionary and return
    a dict. that for any param. we get a list that  contains the x0,x1,x2,x3,x4,x5 values for each parameter.
    In case the table is TOC then there are 2 sets of data for each parameter.
    TblName - string. The table to query
    con -  connector. The database  connector
    FiltrDic - dict. The keys are the fields to filter and the values are the
               values to filter upon. The function will use AND between
               each filter
    TOCtbl - bool. If true then this is a TOC table and there are 2 sets
             of values to return
    ParamFld - string. The name of the parameter field in the table
    return:
    Dictionary with a parameter as the key and X0,X1,X2,X3,X4,X5 as a list.
    In the case of TOC it return 2 sets of X in the format: TOC_X and UVL_X

    Example:
        FiltrDic = {'device_id':'UNUM0005','Active':1}
        PrmDic=crtParmDic('Calibration_equations',mycursor,FiltrDic)
    """
    NumFltrElm = len(FiltrDic.keys())
    WhereClause = ""
    OutDic = {}

    # Build the where clause
    # Check if the filter dict. is empty or not
    if NumFltrElm > 0:
        WhereClause = " Where "
        for key in FiltrDic.keys():
            if isinstance(FiltrDic[key], str) or isinstance(FiltrDic[key], dt.datetime):
                val = '"' + str(FiltrDic[key]) + '"'
            else:
                val = str(FiltrDic[key])
            WhereClause = WhereClause + key + ' = ' + val + ' and '
        WhereClause = WhereClause[0:-5]

    # Build the SQL sentence
    SQL = 'select * from ' + TblName + WhereClause

    # Get the data from the database into dataframe
    df = pd.read_sql(SQL, con)
    # Check if this is a TOC table or not
    if not TOCtbl:
        for i in range(0, len(df.index)):
            OutDic[df[ParamFld].iloc[i]] = []
            for j in range(0, 6):
                OutDic[df[ParamFld].iloc[i]].append(df['X' + str(j)].iloc[i])
    else:
        OutDic['TOC'] = []
        OutDic['Ab230_TOC'] = []
        for j in range(0, 6):
            OutDic['TOC'].append(df['TOC_X' + str(j)].iloc[0])
        for k in range(0, 6):
            OutDic['Ab230_TOC'].append(df['UVL_X' + str(k)].iloc[0])
    return OutDic


def CalibList(x, CalbList, MustBePositive=False):
    """
    Gets alist of polynomial parameters (CalibList) that is used for calibration. Also gets the X value and
    returns the f(x) value of the calibration.
    :param x: double/int. The X value in the calibration polynom
    :param CalbList:list. The list that contains the polynomial parameters
    :param MustBePositive: in case the f(x) should only be positive then it transforms the negative values to zero
    :return: f(x)
    """
    reslt = CalbList[0] * (x ** 0) + CalbList[1] * (x ** 1) + CalbList[2] * (x ** 2) \
            + CalbList[3] * (x ** 3) + CalbList[4] * (x ** 4) + CalbList[5] * (x ** 5)
    if MustBePositive:
        reslt = np.where(reslt < 0, 0, reslt)
    return reslt


def DecodeRemarks(df):
    """
    Gets dataframe with column "comment"
    Then decode the comment in the following template:
    Description_ParamName_ParamValue...._ParamName_ParamValue
    The values will appeneded to the dataframe and the new columns will be:
    Description and all the ParamName that were given
    The function return the original df + the new columns
    """
    df['comment'] = df['comment'].astype(str) # make sure that the comments is a string column
    if '_' in df['comment'].iloc[0]:
        df['lengthOfComments'] = df['comment'].str.split('_').str.len()
        df['commentList'] = df['comment'].str.split('_')

        # if there are odd number of elements it removes the first element from the list (usually the experiment name)
        df['comment2'] = df.apply(lambda x: x.commentList if (x.lengthOfComments %2)==0 else x.commentList[1:],axis=1)
        df['lengthOfComments2'] = df['comment2'].str.len()
        lengthOfComments = df['lengthOfComments2'].max()

        for i in range(0, lengthOfComments, 2):
            param = df['comment2'].str[i].iloc[0]
            if param=='EC':
                param= 'EC_std'
            df[param] = df['comment2'].str[i + 1].astype(float)
        df=df.drop(['comment2','lengthOfComments','lengthOfComments2','commentList'],axis=1)
        df = df.loc[:, df.columns.notna()] #Remove columns titled Nan
    else:
        print("No comments")
    
    return df


def CompleteSet(Title, ParamList):
    """
     This function takes a list of values and return a 6 values list putting
     zeroes in "empty places. Also, if the title say "no_inter" then
     it adds a zero at the beggining of the list.
     Input: Title string. - The title of the parameters list
            ParamList list. - The parameters list
    """
    OutList = []
    if 'no_inter' in Title:
        OutList = [0]

    OutList.extend(ParamList)
    for x in range(len(OutList), 6):
        OutList.append(0)
    return OutList
