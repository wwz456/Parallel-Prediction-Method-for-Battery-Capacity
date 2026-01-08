import glob
import numpy as np
import pandas as pd
import os

# 去除异常点
def drop_outlier(array, bins):
    index = []
    range_ = np.arange(0, len(array), bins)  # 从 0 开始
    for start_index in range_:
        end_index = start_index + bins
        array_lim = array[start_index:end_index]
        sigma = np.std(array_lim)
        mean = np.mean(array_lim)
        th_max, th_min = mean + sigma * 2, mean - sigma * 2
        idx = np.where((array_lim < th_max) & (array_lim > th_min))[0]
        idx = idx + start_index
        index.extend(idx)
    return np.array(index, dtype=int)  # 确保返回值是整数类型

# 加载数据
def load_data(Battery_list, dir_path):
    Battery = {}
    for name in Battery_list:
        print('Load Dataset ' + name + ' ...')
        full_path = os.path.join(dir_path, name, "*.xlsx")  # 使用 os.path.join 拼接路径
        print("Full path:", full_path)
        path = glob.glob(full_path)
        print("Files found:", path)
        if not path:
            print(f"No files found for {name}. Please check the directory and file names.")
            continue

        dates = []
        for p in path:
            df = pd.read_excel(p, sheet_name=1)
            dates.append(df['Date_Time'][0])
        idx = np.argsort(dates)
        path_sorted = np.array(path)[idx]
        print(path_sorted)
        discharge_capacities = []
        health_indicator = []
        internal_resistance = []
        CCCT = []
        CVCT = []

        for p in path_sorted:
            df = pd.read_excel(p, sheet_name=1)
            print('Load ' + str(p) + ' ...')
            cycles = list(set(df['Cycle_Index']))
            print(cycles)
            '''
            “Current”这一栏所在的数据为正即为充电过程，为负即为放电过程。
            为了研究人员更容易区分充放电过程，实验人员建立了“Step index”这一栏，
            其中：'2'和'4'表示稳定的恒压过程，即充电过程；
            而'7'则表示稳定的恒流过程，即放电过程。
            当然，对于其他的数据，不一定用数字'7'表示恒流过程,
            '''
            for c in cycles:
                df_lim = df[df['Cycle_Index'] == c]
                df_c = df_lim[(df_lim['Step_Index'] == 2) | (df_lim['Step_Index'] == 4)]
                df_cc = df_lim[df_lim['Step_Index'] == 2]
                df_cv = df_lim[df_lim['Step_Index'] == 4]
                CCCT.append(np.max(df_cc['Test_Time(s)']) - np.min(df_cc['Test_Time(s)']))# 恒流充电阶段
                CVCT.append(np.max(df_cv['Test_Time(s)']) - np.min(df_cv['Test_Time(s)']))# 恒压充电阶段

                df_d = df_lim[df_lim['Step_Index'] == 7]# 放电阶段
                if len(df_d['Current(A)']) < 2:
                    print(f"Insufficient data in file {p}. Skipping this cycle.")
                    continue

                time_diff = np.diff(df_d['Test_Time(s)'])
                discharge_capacity = np.cumsum(time_diff * df_d['Current(A)'][1:] / 3600)
                if len(discharge_capacity) == 0:
                    print(f"No discharge capacity data in file {p}. Skipping this cycle.")
                    continue

                discharge_capacities.append(-discharge_capacity.iloc[-1])

                start = discharge_capacity[np.argmin(np.abs(df_d['Voltage(V)'] - 3.8))]
                end = discharge_capacity[np.argmin(np.abs(df_d['Voltage(V)'] - 3.4))]
                health_indicator.append(-(end - start))

                internal_resistance.append(np.mean(df_d['Internal_Resistance(Ohm)']))

        discharge_capacities = np.array(discharge_capacities)
        health_indicator = np.array(health_indicator)
        internal_resistance = np.array(internal_resistance)
        CCCT = np.array(CCCT)
        CVCT = np.array(CVCT)

        idx = drop_outlier(discharge_capacities, 40)
        print("discharge_capacities length:", len(discharge_capacities))
        print("health_indicator length:", len(health_indicator))
        print("internal_resistance length:", len(internal_resistance))
        print("CCCT length:", len(CCCT))
        print("CVCT length:", len(CVCT))
        print("idx length:", len(idx))
        print("idx type:", idx.dtype)

        if len(idx) == 0:
            print(f"No valid indices for {name}. Skipping...")
            continue

        df_result = pd.DataFrame({
            'cycle': np.arange(1, len(idx) + 1, dtype=int),
            'capacity': discharge_capacities[idx],
            'SoH': health_indicator[idx],
            'resistance': internal_resistance[idx],
            'CCCT': CCCT[idx],
            'CVCT': CVCT[idx]
        })
        Battery[name] = df_result

    return Battery

# 定义电池列表和路径
Battary_list = ['CS2_35', 'CS2_36', 'CS2_37', 'CS2_38']
dir_path = r'D:\DATASETS\BATTERY'  # 使用原始字符串
Battery = load_data(Battary_list, dir_path)
