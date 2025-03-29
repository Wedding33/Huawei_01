import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from math import ceil

class Data:
    def __init__(self, path, folder):
        file = open(path, 'r')
        head = file.readline().strip().split()

        self.folder = folder

        self.T = int(head[0])     # {T + EXTRA_TIME} timestamps, [1, 86400] = 86400
        self.M = int(head[1])     # {M} tags, [1, 16] = 16
        self.N = int(head[2])     # {N} disks, [3, 10] = 10
        self.V = int(head[3])     # {V} units, [1, 16384] = 5792
        self.G = int(head[4])     # {G} tokens, [64, 1000] = 350
        self.slice_num = ceil(self.T / 1800)

        self.del_list = [list(map(int, file.readline().strip().split())) for _ in range(self.M)]
        self.write_list = [list(map(int, file.readline().strip().split())) for _ in range(self.M)]
        self.read_list = [list(map(int, file.readline().strip().split())) for _ in range(self.M)]

        # self.section_map = {
        #     1: {'tag': [1, 15, 16], 'weight': [1, 1, 1]},
        #     2: {'tag': [2, 3, 5], 'weight': [1, 1, 1]},
        #     3: {'tag': [6, 7, 8], 'weight': [1, 1, 1]},
        #     4: {'tag': [12, 13], 'weight': [1, 1]},
        #     5: {'tag': [9, 10, 11], 'weight': [1, 1, 1]},
        #     6: {'tag': [4, 14], 'weight': [1, 1]},
        # }
        self.section_map = {
            1: {'tag': [1, 4], 'weight': [1/3, 1/3]},
            2: {'tag': [2, 3, 5, 6, 7, 11, 15], 'weight': [1/3, 1/3, 1/3, 2/3, 2/3, 1/3, 1/3]},
            3: {'tag': [1, 5, 7, 12, 14, 15], 'weight': [1/3, 1/3, 1/3, 2/3, 1/3, 1/3]},
            4: {'tag': [3, 8, 10, 13, 16], 'weight': [1/3, 1/3, 1/3, 1/3, 1/3]},
            5: {'tag': [1, 5, 9, 10, 11, 14], 'weight': [1/3, 1/3, 1/3, 1/3, 1/3, 1/3]},
            6: {'tag': [2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16], 'weight': [1/3, 1/3, 1/3, 2/3, 1/3, 1/3, 1/3, 1/3, 2/3, 1/3, 1/3, 1/3]},
            7: {'tag': [2, 3, 16, 4, 9], 'weight': [1/3, 1/3, 1/3, 1/3, 1/3]},
        }
        self.inverse_map = dict()
        for i in range(1, len(self.section_map.keys()) + 1):
            for tag, w in zip(self.section_map[i]['tag'], self.section_map[i]['weight']):
                if tag not in self.inverse_map: self.inverse_map[tag] = {i: w}
                self.inverse_map[tag][i] = w

        basic_keys = ['delete', 'write', 'read', 'total']
        self.raw_data: List[Dict] = [None] * self.M
        for i, (dl, wl, rl) in enumerate(zip(self.del_list, self.write_list, self.read_list)):
            self.raw_data[i] = {
                'delete': dl, 'write': wl, 'read': rl, 'total': [sum(wl[:j + 1]) - sum(dl[:j + 1]) for j in range(self.slice_num)]
            }
        for i in range(self.M):
            self.raw_data[i]['ratio'] = [(r / t) for r, t in zip(self.raw_data[i]['read'], self.raw_data[i]['total'])]
        self.raw_data = [None] + self.raw_data
        self.raw_data[0] = {
            key: [sum([self.raw_data[j][key][i] for j in range(1, self.M + 1)]) for i in range(self.slice_num)]
            for key in basic_keys
        }

        self.mapped_raw_data = []

        # self.statistic = {i: {'id': [], 'size': {}} for i in range(1, self.M + 1)}
        self.tag_and_size_of_id = {}
        self.statistic_tag: Dict[int, Dict[str, List]] = {i: {'count': 0, 'total_size': [], 'request_size': [], 'max_total_size': 0, 'size': {}} for i in range(1, 17)}
        self.statistic_sec: Dict[int, Dict[str, List]] = {i: {'count': 0, 'total_size': [], 'request_size': [], 'max_total_size': 0, 'size': {}} for i in range(1, 8)}
        
        data = ''.join(file.readlines()).split('TIMESTAMP')[1:]
        data = [d.split('\n')[1:] for d in data]
        cnt = 0
        for d in data:
            for k in self.statistic_tag:
                self.statistic_tag[k]['total_size'].append(0 if cnt == 0 else self.statistic_tag[k]['total_size'][-1])
                self.statistic_tag[k]['request_size'].append(0)
            for k in self.statistic_sec:
                self.statistic_sec[k]['total_size'].append(0 if cnt == 0 else self.statistic_sec[k]['total_size'][-1])
                self.statistic_sec[k]['request_size'].append(0)
            cnt += 1

            n_delete = int(d[0].strip())
            for i in range(n_delete):
                obj_id = int(d[i + 1].strip().split()[0])
                tag, size = self.tag_and_size_of_id[obj_id]
                self.statistic_tag[tag]['count'] -= 1
                self.statistic_tag[tag]['size'][size] -= 1
                self.statistic_tag[tag]['total_size'][-1] -= size
                for sec_id in self.inverse_map[tag]:
                    weight = self.inverse_map[tag][sec_id]
                    self.statistic_sec[sec_id]['count'] -= weight
                    self.statistic_sec[sec_id]['size'][size] -= weight
                    self.statistic_sec[sec_id]['total_size'][-1] -= weight * size

            pos_n_write = 1 + n_delete
            n_write = int(d[pos_n_write].strip())
            pos = 1 + pos_n_write
            while n_write > 0:
                n_write -= 1
                info = d[pos].strip().split()
                obj_id, obj_size, tag = int(info[0]), int(info[1]), int(info[2])
                self.tag_and_size_of_id[obj_id] = (tag, obj_size)
                if obj_size not in self.statistic_tag[tag]['size']:
                    self.statistic_tag[tag]['size'][obj_size] = 1
                else:
                    self.statistic_tag[tag]['size'][obj_size] += 1
                self.statistic_tag[tag]['total_size'][-1] += obj_size
                self.statistic_tag[tag]['count'] += 1
                self.statistic_tag[tag]['max_total_size'] = max(self.statistic_tag[tag]['max_total_size'], self.statistic_tag[tag]['total_size'][-1])
                for sec_id in self.inverse_map[tag]:
                    weight = self.inverse_map[tag][sec_id]
                    # self.statistic[sec_id]['id'].append(obj_id)
                    if obj_size not in self.statistic_sec[sec_id]['size']:
                        self.statistic_sec[sec_id]['size'][obj_size] = weight
                    else:
                        self.statistic_sec[sec_id]['size'][obj_size] += weight
                    self.statistic_sec[sec_id]['count'] += weight
                    self.statistic_sec[sec_id]['total_size'][-1] += weight * obj_size
                    self.statistic_sec[sec_id]['max_total_size'] = max(self.statistic_sec[sec_id]['max_total_size'], self.statistic_sec[sec_id]['total_size'][-1])
                pos += 1

            n_read = int(d[pos].strip().split()[0])
            for i in range(n_read):
                info = d[pos + i + 1].strip().split()
                req_id, obj_id = int(info[0]), int(info[1])
                tag, size = self.tag_and_size_of_id[obj_id]
                self.statistic_tag[tag]['request_size'][-1] += (size + 1) * 0.5
                for sec_id in self.inverse_map[tag]:
                    weight = self.inverse_map[tag][sec_id]
                    # self.statistic[sec_id]['id'].append(obj_id)
                    self.statistic_sec[sec_id]['request_size'][-1] += (size + 1) * 0.5 * weight


        self.statistic_total_size = {i: {'size': {size: self.statistic_tag[i]['size'][size] * size for size in self.statistic_tag[i]['size']} } for i in range(1, 8)}


    def show_statistic_trends(self, data, rows=2, cols=3, move_average_obj=10, move_average_req=100, notation='tag'):
        num_tags = len(data)
        figures_per_page = rows * cols
        num_figures = num_tags // figures_per_page + (1 if num_tags % figures_per_page != 0 else 0)

        for fig_idx in range(num_figures):
            start_idx = fig_idx * figures_per_page
            end_idx = min(start_idx + figures_per_page, num_tags)
            fig, axes = plt.subplots(rows, cols, figsize=(15, 10))
            axes = axes.flatten()

            for i in range(start_idx, end_idx):
                tag = i + 1
                ax = axes[i - start_idx]

                # 计算移动平均
                total_size = np.array(data[tag]['total_size'])
                request_size = np.array(data[tag]['request_size'])
                total_size_ma = np.convolve(total_size, np.ones(move_average_obj)/move_average_obj, mode='valid')
                request_size_ma = np.convolve(request_size, np.ones(move_average_req)/move_average_req, mode='valid')

                # 绘制 total_size 到第一个坐标轴
                line1, = ax.plot(total_size_ma, label='Total Size (MA)', color='blue')
                ax.set_ylabel('Total Size', color='blue')
                ax.tick_params(axis='y', labelcolor='blue')
                ax.set_title(f'{notation} {tag} Trends')
                ax.set_xlabel('Time')

                # 创建第二个坐标轴
                ax2 = ax.twinx()
                # 绘制 request_size 到第二个坐标轴
                line2, = ax2.plot(request_size_ma, label='Request Size (MA)', color='red')
                ax2.set_ylabel('Request Size', color='red')
                ax2.tick_params(axis='y', labelcolor='red')

                # 合并两个坐标轴的图例
                lines = [line1, line2]
                labels = [l.get_label() for l in lines]
                ax.legend(lines, labels, loc='upper left')

            plt.tight_layout()
            # 保存图片
            plt.savefig(self.folder + f'/statistic_{notation}_trends_{fig_idx}.png')
            plt.show()

    def show_statistic_tag_and_sec_trends(self, move_average_obj=10, move_average_req=100):
        self.show_statistic_trends(self.statistic_tag, rows=2, cols=4, move_average_obj=move_average_obj, move_average_req=move_average_req, notation='tag')
        self.show_statistic_trends(self.statistic_sec, rows=2, cols=4, move_average_obj=move_average_obj, move_average_req=move_average_req, notation='sec')


# ... existing code ...
    def show_time_varience(self):
        draw_data = self.raw_data
        num_figures = len(draw_data) // 6 + (1 if len(draw_data) % 6 != 0 else 0)
        for fig_idx in range(num_figures):
            start_idx = fig_idx * 6
            end_idx = min(start_idx + 6, len(draw_data))
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            axes = axes.flatten()

            for i in range(start_idx, end_idx):
                ax = axes[i - start_idx]
                # 绘制 write、delete 和 total 到第一个坐标轴
                lines = []
                for key in ['delete', 'write', 'total']:
                    line, = ax.plot(draw_data[i][key], label=key)
                    lines.append(line)
                ax.set_ylabel('Delete, Write, Total')
                ax.set_title(f'Data {i}' if i > 0 else 'Sum')

                # 创建第二个坐标轴
                ax2 = ax.twinx()
                # 绘制 read 到第二个坐标轴
                line, = ax2.plot(draw_data[i]['read'], label='read', color='red')
                lines.append(line)
                ax2.set_ylabel('Read')

                # 合并两个坐标轴的图例
                labels = [l.get_label() for l in lines]
                ax.legend(lines, labels, loc='upper left')

            plt.tight_layout()
            # 保存图片
            plt.savefig(self.folder + f'/time_varience_{fig_idx}.png')
            # plt.show()

        metrics = ['delete', 'write', 'read', 'total', 'ratio']
        types = {'large': {}, 'small': {}}
        for i in range(1, len(draw_data)):
            if draw_data[i]['write'][0] > 750:
                types['large'][i] = draw_data[i]['write'][0]
            else:
                types['small'][i] = draw_data[i]['write'][0]
        print(types)
        
        # 为每个指标创建一个单独的图形
        for metric in metrics:
            plt.figure(figsize=(10, 6))
            for i in range(len(draw_data)):
                plt.plot(draw_data[i][metric], label=f'Data {i}' if i > 0 else 'Sum')

            plt.title(f'{metric.capitalize()} Time Variance')
            plt.xlabel('Time Slices')
            plt.ylabel(metric.capitalize())
            plt.legend()
            plt.tight_layout()
            # 保存图片
            plt.savefig(self.folder + f'/{metric}_time_variance.png')
            # plt.show()

        for metric in metrics:
            # 创建一个空的 DataFrame 用于存储每个数据点
            df = pd.DataFrame()
            for i in range(len(draw_data)):
                df[f'Data {i + 1}'] = draw_data[i][metric]

            # 绘制堆叠折线图
            plt.figure(figsize=(10, 6))
            df.plot(kind='area', stacked=True, ax=plt.gca())
            plt.title(f'{metric.capitalize()} Time Variance (Stacked)')
            plt.xlabel('Time Slices')
            plt.ylabel(metric.capitalize())
            plt.legend()
            plt.tight_layout()
            # 保存图片
            plt.savefig(self.folder + f'/{metric}_time_variance_stacked.png')
            # plt.show()

    def show_read_total(self):
        read_totals = [sum(data['read']) for data in self.raw_data]
        keys = [f'Data {i + 1}' for i in range(len(self.raw_data))]

        # 绘制柱状图
        plt.figure(figsize=(10, 6))
        sns.barplot(x=keys, y=read_totals)
        plt.title('Total Read Amount for Each Key')
        plt.xlabel('Keys')
        plt.ylabel('Total Read Amount')
        plt.xticks(rotation=45)
        plt.tight_layout()
        # 保存图片
        plt.savefig(self.folder + '/read_total.png')
        # plt.show()

    def show_write_total(self):
        # 计算每个 key 的 delete 总量和 total 总量
        delete_totals = [sum(data['delete']) for data in self.raw_data]
        total_totals = [data['total'][-1] for data in self.raw_data]
        keys = [f'Data {i + 1}' for i in range(len(self.raw_data))]

        # 创建 DataFrame 用于绘图
        df = pd.DataFrame({
            'Keys': keys,
            'Total': total_totals,
            'Delete': delete_totals
        })

        # 绘制堆叠柱状图
        plt.figure(figsize=(10, 6))
        bottom = df['Total']
        plt.bar(df['Keys'], df['Total'], label='Total')
        plt.bar(df['Keys'], df['Delete'], bottom=bottom, label='Delete')

        plt.title('Stacked Bar Chart of Total and Delete Amounts for Each Key')
        plt.xlabel('Keys')
        plt.ylabel('Amount')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        # 保存图片
        plt.savefig(self.folder + '/write_total.png')
        # plt.show()

    def show_statistic(self):
        total_sizes, average_sizes = {}, {}
        for tag, info in self.statistic.items():
            sizes = info['size']
            total_sizes[tag] = sum([sizes[s] * s for s in sizes])
            average_sizes[tag] = total_sizes[tag] / sum([sizes[s] for s in sizes])
        for tag, info in self.statistic.items():
            print(f'tag {tag}: ', sizes, f'(total: {total_sizes[tag]} proportion: {total_sizes[tag] / sum(total_sizes.values())}, average: {average_sizes[tag]: .2f})')
        print(f'total: {sum(total_sizes.values())}')

        data = []
        sizes = set()
        for tag, info in self.statistic_total_size.items():
            size_counts = info['size']
            row = {'tag': tag}
            for size, count in size_counts.items():
                row[size] = count
                sizes.add(size)
            data.append(row)

        df = pd.DataFrame(data)
        df = df.set_index('tag')
        df = df.fillna(0)

        # 按列名（即 size）升序排序
        df = df.reindex(sorted(df.columns), axis=1)

        plt.figure(figsize=(10, 6))
        df.plot(kind='bar', stacked=True, ax=plt.gca())

        plt.title('Stacked Bar Chart of Size Distribution for Each Tag')
        plt.xlabel('Tags')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Sizes')
        plt.tight_layout()
        # 保存图片
        plt.savefig(self.folder + '/size_distribution_by_tag.png')
        # plt.show()

        data = []
        sizes = set()
        for tag, info in self.statistic.items():
            size_counts = info['size']
            row = {'tag': tag}
            for size, count in size_counts.items():
                row[size] = count
                sizes.add(size)
            data.append(row)

        df = pd.DataFrame(data)
        df = df.set_index('tag')
        df = df.fillna(0)

        # 转置 DataFrame，使得列是 tag，行是 size
        df = df.T

        # 按 tag 升序排列
        df = df.reindex(sorted(df.columns), axis=1)

        plt.figure(figsize=(10, 6))
        df.plot(kind='bar', stacked=True, ax=plt.gca())

        plt.title('Stacked Bar Chart of Tag Distribution for Each Size')
        plt.xlabel('Sizes')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Tags')
        plt.tight_layout()
        # 保存图片
        plt.savefig(self.folder + '/tag_distribution_by_size.png')
        # plt.show()


# data = Data('./data/sample_practice.in', './fig/practice')
data = Data('./data/sample_official.in', './fig/official')
# data.show_time_varience()
# data.show_read_total()
# data.show_write_total()
# data.show_statistic()
data.show_statistic_tag_and_sec_trends()