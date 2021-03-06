import sys
path_project = "/home/igorcosta/soccer/"
sys.path.insert(1, path_project)
import pandas as pd
from apps.sportmonks import learning
from apps.sportmonks import tunning
from core.config import PATH_SPORTMONKS_DATAFRAMES
import sys

stats_list = ['goals', 'corners', 'on_target', 'off_target', 'attacks', 'dangerous_attacks', 'possession']
goals_list = ['goals']


def process_gb():

    print("processing...")
    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'
    data = pd.read_csv(filename)

    features = stats_list
    name = 'gb_stats_all'
    learning.learning_all_time(data, features, name)
    features = stats_list
    name = 'gb_stats_lm'
    learning.learning_last_minute(data, features, name)
    print("end")

    features = ['goals']
    name = 'gb_goals_all'
    learning.learning_all_time(data, features, name)
    features = ['goals']
    name = 'gb_goals_lm'
    learning.learning_last_minute(data, features, name)


def process_nn():

    print("processing...")
    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'
    data = pd.read_csv(filename)
    print(data.keys())

    features = ['goals']
    name = 'nn_goals_lm_mae'
    learning.learning_keras_all_time(data, features, name)
    print("end")

    features = stats_list
    name = 'nn_stats_lm_mae'
    learning.learning_keras_all_time(data, features, name)


def process_dnn():

    print("processing...")
    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'
    data = pd.read_csv(filename)
    print(data.keys())

    # features = ['goals']
    # name = 'dnn_goals_lm_2'
    # learning.learning_dnn_lm(data, features, name)
    # print("end")

    features = stats_list
    name = 'dnn_stats_lm_32'
    learning.learning_dnn_lm(data, features, name)


def get_columns(features, types, minute, transform=False):

    columns = []
    for stat in features:
        for t in types:
            label = 'ts_' + stat + '_' + t + '_' + str(minute)
            col = label
            columns.append(col)

    if transform:
        for stat in features:
            for t in types:
                label = 'ts_' + stat + '_' + t + '_' + str(minute)

                col = label + '_mean'
                columns.append(col)
                col = label + '_var'
                columns.append(col)
                col = label + '_kut'
                columns.append(col)


    return columns

def learning_by_minute(data, clf_label, ft_label, id_label, features, minute, transform=False, pre=False):

    print("...begin...")

    if id_label == 'ha':
        col_labels = ['home', 'away']
        columns = get_columns(features, col_labels, minute, transform)
    elif id_label == 'dd':
        col_labels = ['dif', 'div']
        columns = get_columns(features, col_labels, minute, transform)

    if pre:
        columns.append("odds_p_norm_home")
        columns.append("odds_p_norm_draw")
        columns.append("odds_p_norm_away")
        columns.append("odds_p_std_home")
        columns.append("odds_p_std_draw")
        columns.append("odds_p_std_away")

    job_label = clf_label + "_" + ft_label + "_" + id_label

    if clf_label.find('gnb') >= 0:
        learning.gnb_by_minute_total(data, columns, job_label, minute)
    elif clf_label.find('knn') >= 0:
        learning.knn_by_minute_total(data, columns, job_label, minute)
    elif clf_label.find('xgb') >= 0 :
        learning.xgb_by_minute_total(data, columns, job_label, minute)
    elif clf_label.find('mlp') >= 0:
        learning.mlp_by_minute_total(data, columns, job_label, minute)

    print("...end...")


def learning_clf(clf_label, transform=False, pre=False):

    if pre:
        filename = PATH_SPORTMONKS_DATAFRAMES + 'status1_odds.csv'
    else:
        if transform:
            filename = PATH_SPORTMONKS_DATAFRAMES + 'status1_transformed.csv'
        else:
            filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'

    data = pd.read_csv(filename)

    print(len(data))
    data = data[pd.notnull(data['odds_p_norm_home'])]
    data = data[pd.notnull(data['odds_p_norm_draw'])]
    data = data[pd.notnull(data['odds_p_norm_away'])]
    data['odds_p_std_home'].fillna(0, inplace=True)
    data['odds_p_std_draw'].fillna(0, inplace=True)
    data['odds_p_std_away'].fillna(0, inplace=True)
    print(len(data))

    for i in range(0,96):

        for ft_label, features in zip(['stats', 'goals'], [stats_list, goals_list]):

            for id_label in ['ha','dd']:
                print('minute ', str(i))
                learning_by_minute(data, clf_label, ft_label, id_label, features, i, transform, pre)

def learning_knn():

    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'
    data = pd.read_csv(filename)
    clf_label = 'knn'

    print(len(data))
    for i in range(0,96):

        for ft_label, features in zip(['stats', 'goals'], [stats_list, goals_list]):

            for id_label in ['ha','dd']:
                print('minute ', str(i))
                learning_by_minute(data, clf_label, ft_label, id_label, features, i)


def learning_gnb_by_minute(minute, tp):

    print("...begin...")
    method = 'gnb'

    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'

    if tp == 1:
        types = ['home', 'away']
        tp = 'ha'
    elif tp == 2:
        types = ['dif', 'div']
        tp = 'dd'

    data = pd.read_csv(filename)

    features = stats_list
    name = method + "_stats_" + tp + ""
    learning.gnb_by_minute(data, features, types, name, minute)

    features = ['goals']
    name = method + "_goals_" + tp + ""
    learning.gnb_by_minute(data, features, types, name, minute)
    print("...end...")


def process_by_minute_dnn(minute):

    print("processing...")
    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1_transformed.csv'
    data = pd.read_csv(filename)
    types = ['home', 'away']

    features = stats_list
    name = 'nn_stats_fv_t2_' + str(minute)
    learning.learning_by_minute_nn(data, features, types, name, minute, transform=True)

    features = ['goals']
    name = 'nn_goals_fv_t2_' + str(minute)
    learning.learning_by_minute_nn(data, features, types, name, minute, transform=True)

def learning_knn_by_minute(minute, tp):

    print("processing...")
    method = 'knn'

    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'

    if tp == 1:
        types = ['home', 'away']
        tp = 'ha'
    elif tp == 2:
        types = ['dif', 'div']
        tp = 'dd'

    data = pd.read_csv(filename)

    features = stats_list
    name = method + "_stats_" + tp + ""
    learning.knn_by_minute(data, features, types, name, minute)

    features = ['goals']
    name = method + "_goals_" + tp + ""
    learning.knn_by_minute(data, features, types, name, minute)

def tunning_knn_by_minute(minute, tp):

    print("processing...")
    method = 'knn'

    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'

    if tp == 1:
        types = ['home', 'away']
        tp = 'ha'
    elif tp == 2:
        types = ['dif', 'div']
        tp = 'dd'

    data = pd.read_csv(filename)

    features = stats_list
    name = method + "_stats_" + tp + ""
    tunning.knn_by_minute(data, features, types, name, minute)

    features = ['goals']
    name = method + "_goals_" + tp + ""
    tunning.knn_by_minute(data, features, types, name, minute)

def tunning_xgb_by_minute(minute, tp):

    print("processing...")
    method = 'xgb'

    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'

    if tp == 1:
        types = ['home', 'away']
        tp = 'ha'
    elif tp == 2:
        types = ['dif', 'div']
        tp = 'dd'

    data = pd.read_csv(filename)

    features = stats_list
    name = method + "_stats_" + tp + ""
    tunning.xgb_by_minute(data, features, types, name, minute)

    features = ['goals']
    name = method + "_goals_" + tp + ""
    tunning.xgb_by_minute(data, features, types, name, minute)

def tunning_by_minute_dnn(minute):

    print("processing...")
    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'
    data = pd.read_csv(filename)
    types = ['dif', 'div']
    method = 'dnn'
    tp = types[0][0] + types[1][0]

    features = stats_list
    name = method + "_stats_" + tp + ""
    tunning.tunning_by_minute_mlp(data, features, types, name, minute)

    features = ['goals']
    name = method + "_goals_" + tp + ""
    tunning.tunning_by_minute_mlp(data, features, types, name, minute)

def tunning_by_minute_cnn(minute):

    print("processing...")
    filename = PATH_SPORTMONKS_DATAFRAMES + 'status1.csv'
    data = pd.read_csv(filename)
    types = ['dif', 'div']
    method = 'dnn'
    tp = types[0][0] + types[1][0]

    features = stats_list
    name = method + "_stats_" + tp + ""
    tunning.tunning_by_minute_cnn(data, features, types, name, minute)

    features = ['goals']
    name = method + "_goals_" + tp + ""
    tunning.tunning_by_minute_cnn(data, features, types, name, minute)

tunning_by_minute_cnn(2)
#learning_clf('knn')
#leaning_clf('pre_knn', pre=True)
#minute = sys.argv[1]
#tp = int(sys.argv[2])
#minute = 16
#tp = 1
#print(minute, tp)
#tunning_xgb_by_minute(minute, tp)
