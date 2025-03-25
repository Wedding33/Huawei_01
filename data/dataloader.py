import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from math import ceil
from math import ceil

class Data:
    def __init__(self):
        file = open('./data/sample_practice.in', 'r')
        head = file.readline().strip().split()

        self.T = int(head[0])     # {T + EXTRA_TIME} timestamps, [1, 86400] = 86400
        self.M = int(head[1])     # {M} tags, [1, 16] = 16
        self.N = int(head[2])     # {N} disks, [3, 10] = 10
        self.V = int(head[3])     # {V} units, [1, 16384] = 5792
        self.G = int(head[4])     # {G} tokens, [64, 1000] = 350
        self.slice_num = ceil(self.T / 1800)

        self.del_list = [list(map(int, file.readline().strip().split())) for _ in range(self.M)]
        self.write_list = [list(map(int, file.readline().strip().split())) for _ in range(self.M)]
        self.read_list = [list(map(int, file.readline().strip().split())) for _ in range(self.M)]


        self.draw_data = [None] * self.M
        for i, (dl, wl, rl) in enumerate(zip(self.del_list, self.write_list, self.read_list)):
            self.draw_data[i] = {
                'delete': dl, 'write': wl, 'read': rl, 'total': [sum(wl[:j + 1]) - sum(dl[:j + 1]) for j in range(self.slice_num)]
            }
        for i in range(self.M):
            self.draw_data[i]['ratio'] = [(r / t) for r, t in zip(self.draw_data[i]['read'], self.draw_data[i]['total'])]

        self.statistic = {i: {'id': [], 'size': {}} for i in range(1, self.M + 1)}
        data = ''.join(file.readlines()).split('TIMESTAMP')[1:]
        data = [d.split('\n')[1:] for d in data]
        for d in data:
            n_delete = int(d[0].strip())
            pos_n_write = 1 + n_delete
            n_write = int(d[pos_n_write].strip())
            pos = 1 + pos_n_write
            while n_write > 0:
                n_write -= 1
                info = d[pos].strip().split()
                obj_id, obj_size, tag = int(info[0]), int(info[1]), int(info[2])
                self.statistic[tag]['id'].append(obj_id)
                if obj_size not in self.statistic[tag]['size']:
                    self.statistic[tag]['size'][obj_size] = 1
                else:
                    self.statistic[tag]['size'][obj_size] += 1
                pos += 1


    def show_time_varience(self):
        draw_data = self.draw_data
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
                ax.set_title(f'Data {i + 1}')

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
            plt.show()

        metrics = ['delete', 'write', 'read', 'total', 'ratio']
        # 为每个指标创建一个单独的图形
        for metric in metrics:
            plt.figure(figsize=(10, 6))
            for i in range(len(draw_data)):
                plt.plot(draw_data[i][metric], label=f'Data {i + 1}')

            plt.title(f'{metric.capitalize()} Time Variance')
            plt.xlabel('Time Slices')
            plt.ylabel(metric.capitalize())
            plt.legend()
            plt.tight_layout()
            plt.show()

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
            plt.show()

    def show_read_total(self):
        read_totals = [sum(data['read']) for data in self.draw_data]
        keys = [f'Data {i + 1}' for i in range(len(self.draw_data))]

        # 绘制柱状图
        plt.figure(figsize=(10, 6))
        sns.barplot(x=keys, y=read_totals)
        plt.title('Total Read Amount for Each Key')
        plt.xlabel('Keys')
        plt.ylabel('Total Read Amount')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_write_total(self):
        # 计算每个 key 的 delete 总量和 total 总量
        delete_totals = [sum(data['delete']) for data in self.draw_data]
        total_totals = [data['total'][-1] for data in self.draw_data]
        keys = [f'Data {i + 1}' for i in range(len(self.draw_data))]

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
        plt.show()

    def show_statistic(self):
        total_sizes, average_sizes = {}, {}
        for tag, info in self.statistic.items():
            sizes = info['size']
            total_sizes[tag] = sum([sizes[s] * s for s in sizes])
            average_sizes[tag] = total_sizes[tag] / sum([sizes[s] for s in sizes])
            print(f'tag {tag}: ', sizes, f'(total: {total_sizes[tag]} average: {average_sizes[tag]: .2f})')
        print(f'total: {sum(total_sizes.values())}')

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
        plt.show()

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
        plt.show()


data = Data()
data.show_time_varience()
# data.show_read_total()
# data.show_write_total()
data.show_statistic()