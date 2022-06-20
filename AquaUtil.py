import numpy as np


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


def DecodeRemarks(df, withExpName=True):
    """
    Gets dataframe with column "comment"
    Then decode the comment in the following template:
    Description_ParamName_ParamValue...._ParamName_ParamValue
    The values will appeneded to the dataframe and the new columns will be:
    Description and all the ParamName that were given
    The function return the original df + the new columns
    if withExpName= true then the first parameter is the experiment name
    """
    lengthOfComments = df['comment'].str.split('_').str.len()[0]
    commentList = df['comment'].str.split('_')
    if withExpName:
        StartFrom = 1
        df['ExperName'] = commentList.str[0]
    else:
        StartFrom = 0

    for i in range(StartFrom, lengthOfComments, 2):
        df[commentList.str[i][0]] = commentList.str[i + 1].astype(float)

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
