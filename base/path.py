CONT_READ_TOKENS = [64, 52, 42, 34, 28, 23, 19, 16]

def read_and_pass_diff(pre_token: int, n_pass: int, n_read: int):
    for i in range(len(CONT_READ_TOKENS)):
        if CONT_READ_TOKENS[i] == pre_token:
            break

    read_tokens = CONT_READ_TOKENS[i + 1: i + 1 + n_pass + n_read]
    sum_read_tokens = sum(read_tokens)
    if len(read_tokens) < n_pass + n_read:
        sum_read_tokens += 16 * (n_pass + n_read - len(read_tokens))

    sum_pass_tokens = n_pass + sum(CONT_READ_TOKENS[:n_read])

    return sum_read_tokens - sum_pass_tokens


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    # 定义 n_pass 和 n_read 的范围
    n_pass_values = [1, 2, 3, 4]
    n_read_values = list(range(1, 16))

    for j in range(2):
        # 创建一个 2x2 的子图布局
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # 遍历前 4 个 pre_token 值
        for i, pre_token in enumerate(CONT_READ_TOKENS[j * 4: (j + 1) * 4]):
            row = i // 2
            col = i % 2
            ax = axes[row, col]

            # 绘制不同 n_pass 的折线
            for n_pass in n_pass_values:
                results = [read_and_pass_diff(pre_token, n_pass, n_read) for n_read in n_read_values]
                ax.plot(n_read_values, results, label=f'n_pass = {n_pass}')

            ax.set_title(f'pre_token = {pre_token}')
            ax.set_xlabel('n_read')
            ax.set_ylabel('read_and_pass_diff')
            ax.legend()
            # 添加网格
            ax.grid(True)

        plt.tight_layout()
        plt.show()