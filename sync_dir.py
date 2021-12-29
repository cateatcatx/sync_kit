import sys
import pytomlpp
import os
import shutil

g_sour_dir = None
g_dest_dir = None
g_ignores = None

def load_config(dir):
    path = os.path.join(dir, 'SyncDecoherence.toml')
    if not os.path.isfile(path):
        raise Exception('找不到配置文件' + path)
    
    with open(path, 'r', encoding = 'utf-8') as f:
        dic = pytomlpp.load(f)
        print('读取配置' + path + '成功')
        return dic


def remove_path(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def sync_dir(sour, dest):
    if is_path_ignored(sour):
        if os.path.exists(dest):
            remove_path(dest)
        return

    if os.path.isfile(dest):
        os.remove(dest)
    
    # 创建目标目录
    need_del = True
    if not os.path.isdir(dest):
        need_del = False # 新建的目录没必要再检查删除的文件
        print('mkdir ' + dest)
        os.makedirs(dest)

    # 拷贝新增或修改的文件
    for p in os.listdir(sour):
        sour_path = os.path.join(sour, p)
        dest_path = os.path.join(dest, p)

        if os.path.isfile(sour_path) and not is_path_ignored(sour_path):
            print(sour_path + ' -> ' + dest_path)
            shutil.copy(sour_path, dest_path)
        elif os.path.isdir(sour_path):
            sync_dir(sour_path, dest_path)
    
    # 删除多余的文件
    if need_del:
        for p in os.listdir(dest):
            sour_path = os.path.join(sour, p)
            dest_path = os.path.join(dest, p)
            if os.path.exists(dest_path) and (not os.path.exists(sour_path) or is_path_ignored(sour_path)):
                print('del ' + dest_path)
                remove_path(dest_path)


def sync_file(sour, dest):
    if os.path.isfile(sour) and not is_path_ignored(sour):
        print(sour + ' -> ' + dest)
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        shutil.copy(sour, dest)
    else:
        print('del ' + dest)
        remove_path(dest)


def sync(sour_path, dest_path):
    if os.path.isdir(sour_path):
        sync_dir(sour_path, dest_path)
    else:
        sync_file(sour_path, dest_path)

def is_path_ignored(path):
    global g_sour_dir
    global g_ignores

    rpath = os.path.relpath(path, g_sour_dir)
    for ignore in g_ignores:
        if os.path.normpath(ignore) == os.path.normpath(rpath):
            return True
    return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('请输入参数1: 待同步目录')
    dir = os.path.normpath(sys.argv[1])

    if len(sys.argv) < 3:
        raise Exception('请输入参数2: 操作[pull|push]')
    op = sys.argv[2]

    print('输入目录为' + dir)

    config_dic = load_config(dir)

    
    if op == 'push':
        g_sour_dir = os.path.normpath(os.path.join(dir, config_dic['destiny']))
        g_dest_dir = os.path.normpath(os.path.join(dir, config_dic['source']))
    elif op == 'pull':
        g_sour_dir = os.path.normpath(os.path.join(dir, config_dic['source']))
        g_dest_dir = os.path.normpath(os.path.join(dir, config_dic['destiny']))
    else:
        Exception(op + '为非法操作')

    g_ignores = config_dic['ignores']
    
    print('sync ' + g_sour_dir + ' -> ' + g_dest_dir)
    paths = config_dic['paths']
    for path in paths:
        sync(os.path.normpath(os.path.join(g_sour_dir, path)), os.path.normpath(os.path.join(g_dest_dir, path)))