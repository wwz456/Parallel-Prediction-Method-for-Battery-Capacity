# 处理每个电池（假设共有8个电池，从Cell1到Cell8）
for cell_idx in range(1, 9):
    cell_name = f'Cell{cell_idx}'
    cell_data = data[cell_name]  # 从原始数据中获取当前电池数据
    
    # 为每个电池创建单独的文件夹
    cell_dir = os.path.join(output_dir, cell_name)
    if not os.path.exists(cell_dir):
        os.makedirs(cell_dir)
    
    # 存储放电循环数据(循环号, 电压数据)
    discharge_cycles = []
    
    # 遍历所有循环
    for cycle_name in cell_data.dtype.names:
        cycle_data = cell_data[cycle_name][0, 0]
        
        # 提取放电循环的电压数据（检查是否包含放电数据）
        if 'C1dc' in cycle_data.dtype.names:  # 匹配放电数据字段
            # 提取电压数据并展平为一维数组
            voltage_data = cycle_data['C1dc'][0, 0]['v'][0, 0].flatten()
            
            # 提取循环编号（从循环名称如"cyc0000"中提取数字部分）
            cycle_number = int(cycle_name[3:])  # "cyc0000" -> 0, "cyc4000" -> 4000
            
            # 存储循环号和对应的电压数据
            discharge_cycles.append((cycle_number, voltage_data))
    
    # 按循环号从小到大排序
    discharge_cycles.sort(key=lambda x: x[0])
    
    # 保存每个循环的电压数据为npy文件
    for cycle_num, voltage_data in discharge_cycles:
        # 文件名格式：voltage_CellX_cycle_Y.npy
        filename = f"voltage_{cell_name}_cycle_{cycle_num}.npy"
        file_path = os.path.join(cell_dir, filename)
        np.save(file_path, voltage_data)
    
    print(f"已处理 {cell_name}，共保存 {len(discharge_cycles)} 个放电循环的电压数据")

# 绘制Cell1的放电电压曲线（保留你提供的可视化代码）
plt.figure(figsize=(10, 5))
plt.style.use('dark_background')

cell1_data = data['Cell1']
highlight_colors = {'cyc0000': '#FF6347', 'cyc4000': '#4682B4', 'cyc8000': '#32CD32'}
default_color = '#D3D3D3'

for cycle_name in cell1_data.dtype.names:
    cycle_data = cell1_data[cycle_name][0, 0]
    if 'C1dc' in cycle_data.dtype.names:
        voltage = cycle_data['C1dc'][0, 0]['v'][0, 0].flatten()

        if cycle_name in highlight_colors:
            plt.plot(voltage, label=f'Cycle {cycle_name[3:]}', linewidth=2.5, color=highlight_colors[cycle_name])
        else:
            plt.plot(voltage, color=default_color, alpha=0.5)

plt.title('Discharge Voltage for All Cycles of Cell 1', fontsize=16, fontweight='bold')
plt.xlabel('Time (seconds)', fontsize=14)
plt.ylabel('Discharge Voltage (V)', fontsize=14)
plt.legend(title="Highlighted Cycles", title_fontsize='10', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
