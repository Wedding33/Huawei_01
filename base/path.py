CONT_READ_TOKENS = [None, 64, 52, 42, 34, 28, 23, 19, 16]
CONT_N_READ = {token: i for i, token in enumerate(CONT_READ_TOKENS)}

CAL_READ_TOKENS_HISTORY = {}
def cal_read_tokens(pre_token: int, n_read: int, max_token=-1):
    assert n_read > 0
    global CONT_READ_TOKENS, CONT_N_READ, CAL_READ_TOKENS_HISTORY
    if (pre_token, n_read) in CAL_READ_TOKENS_HISTORY:
        return CAL_READ_TOKENS_HISTORY[(pre_token, n_read, max_token)]
    if pre_token != 16:
        # NOTE: calculate read tokens
        i = CONT_N_READ[pre_token]
        read_tokens = CONT_READ_TOKENS[i + 1: i + 1 + n_read]
        sum_read_tokens = sum(read_tokens)
        diff = n_read - len(read_tokens)
        if diff > 0:
            sum_read_tokens += 16 * diff
            read_tokens += [16] * diff

        if max_token == -1:     # no limit
            return sum_read_tokens, read_tokens[-1]
        elif max_token >= sum_read_tokens:        # tokens is enough
            return sum_read_tokens, read_tokens[-1], n_read
        
        # NOTE: tokens is limited
        j = 0
        sum_read_tokens = 0
        last_read_token = pre_token
        while (j < n_read) and (sum_read_tokens + read_tokens[j]) <= max_token:
            sum_read_tokens += read_tokens[j]
            last_read_token = read_tokens[j]
            j += 1
        return sum_read_tokens, last_read_token, j
    else:
        if max_token != -1:
            if max_token >= 16 * n_read:
                return max_token, 16, n_read
            else:
                n_read = max_token // 16
                return 16 * n_read, 16, n_read
        return 16 * n_read, 16

for pre_token in CONT_READ_TOKENS:
    pass

PATH_RESULTS = {}
def read_and_pass_diff(pre_token: int, n_pass: int, n_read: int):
    sum_read_tokens, _ = cal_read_tokens(pre_token, n_read + n_pass)

    sum_pass_tokens = n_pass + cal_read_tokens(None, n_read)[0]

    return sum_read_tokens - sum_pass_tokens

def read_instead_of_pass(pre_token: int, n_pass: int, n_read: int):
    global PATH_RESULTS
    if (pre_token, n_pass, n_read) in PATH_RESULTS:
        return PATH_RESULTS[(pre_token, n_pass, n_read)]
    else:
        ret = read_and_pass_diff(pre_token, n_pass, n_read) >= 0
        PATH_RESULTS[(pre_token, n_pass, n_read)] = ret
        return ret


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