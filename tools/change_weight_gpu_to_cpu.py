import torch


def change_feature(check_point):
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu")
    check_point = torch.load(check_point, map_location=device)
    # load_state_dict(self.model, checkpoint['state_dict'])

    import collections
    dicts = collections.OrderedDict()

    for cps in check_point:
        # ['state_dict'].items()
        # cps_items = cps.items()
        for k, value in cps.items():
            # print("names:{}".format(k))  # 打印结构
            # print("shape:{}".format(value.size()))

            if "module" in k:  # 去除命名中的module
                k = k.split(".")[1:]
                k = ".".join(k)
                print(k)
            dicts[k] = value

    torch.save(dicts, "/mnt/work/workspace/ai-blocks/lane_line/erfnet/trained/ERFNet_trained.pth")


if __name__ == "__main__":
    model_path = "./lane_line/erfnet/trained/ERFNet_trained.tar"
    change_feature(model_path)
    print('done!')
