"""
根据配置同步目录
    config_path: toml配置路径
    op: 操作[pull|push]
"""
from decoherence import pathutils
import sys
import os
import pytomlpp


def load_config(conf_path):
    if not os.path.isfile(conf_path):
        raise Exception('找不到配置文件' + conf_path)

    with open(conf_path, 'r', encoding='utf-8') as f:
        dic = pytomlpp.load(f)
        print('读取配置' + conf_path + '成功')
        return dic


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('请输入参数1: 同步配置文件')
    config_path = os.path.normpath(sys.argv[1])

    if len(sys.argv) < 3:
        raise Exception('请输入参数2: 操作[pull|push]')
    op = sys.argv[2]

    syncing_dir = os.path.dirname(os.path.abspath(config_path))
    print('同步目录为' + syncing_dir)

    config_dic = load_config(config_path)

    sour_dir = None
    dest_dir = None
    if op == 'push':
        sour_dir = os.path.normpath(os.path.join(syncing_dir, config_dic['destiny']))
        dest_dir = os.path.normpath(os.path.join(syncing_dir, config_dic['source']))
    elif op == 'pull':
        sour_dir = os.path.normpath(os.path.join(syncing_dir, config_dic['source']))
        dest_dir = os.path.normpath(os.path.join(syncing_dir, config_dic['destiny']))
    else:
        Exception(op + '为非法操作')

    print('sync ' + sour_dir + ' -> ' + dest_dir)

    ignore_paths = None
    if 'ignore_paths' in config_dic.keys():
        ignore_paths = config_dic['ignore_paths']

    sync_paths = None
    if 'sync_paths' in config_dic.keys():
        sync_paths = config_dic['sync_paths']

    syncer = pathutils.PathSyncer(sour_dir, dest_dir, sync_paths, ignore_paths)
    syncer.sync()
