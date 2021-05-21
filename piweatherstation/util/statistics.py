from numpy import mean
from numpy import std
from numpy import percentile

def std_dev(dataset):

    data_mean, data_std = mean(dataset), std(dataset)
    # Identify outliers
    cut_off = data_std * 3
    lower, upper = data_mean - cut_off, data_mean + cut_off

    #outliers = [x for x in data if x < lower or x > upper]
    outliers_removed = [x for x in dataset if x > lower and x < upper]

    return outliers_removed


def iqr(dataset):

    # calculate interquartile range
    q25, q75 = percentile(dataset, 25), percentile(dataset, 75)
    iqr = q75 - q25

    # calculate the outlier cutoff
    cut_off = iqr * 1.5
    lower, upper = q25 - cut_off, q75 + cut_off 

    # remove outliers
    outliers_removed = [x for x in dataset if x > lower and x < upper]

    return outliers_removed
