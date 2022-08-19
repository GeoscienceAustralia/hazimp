import pandas as pd
import os
import numpy as np
import re
from datetime import datetime
import argparse


def get_damage(fp):
    """
    Calculates the total strucural loss given a hazimp output file.
    """
    df = pd.read_csv(fp)
    return df.structural_loss_sum.sum()


def get_quantile_id(eventids, loss, q):
    """
    Calculates the specified loss quantile and returns the corresponding eventid.

    params:
        - eventids: list of eventids
        - loss: a list of total structural losses for each event id
        - q: the quantile to calculate
    """
    idxs = np.argsort(loss)
    ii = int(np.round(q * (len(idxs) - 1)))
    return eventids[idxs[ii]]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-wc', '--wm_config', help='')
    parser.add_argument('-hc', '--hazimp_config', help='')
    parser.add_argument('-wd', '--work_dir', help='')
    parser.add_argument('-l', '--low_res_dir', help='')

    args = parser.parse_args()
    print(args)
    # only these filepaths need to be specified
    low_res_impact_dir = args.low_res_dir
    working_dir = args.work_dir
    wm_config_template = open(args.wm_config).read()
    hazimp_config_template = open(args.hazimp_config).read()

    # the quantiles also need to be specified
    quantiles = [0.5, 0.9]

    # NOTE: nothing below needs to be changed for different use cases

    # calculate the total structural loss for each event in `low_res_impact_dir`
    low_res_loss = []
    eventids = []
    print("Loading in loss")
    for eventid in os.listdir(low_res_impact_dir):
        try:
            loss = get_damage(os.path.join(low_res_impact_dir, eventid, f"{eventid}_agg.csv"))
            low_res_loss.append(loss)
            eventids.append(eventid)

        except FileNotFoundError as e:
            pass

    # calculate the eventids for each quantile and apply wind multipliers
    # and hazimp

    # NOTE: ideally this should re-use the WM extracted by the low resolution wm script
    # to do this change the extent applied to 'yes' and the mult_path to the the m4.. file generated
    extent_applied = 'no'
    mult_path = os.path.join(working_dir, f"{int(quantiles[0] * 100)}_percentile", "m4_source.tif")
    print("Calculating in quantiles")
    for q in quantiles:

        # calculate eventid
        eventid = get_quantile_id(eventids, low_res_loss, q)

        # setup output folder
        outpath = os.path.join(working_dir, f"{int(q * 100)}_percentile")
        if not os.path.isdir(outpath):
            os.makedirs(outpath)

        # setup wm config file
        wm_config = wm_config_template.replace('EVENTID', eventid)
        wm_config = wm_config.replace('EXTENTAPPLIED', extent_applied)
        wm_config = wm_config.replace('OUTPUTPATH', outpath)
        if extent_applied == 'yes':
            wm_config = re.sub('Multipliers=.*', mult_path, wm_config)

        wm_config_path = os.path.join(outpath, f"{eventid}_pm.ini")
        with open(wm_config_path, 'w') as fout:
            fout.write(wm_config)

        # setup hazimp config file
        hazimp_config = hazimp_config_template.replace('EVENTID', eventid)
        hazimp_config_path = os.path.join(outpath, f"{eventid}_hazimp.yaml")
        with open(hazimp_config_path, 'w') as fout:
            fout.write(hazimp_config)

        extent_applied = 'yes'

        date = str(datetime.now().date())
        print("running wm!")
        # run wm
        os.system(
            f"python3 ~/tcrm/ProcessMultipliers/processMultipliers.py -c {wm_config_path} > {outpath}/wm_{eventid}.stdout.{date} 2>&1"
        )

        # run hazimp
        os.system(
            f"python3 ~/tcrm/ProcessMultipliers/processMultipliers.py -c {wm_config_path} > {outpath}/hazimp_{eventid}.stdout.{date} 2>&1"
        )

    #export PYTHONPATH=$PYTHONPATH:~/tcrm
