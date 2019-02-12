#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm

from PIL import Image, ImageDraw, ImageOps

def circle(radius):
    # init vars
    switch = 3 - (2 * radius)
    points = []
    x = 0
    y = radius
    # first quarter/octant starts clockwise at 12 o'clock
    while x <= y:
        # first quarter first octant
        points.append([x,-y])
        # first quarter 2nd octant
        points.append([y,-x])
        # second quarter 3rd octant
        points.append([y,x])
        # second quarter 4.octant
        points.append([x,y])
        # third quarter 5.octant
        points.append([-x,y])        
        # third quarter 6.octant
        points.append([-y,x])
        # fourth quarter 7.octant
        points.append([-y,-x])
        # fourth quarter 8.octant
        points.append([-x,-y])
        if switch < 0:
            switch = switch + (4 * x) + 6
        else:
            switch = switch + (4 * (x - y)) + 10
            y = y - 1
        x = x + 1
    return points

def Double_circle(radius, img_array):
    # init vars
    radius
    switch = 3 - (2 * radius)
    points = []
    x = 0
    y = radius
    # first quarter/octant starts clockwise at 12 o'clock
    while x <= y:
        # first quarter first octant
        points.append(int(img_array[x,-y]+img_array[x+1,-y-1])/2)
        # first quarter 2nd octant
        points.append(int(img_array[y,-x]+img_array[y+1,-x-1])/2)
        # second quarter 3rd octant
        points.append(int(img_array[y,x]+img_array[y+1,x+1])/2)
        # second quarter 4.octant
        points.append(int(img_array[x,y]+img_array[x+1,y+1])/2)
        # third quarter 5.octant
        points.append(int(img_array[-x,y]+img_array[-x-1,y+1])/2)
        # third quarter 6.octant
        points.append(int(img_array[-y,x]+img_array[-y-1,x+1])/2)
        # fourth quarter 7.octant
        points.append(int(img_array[-y,-x]+img_array[-y-1,-x-1])/2)
        # fourth quarter 8.octant
        points.append(int(img_array[-x,-y]+img_array[-x-1,-y-1])/2)
        if switch < 0:
            switch = switch + (4 * x) + 6
        else:
            switch = switch + (4 * (x - y)) + 10
            y = y - 1
        x = x + 1
    
    # 円を一筆書きようにソートする
    sorted=[]
    for j in range(8):
        if j % 2 != 0:
            sorted.append(points[j-8::-8])
        else:
            sorted.append(points[j::8])
    return sum(sorted, [])

def pre_processing(image, size):
    image = image.resize((size, size), Image.LANCZOS)
    gray_image = image.convert('L')
    gray_array = np.asarray(gray_image)
    
    return gray_array

def circle_mean_binary(gray_array):
    
    radius = len(gray_array)//2
    
    p = []
    for i in range(radius): 
        p.append(np.asarray(Double_circle(i, gray_array)))
    
    b = []
    for i in range(len(p)):
        temp = []
        for j in range(len(p[i])):
            if p[i][j] >= p[i].sum()/len(p[i]):
                temp.append(1)
            else:
                temp.append(0)
        b.append(temp)
    return b

#一番最初の素体
def cHash(image, size=256):
    
    gray_array = pre_processing(image, size)
    
    radius = len(gray_array)//2 #radius = image//2
    
    p = []
    for i in range(radius): 
        p.append(np.asarray(Double_circle(i, gray_array)))
        
    b=[]
    for i in range(len(p)):
        temp = []
        for j in range(len(p[i])):
            if p[i][j] >= p[i].sum()/len(p[i]):
                temp.append(1)
            else:
                temp.append(0)
        b.append(temp)
    
    d=[]
    for i in range(len(b)):
        e=[]
        for j in range(len(b[i])):
            e.append(rotate(b[i], j))
        d.append(e)
    
    #循環ハッシュを求める
    c=[]
    for i in tqdm(range(len(b))):
        check = 0
        for j in range(len(b[i])):
              check += np.sum(np.logical_xor(b[i], d[i][j] == False))
        c.append(check)
    
    return c

def rotate(l, n):
    return l[n:] + l[:n]


def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result


def pre_cHash(image, size = 256):
    
    #正方形へ変形、リサイズしている
    image = image.resize((size, size), Image.LANCZOS)
    #image = expand2square(image, (0, 0, 0)).resize((size, size), Image.LANCZOS)
    
    #グレイスケール化
    gray_image = image.convert('L')
    gray_array = np.asarray(gray_image)
    
    #指定したサイズのBresenham中実円の座標を得る
    radius = len(gray_array)//2 #radius = image//2
    p = []
    for i in range(radius): 
        p.append(circle(i)) #画像の中心を(0,0)とした座標を得る
                #ここをDouble_circle関数にすると二重円の平均

    #重複を消して座標を左上を(0,0)に合わせる
    coords = []
    for i in range(len(p)):
        coords.append(np.asarray(list(map(list, set(map(tuple, p[i])))))-size//2)
    
    #Bresenham円の座標に合わせて画像からグレー値を得る
    a = []
    for i in range(len(coords)):
        temp = []
        pad_width = (0, len(max(coords, key=len))-len(coords[i]))
        for j in range(len(coords[i])):
            x, y = zip(coords[i][j])
            temp.append(gray_array[x,y])
        a.append(np.asarray(temp))
    
    #円の半径毎にグレー値の平均値を出し、平均値より上か下かで1,0を割り振る
    b = []
    for i in range(len(a)) :
        temp = []
        for j in range(len(a[i])) :
            if a[i][j] >= a[i].sum()/len(a[i]):
                temp.append(1)
            else:
                temp.append(0)
        b.append(temp)
    
    #自己相関関数を求める
    c=[]
    for i in tqdm(range(len(b))):
        check = 0
        for j in range(len(b[i])):
              check += np.sum(np.logical_xor(b[i], rotate(b[i],j)) == False)
        c.append(check)
        
    return c

def Double_cHash(image, size=256):
    image = image.resize((size, size), Image.LANCZOS)
    gray_image = image.convert('L')
    gray_array = np.asarray(gray_image)
    
    radius = len(gray_array)//2 #radius = image//2
    p = []
    for i in range(radius): 
        p.append(np.asarray(Double_circle(i, gray_array)))
        
    b=[]
    for i in range(len(p)) :
        temp = []
        for j in range(len(p[i])) :
            if p[i][j] >= p[i].sum()/len(p[i]):
                temp.append(1)
            else:
                temp.append(0)
        b.append(temp)
    
    d=[]
    for i in range(len(b)):
        for j in range(len(b[i])):
            d.append(rotate(b[i], j))
    
    
    #循環ハッシュを求める
    c=[]
    for i in tqdm(range(len(b))):
        check = 0
        for j in range(len(b[i])):
              check += np.sum(np.logical_xor(b[i], rotate(b[i],j)) == False)
        c.append(check)
    
    return c

def main():
    #pillowで画像を読み込み、そのまま関数渡す
    lena = Image.open(r'data/lena.png')
    a = pre_cHash(lena)
    #a = Double_cHash(lena)
    
    lena_left = Image.open(r'data/lena_left.png')
    b =  pre_cHash(lena_left)
    

    barbara = Image.open(r'data/Barbara.jpg')
    c =  pre_cHash(barbara)


    lenna2 = Image.open('./data/DWT_lenna2.jpg')
    d = pre_cHash(lenna2)


    lenna_DWT = Image.open('./data/DWT_lenna.png')
    e = pre_cHash(lenna_DWT)


    innocence = Image.open('./data/innocence.jpg')
    f = pre_cHash(innocence)


    lena_mirror = ImageOps.mirror(lena)
    g = pre_cHash(lena_mirror)


    # # lenna vs. lena_left
    print('lenna vs. lena_left')
    print(np.abs(np.asarray(a)-np.asarray(b)))

    print(sum(np.abs(np.asarray(a)-np.asarray(b))))


    # # lenna vs. barbara
    print('lenna vs. barbara')
    print(np.abs(np.asarray(a)-np.asarray(c)))

    print(sum(np.abs(np.asarray(a)-np.asarray(c))))


    # # lenna vs. lenna2
    print('lenna vs. lenna2')
    print(np.abs(np.asarray(a)-np.asarray(d)))

    print(sum(np.abs(np.asarray(a)-np.asarray(d))))


    # # lenna vs. resize_same
    print('lenna vs. resize_same')
    print(np.abs(np.asarray(a)-np.asarray(e)))

    print(sum(np.abs(np.asarray(a)-np.asarray(e))))


    # # lenna vs. innocence
    print('lenna vs. innocence')
    print(np.abs(np.asarray(a)-np.asarray(f)))

    print(sum(np.abs(np.asarray(a)-np.asarray(f))))


    # # lenna vs. mirror
    print('lenna vs. mirror')
    print(np.abs(np.asarray(a)-np.asarray(g)))

    print(sum(np.abs(np.asarray(a)-np.asarray(g))))


if __name__ == "__main__":
    main()