#!/usr/bin/env python
#coding: utf-8
import pygame
from pygame.locals import *
import os
import sys
import threading
import time

SCR_RECT = Rect(0, 0, 900, 700) 
ISGAMEOVER =False
LIMIT=102

class PyAction:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCR_RECT.size)
        pygame.display.set_caption("100秒後に死ぬワニ")

        #カーソルを出さない
        pygame.mouse.set_visible(False)
        
        # 画像のロード
        Python.left_image = load_image("wani.bmp", None)                    # 左向き
        Python.right_image = pygame.transform.flip(Python.left_image, 1, 0)  # 右向き
        Block.image = load_image("block.png", None)
        Cloud.image = load_image("cloud.png",-1)
        king.image=load_image("king.png",-1)
        dokan.image=load_image("dokan.png",-1)
        hiyoko.image=load_image("hiyoko.png",-1)
        goal.image=load_image("goal.bmp",-1)
        self.over_image=load_image("gameover.png",-1)
        self.over_car=load_image("car.png",-1)


        # マップのロード
        self.map = Map("data/test.map")

        #サウンドのロード
        game_over_sound=pygame.mixer.Sound("data/IWBG.wav")
        s = Sound()
        s.set_sound(game_over_sound)

        #フォントの設定
        self.font = pygame.font.Font(None, 55)  

        # BGMを再生
        pygame.mixer.music.load("data/stage.mp3")
        pygame.mixer.music.play(-1)

        


       
        # メインループ
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            global ISGAMEOVER
            global LIMIT
            #LIMIT-=1
            if(LIMIT==0):
                ISGAMEOVER=True
            self.update()
            self.draw(self.screen)
            pygame.display.update()
            self.key_handler()
            if(ISGAMEOVER==True):
                self.game_over()
            

    def update(self):
        self.map.update()
    
    def draw(self, screen):
        self.map.draw()
    
        
        # オフセッとに基づいてマップの一部を画面に描画
        offsetx, offsety = self.map.calc_offset()
        
        # 端ではスクロールしない
        if offsetx < 0:
            offsetx = 0
        elif offsetx > self.map.width - SCR_RECT.width:
            offsetx = self.map.width - SCR_RECT.width
        
        if offsety < 0:
            offsety = 0
        elif offsety > self.map.height - SCR_RECT.height:
            offsety = self.map.height - SCR_RECT.height
        
        # マップの一部を画面に描画
        screen.blit(self.map.surface, (0,0), (offsetx, offsety, SCR_RECT.width, SCR_RECT.height))

        text = self.font.render('{} second'.format(int(LIMIT)), True, (255,255,255))   # 描画する文字列の設定
        self.screen.blit(text, [680, 0])# 文字列の表示位置

        
    


    
       
    def key_handler(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
    def game_over(self): #ゲームオーバー
        global ISGAMEOVER
        ISGAMEOVER = False
        global LIMIT

        #BGM終了
        pygame.mixer.music.stop()
        s = Sound()
        sound=s.get_sound(0)
        sound.play()

        #描画
        #elf.screen.blit(self.over_car,(0,Python.get_POS()[1]-100))
        for i in range(0,int(SCR_RECT[2]/2),20):
            self.draw(self.screen)
            self.screen.blit(self.over_image,(75,300))
            self.screen.blit(self.over_car, (i,Python.get_POS()[1]-100))
            pygame.display.update()
         
        while(True):
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key ==K_r:
                    #サウンドが流れていたら終了
                    pygame.mixer.stop()
        
                    PyAction()
   
            


class Python(pygame.sprite.Sprite):
    """パイソン"""
    MOVE_SPEED = 3.5    # 移動速度
    JUMP_SPEED = 8.0    # ジャンプの初速度
    GRAVITY = 0.3       # 重力加速度
    MAX_JUMP_COUNT = 1  # ジャンプ段数の回数
    X=0
    Y=0
    animcycle = 12  # アニメーション速度
    frame = 0
    global ISGAMEOVER
    
    
    def __init__(self, pos, blocks,enemies):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = split_image(self.right_image)
        self.image=self.images[0]
        self.images_left=split_image(self.left_image)
        self.image_left = self.images_left[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]  # 座標設定
        self.blocks = blocks  # 衝突判定用
        self.enemies=enemies

   
        
        # ジャンプ回数
        self.jump_count = 0
        
        # 浮動小数点の位置と速度
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.fpvx = 0.0
        self.fpvy = 0.0
        
        # 地面にいるか？
        self.on_floor = False
        
    def update(self):
        """スプライトの更新"""
        self.frame += 1
        self.number = int((self.frame/self.animcycle)%2)
        self.image = self.images[self.number]
        # キー入力取得
        pressed_keys = pygame.key.get_pressed()
        
        # 左右移動
        if pressed_keys[K_RIGHT]:
            self.image = self.images[self.number]
            self.fpvx = self.MOVE_SPEED
            
        elif pressed_keys[K_LEFT]:
            self.image = self.images_left[self.number]
            self.fpvx = -self.MOVE_SPEED
        else:
            self.fpvx = 0.0
        
        
        # ジャンプ
        if pressed_keys[K_SPACE]:
            if self.on_floor:
                self.fpvy = - self.JUMP_SPEED  # 上向きに初速度を与える
                self.on_floor = False
                self.jump_count = 1
            elif not self.prev_button and self.jump_count < self.MAX_JUMP_COUNT:
                self.fpvy = -self.JUMP_SPEED
                self.jump_count += 1
            
        # 速度を更新
        if not self.on_floor:
            self.fpvy += self.GRAVITY  # 下向きに重力をかける
        
        self.collision_x()  # X方向の衝突判定処理
        self.collision_y()  # Y方向の衝突判定処理
        
        # 浮動小数点の位置を整数座標に戻す
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)

        Python.X=self.rect.x
        Python.Y=self.rect.y

        
        # ボタンのジャンプキーの状態を記録
        self.prev_button = pressed_keys[K_SPACE]
    
        
    def collision_x(self):
        """X方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width
        height = self.rect.height
        
        # X方向の移動先の座標と矩形を求める
        newx = self.fpx + self.fpvx
        newrect = Rect(newx, self.fpy, width, height)

        self.collide_x=False

         # 敵との衝突判定
        for enemy in self.enemies:
            collide = newrect.colliderect(enemy.rect)
            if collide:  # 衝突する敵あり
                
                if self.fpvx > 0:    # 右に移動中に衝突
                    # 終了
                    ISGAMEOVER=True
                elif self.fpvx < 0:  # 左に移動中に衝突
                    # 終了
                    ISGAMEOVER=True
                  
                break  # 衝突は1個調べれば十分
            else:
                # 衝突がない場合、パス
                pass
        
        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvx > 0:    # 右に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpx = block.rect.left - width
                    self.fpvx = 0
                    collide_x=True
                elif self.fpvx < 0:  # 左に移動中に衝突
                    self.fpx = block.rect.right
                    self.fpvx = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpx = newx
                self.collide_x=False
        
    
    def collision_y(self):
        """Y方向の衝突判定処理"""
        # パイソンのサイズ
        width = self.rect.width
        height = self.rect.height
        
        # Y方向の移動先の座標と矩形を求める
        newy = self.fpy + self.fpvy
        newrect = Rect(self.fpx, newy, width, height)

        # 敵との衝突判定
        for enemy in self.enemies:
            collide = newrect.colliderect(enemy.rect)
            if collide:  # 衝突する敵あり
                global ISGAMEOVER
                if self.fpvy > 0:    # 下に移動中に衝突
                    # 終了
                    ISGAMEOVER=True
                elif self.fpvy < 0:  # 上に移動中に衝突
                    # 終了
                    ISGAMEOVER=True
                  
                break  # 衝突は1個調べれば十分
            else:
                # 衝突がない場合、パス
                pass
        
        # ブロックとの衝突判定
        for block in self.blocks:
            collide = newrect.colliderect(block.rect)
            if collide:  # 衝突するブロックあり
                if self.fpvy > 0:    # 下に移動中に衝突
                    # めり込まないように調整して速度を0に
                    self.fpy = block.rect.top - height
                    self.fpvy = 0
                    # 下に移動中に衝突したなら床の上にいる
                    self.on_floor = True
                    self.jump_count = 0  # ジャンプカウントをリセット
                elif self.fpvy < 0:  # 上に移動中に衝突
                    self.fpy = block.rect.bottom
                    self.fpvy = 0
                break  # 衝突ブロックは1個調べれば十分
            else:
                # 衝突ブロックがない場合、位置を更新
                self.fpy = newy
                # 衝突ブロックがないなら床の上にいない
                self.on_floor = False

        #穴に落ちたか判定
        if(self.fpy>800):
            ISGAMEOVER=True
    def get_POS():
        return (Python.X,Python.Y)

    
class Sound:
    sound_list = []
    def __init__(self):
        pass
    def set_sound(self,sound):
        self.sound_list.append(sound)
    def get_sound(self,i):
        return self.sound_list[i]

    #0:ゲームオーバー
        
    


class Block(pygame.sprite.Sprite):
    """ブロック"""
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
class king(Block):
     pass
class dokan(Block):
    pass


class Enemy(pygame.sprite.Sprite):
    """エネミー"""
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

class hiyoko(Enemy):
    pass
class moving_hiyoko(hiyoko):
    def __init__(self, pos,pos_x):
        # 浮動小数点の位置と速度
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.fpx = float(self.rect.x)
        self.fpy = float(self.rect.y)
        self.init_posx=pos_x
        self.fpvx = 25
        self.fpvy = 0.0        
    def update(self):
        self.fpx+=self.fpvx
        # スプライトを動かすにはself.rectの更新が必要！
        self.rect.x = int(self.fpx)
        self.rect.y = int(self.fpy)

        if(abs(self.fpx-self.init_posx)>550):
            self.fpvx=-self.fpvx
      

    pass

class Cloud(pygame.sprite.Sprite):
    """雲,および背景"""
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

class goal(Cloud):
    pass
class Map:
    """マップ（プレイヤーや内部のスプライトを含む）"""
    GS = 32  # グリッドサイズ
    
    def __init__(self, filename):
        # スプライトグループの登録
        self.all = pygame.sprite.RenderUpdates()
        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()

        Python.containers = self.all
        Block.containers = self.all, self.blocks
        Enemy.containers = self.all,self.enemies
        Cloud.containers = self.all,self.clouds
        
        # プレイヤーの作成
        self.python = Python((100,600), self.blocks,self.enemies)
        
        # マップをロードしてマップ内スプライトの作成
        self.load(filename)
        
        # マップサーフェイスを作成
        self.surface = pygame.Surface((self.col*self.GS, self.row*self.GS)).convert()
        
    def draw(self):
        """マップサーフェイスにマップ内スプライトを描画"""
        self.surface.fill((30,144,255))
        self.all.draw(self.surface)
    
    def update(self):
        """マップ内スプライトを更新"""
        self.all.update()
    
    def calc_offset(self):
        """オフセットを計算"""
        offsetx = self.python.rect.topleft[0] - SCR_RECT.width/2
        offsety = self.python.rect.topleft[1] - SCR_RECT.height/2
        return offsetx, offsety

    def load(self, filename):
        """マップをロードしてスプライトを作成"""
        map = []
        fp = open(filename, "r")
        for line in fp:
            line = line.rstrip()  # 改行除去
            map.append(list(line))
            self.row = len(map)
            self.col = len(map[-1])
        self.width = self.col * self.GS
        self.height = self.row * self.GS
  
        fp.close()
        
        # マップからスプライトを作成
        for i in range(self.row):
            for j in range(self.col):
                if map[i][j] == 'B':
                    Block((j*self.GS, i*self.GS))  # ブロック
                if map[i][j] == 'C':
                    Cloud((j*self.GS,i*self.GS)) #雲  
                if map[i][j] == 'D':
                    dokan((j*self.GS,(i-2)*self.GS)) #土管
                if map[i][j] == 'G':
                    goal((j*self.GS,(i-3)*self.GS)) #ゴール 
                if map[i][j] =='H':
                    hiyoko((j*self.GS,i*self.GS))#ひよこ
                if map[i][j] =='M':
                    moving_hiyoko((j*self.GS,i*self.GS),j*self.GS)#動くひよこ



           

def load_image(filename, colorkey=None):
    """画像をロードして画像と矩形を返す"""
    filename = os.path.join("data", filename)
    try:
        image = pygame.image.load(filename)
    except pygame.error as  message:
        print ("Cannot load image:", filename)
        raise message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def split_image(image):
    """32x64のキャラクターイメージを32x32の2枚のイメージに分割
    分割したイメージを格納したリストを返す"""
    imageList = []
    for i in range(0, 64, 32):
        surface = pygame.Surface((32,32))
        surface.blit(image, (0,0), (i,0,32,32))
        surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
        surface.convert()
        imageList.append(surface)
    return imageList

if __name__ == "__main__":
    ISGAMEOVER=False

    def limit():
            while(True):
                global LIMIT
                LIMIT -=1
                time.sleep(1)

    t = threading.Thread(target=limit)
    t.start()
    PyAction()
