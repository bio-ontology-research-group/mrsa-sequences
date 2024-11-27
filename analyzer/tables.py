import click as ck
import json
import pandas as pd
import os
import random

ck.command()
def main():
    # with open('data/analysis.json') as f:
    #     data = json.loads(f.read())
    #     # kraken_table(data['kraken'])
    #     # mlst_table(data['mlst'])
    #     sequence_types(data['mlst'])
    # amr_table()
    scoary_table()

def scoary_table():
    files = os.listdir('data/scoary')
    for fn in files:
        df = pd.read_csv('data/scoary/' + fn)
        top10 = []
        for row in df.itertuples():
            pv = float(row.Bonferroni_p)
            if not row.Gene.startswith('group') and pv <= 0.05:
                top10.append(row.Gene.replace('_', '\\_'))
            if len(top10) >= 10:
                break
        if len(top10) == 0:
            continue
        drug = fn.split('_')[0]
        genes = ', '.join(top10)
        print(drug, '&', genes, '\\\\')
        print('\\hline')
        
 
def sort_ids(data):
    res = sorted(data, key=lambda x: x[0])
    return res

def kraken_table(kraken_data):
    data = sort_ids(kraken_data)
    for sid, item in data:
        line = sid
        for score, tid, name in item[:2]:
            line += f' & {name} & {score}'
        # line += ' \\\\'
        print(line)
        print('\\hline')

def mlst_table(mlst_data):
    mlst_data = sort_ids(mlst_data)
    for sid, items in mlst_data:
        line = sid
        for it in items:
            pos = it.find('_')
            if pos != -1:
                it = it[:pos] + '\\' + it[pos:]
            line += f' & {it}'
        line += ' \\\\'
        print(line)
        print('\\hline')

def sequence_types(mlst_data):
    types = [
        1, 101, 1153, 1156, 121, 1290, 1292, 1482, 149, 15, 152, 1535,
        1930, 20, 22, 2250, 239, 241, 25, 2689, 2867, 2884, 291, 30,
        361, 4317, 45, 46, 5, 508, 59, 6, 672, 772, 8, 80, 88, 96, 97,
        997, 1637, 1750]
    n_colors = len(types)
    colors = [
        "#" + ''.join([random.choice('0123456789ABCDEF') for i in range(6)])
       for j in range(n_colors)]
    colors_dict = {str(st): color for st, color in zip(types, colors)}
    colors_dict['-'] = '#0000FF'
    print(' '.join(colors_dict.keys()))
    print(' '.join(colors_dict.values()))
    print(' '.join(['1'] * len(colors_dict)))
    mlst_data = sort_ids(mlst_data)
    for sid, items in mlst_data:
        line = sid
        if items[0] == 'saureus':
            print(sid, colors_dict[items[1]], items[1])

def amr_pred_table():
    df = pd.read_pickle('data/gt_resistance.pkl')
    drugs = set()
    for row in df.itertuples():
        for dr, mic in row.resistance:
            drugs.add(dr)
        for dr, mic in row.sensitive:
            drugs.add(dr)
    drugs = list(drugs)
    drugs = sorted(drugs)
    data = []
    for row in df.itertuples():
        sid = row.samples
        r_drugs = {}
        s_drugs = {}
        for dr, mic in row.resistance:
            r_drugs[dr] = mic
        for dr, mic in row.sensitive:
            s_drugs[dr] = mic
        it_data = []
        for dr in drugs:
            if dr in r_drugs:
                it_data.append(f'\\OK')
            elif dr in s_drugs:
                it_data.append(f'')
            else:
                it_data.append('-')
        data.append((sid, it_data))
    data = sort_ids(data)
    line = 'Isolate'
    for dr in drugs:
        line +=' & \\rot{' + dr + '}'
    print(line)
    for sid, items in data:
        line = sid
        for it in items:
            line += f' & {it}'
        line += ' \\\\'
        print(line)
        print('\\hline')
    


def amr_table():
    df = pd.read_pickle('data/lab_resistance.pkl')
    drugs = set()
    for row in df.itertuples():
        for dr, mic in row.resistance:
            drugs.add(dr)
        for dr, mic in row.sensitive:
            drugs.add(dr)
    drugs = list(drugs)
    drugs = sorted(drugs)
    data = []
    for row in df.itertuples():
        sid = row.samples
        r_drugs = {}
        s_drugs = {}
        for dr, mic in row.resistance:
            r_drugs[dr] = mic
        for dr, mic in row.sensitive:
            s_drugs[dr] = mic
        it_data = []
        for dr in drugs:
            if dr in r_drugs:
                it_data.append(f'\\OK')
            elif dr in s_drugs:
                it_data.append(f'')
            else:
                it_data.append('-')
        data.append((sid, it_data))
    data = sort_ids(data)
    # line = 'Isolate'
    # for dr in drugs:
    #     line +=' & \\rot{' + dr + '}'
    # print(line)
    # for sid, items in data:
    #     line = sid
    #     for it in items:
    #         line += f' & {it}'
    #     line += ' \\\\'
    #     print(line)
    #     print('\\hline')
    # CSV output

    roary_ids = set(["ID00001","ID00002","ID00003","ID00004","ID00005","ID00006","ID00007","ID00008","ID00009","ID00010","ID00011","ID00012","ID00013","ID00014","ID00015","ID00016","ID00017","ID00018","ID00019","ID00020","ID00021","ID00022","ID00023","ID00024","ID00025","ID00026","ID00027","ID00028","ID00029","ID00030","ID00031","ID00032","ID00033","ID00034","ID00035","ID00036","ID00037","ID00038","ID00039","ID00040","ID00041","ID00042","ID00043","ID00044","ID00045","ID00046","ID00047","ID00048","ID00049","ID00050","ID00051","ID00052","ID00053","ID00054","ID00055","ID00056","ID00057","ID00058","ID00059","ID00060","ID00061","ID00062","ID00063","ID00064","ID00065","ID00066","ID00067","ID00068","ID00069","ID00071","ID00072","ID00073","ID00074","ID00075","ID00076","ID00077","ID00078","ID00079","ID00080","ID00081","ID00082","ID00083","ID00084","ID00085","ID00086","ID00087","ID00089","ID00090","ID00091","ID00092","ID00093","ID00094","ID00103","ID00104","ID00106","ID00107","ID00108","ID00109","ID00110","ID00111","ID00113","ID00114","ID00115","ID00119","ID00120","ID00121","ID00122","ID00123","ID00125","ID00126","ID00127","ID00128","ID00129","ID00130","ID00131","ID00132","ID00134","ID00135","ID00136","ID00137","ID00138","ID00139","ID00140","ID00141","ID00142","ID00143","ID00144","ID00145","ID00146","ID00147","ID00148","ID00150","ID00151","ID00152","ID00153","ID00154","ID00155","ID00156","ID00157","ID00158","ID00160","ID00161","ID00162","ID00163","ID00164","ID00165","ID00166","ID00167","ID00168","ID00169","ID00170","ID00171","ID00172","ID00173","ID00174","ID00175","ID00176","ID00177","ID00178","ID00180","ID00181","ID00182","ID00183","ID00184","ID00185","ID00186","ID00188","ID00189","ID00190","ID00192","ID00193","ID00194","ID00195","ID00196","ID00197","ID00198","ID00199","ID00200","ID00201","ID00202","ID00203","ID00204","ID00205","ID00206","ID00207","ID00208","ID00210","ID00211","ID00214","ID00215","ID00216","ID00217","ID00218","ID00219","ID00220","ID00221","ID00222","ID00223","ID00224","ID00225","ID00226","ID00227","ID00228","ID00229","ID00230","ID00232","ID00233","ID00234","ID00235","ID00236","ID00237","ID00238","ID00239","ID00240","ID00241","ID00242","ID00244","ID00245","ID00246","ID00248","ID00249","ID00250","ID00251","ID00252","ID00253","ID00254","ID00255","ID00256","ID00257","ID00258","ID00262","ID00263","ID00264","ID00265","ID00266","ID00267","ID00269","ID00271","ID00272","ID00273","ID00274","ID00275","ID00276","ID00277","ID00278","ID00279","ID00280","ID00281","ID00282","ID00283","ID00284","ID00285","ID00286","ID00287","ID00288","ID00289","ID00290","ID00291","ID00292","ID00293","ID00294","ID00295","ID00296","ID00298","ID00299","ID00301","ID00302","ID00303","ID00304","ID00305","ID00306","ID00307","ID00308","ID00310","ID00311","ID00312","ID00313","ID00315","ID00316","ID00317","ID00318","ID00319","ID00320","ID00321","ID00322","ID00324","ID00325","ID00326","ID00327","ID00328","ID00329","ID00330","ID00331","ID00332","ID00333","ID00334","ID00335","ID00336","ID00337","ID00338","ID00340","ID00341","ID00342","ID00343","ID00344","ID00345","ID00346","ID00347","ID00348","ID00350","ID00351","ID00352","ID00353","ID00354","ID00358","ID00359","ID00362","ID00363","ID00364","ID00365","ID00366","ID00367","ID00368","ID00369","ID00370","ID00371","ID00373","ID00374","ID00375","ID00376","ID00378","ID00379","ID00380","ID00381","ID00382","ID00383","ID00385","ID00387","ID00388","ID00389","ID00391","ID00392","ID00393","ID00394","ID00395","ID00396","ID00397","ID00398","ID00399","ID00400","ID00401","ID00402","ID00403","ID00404","ID00405","ID00406","ID00407","ID00408","ID00409","ID00410","ID00411","ID00412","ID00414","ID00415","ID00416","ID00417","ID00418","ID00419","ID00421","ID00424","ID00425","ID00426","ID00427","ID00428","ID00429","ID00430","ID00431","ID00432","ID00433","ID00434","ID00435","ID00436","ID00437","ID00438","ID00439","ID00440","ID00441","ID00443","ID00444","ID00445","ID00446","ID00447","ID00448","ID00449","ID00450","ID00451","ID00452","ID00453","ID00454","ID00455","ID00456","ID00457","ID00458","ID00459","ID00460","ID00461","ID00462","ID00463","ID00464","ID00465","ID00467","ID00468","ID00469","ID00470","ID00471","ID00472","ID00473","ID00474","ID00475","ID00476","ID00479","ID00482","ID00483","ID00484","ID00485","ID00486","ID00487","ID00488","ID00489","ID00492","ID00493","ID00494","ID00495","ID00496","ID00497","ID00504","ID00505","ID00513","ID00514","ID00515","ID00516","ID00517","ID00518","ID00519","ID00520","ID00521","ID00522","ID00523","ID00524","ID00525","ID00526","ID00528","ID00529","ID00530","ID00531","ID00532","ID00533","ID00534","ID00535","ID00536","ID00537","ID00538","ID00539","ID00541","ID00542","ID00543","ID00544","ID00545","ID00546","ID00547","ID00548","ID00549","ID00550","ID00551","ID00552","ID00553","ID00554","ID00555","ID00556","ID00557","ID00558","ID00561","ID00562","ID00564","ID00565","ID00566","ID00567","ID00570","ID00571","ID00572","ID00573","ID00575","ID00576","ID00577","ID00578","ID00580","ID00583","ID00584","ID00586","ID00587","ID00588","ID00591","ID00593","ID00594","ID00595","ID00596","ID00598","ID00599","ID00606","ID00611","ID00612","ID00613","ID00614","ID00615","ID00616","ID00617","ID00618","ID00620","ID00621","ID00622","ID00623","ID00624","ID00625","ID00626","ID00627","ID00628","ID00630","ID00631","ID00632","ID00633","ID00634","ID00636","ID00637","ID00638","ID00639","ID00640","ID00642","ID00644","ID00646","ID00647","ID00648","ID00649","ID00651","ID00652","ID00653","ID00654","ID00656","ID00657","ID00658","ID00659","ID00663","ID00664","ID00665","ID00666","ID00669","ID00670","ID00674","ID00677","ID00681","ID00682","ID00683","ID00686","ID00694","ID00696","ID00697","ID00698","ID00699","ID00700","ID00701","ID00702","ID00703","ID00704","ID00705","ID00706","ID00707","ID00708","ID00709","ID00712","ID00713","ID00714","ID00715","ID00716","ID00718","ID00719","ID00720","ID00721","ID00722","ID00723","ID00724","ID00725","ID00726","ID00727","ID00728","ID00729","ID00731","ID00732","ID00733","ID00734","ID00735","ID00737","ID00738","ID00739","ID00742","ID00743","ID00744","ID00746","ID00748","ID00749","ID00750","ID00751","ID00752","ID00753","ID00754","ID00756","ID00757","ID00759","ID00761","ID00762","ID00764","ID00765","ID00766","ID00767","ID00768","ID00769","ID00770","ID00771","ID00772","ID00774","ID00777","ID00779","ID00781","ID00782","ID00783","ID00784","ID00785","ID00786","ID00790","ID00791","ID00792","ID00793","ID00794","ID00795","ID00797","ID00798","ID00799","ID00800","ID00801","ID00802","ID00816","ID00817","ID00819","ID00821","ID00823","ID00824","ID00825","ID00828","ID00831","ID00832","ID00833","ID00839","ID00847","ID00850","ID00852","ID00853","ID00854","ID00855","ID00857","ID00858","ID00860","ID00862","ID00863","ID00865","ID00866","ID00867","ID00868","ID00870","ID00871"])
    line = ''
    for dr in drugs:
        dr = dr.replace('/', '')
        line +=f',{dr}'
    print(line)
    for sid, items in data:
        if sid not in roary_ids:
            continue
        line = sid
        for it in items:
            if len(it) > 1:
                line += ',1'
            else:
                line += ',0'
        print(line)
if __name__ == '__main__':
    main()
