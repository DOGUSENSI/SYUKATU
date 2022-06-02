import numpy
import scipy.special


import matplotlib.pyplot
import imageio

class neuralNetowork:

    #ニューラルネットワークの初期化
    def __init__(self,inputnodes,hiddennodes,outputnodes,learningrate):
        #入力層　隠れ層　出力層のノード数の設定
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes   = outputnodes

    

        #リンクの重み行列　wihとwho
        #行列内の重み w_i_j,ノードから次の層のノードjへのリンクの重み
        #11 W21
        #12 W22など

        self.wih=numpy.random.normal(0.0,pow(self.hnodes,-0.5),(self.hnodes,self.inodes))
        self.who=numpy.random.normal(0.0,pow(self.onodes,-0.5),(self.onodes,self.hnodes))

        #学習率の設定
        self.lr=learningrate

        #活性化関数はシグモイド関数
        self.activation_function= lambda x: scipy.special.expit(x)

        pass

    #ニューラルネットワークの学習
    def train(self,inputs_list,targets_list):
        #入力リストを行列に変換
        inputs = numpy.array(inputs_list,ndmin=2).T
        targets = numpy.array(targets_list,ndmin=2).T

        #隠れ層に入ってくる信号の計算
        hidden_inputs=numpy.dot(self.wih,inputs)
         #信号を活性化関数で出力
        hidden_outputs=self.activation_function(hidden_inputs)

        #出力層に入る信号の計算
        final_inputs=numpy.dot(self.who,hidden_outputs)
        #出力層で結合された信号を活性化関数により出力
        final_outputs=self.activation_function(final_inputs)

        #出力層の誤差
        output_errors=targets-final_outputs
        #隠れ層の誤差は出力層の誤差を重みで分配
        hidden_errors=numpy.dot(self.who.T,output_errors)

        #隠れ層と出力層の間のリンクの重みを更新
        self.who+=self.lr*numpy.dot((output_errors*final_outputs*(1.0-final_outputs)),numpy.transpose(hidden_outputs))
        
        #入力層と隠れ層の間のリンクの重みを更新
        self.wih+=self.lr*numpy.dot((hidden_errors*hidden_outputs*(1.0-hidden_outputs)),numpy.transpose(inputs))

        pass

    #ニューラルネットワークの照会
    def query(self,inputs_list):
        #入力リストを行列に変換
        inputs=numpy.array(inputs_list,ndmin=2).T

        #隠れ層に入る信号の計算
        hidden_inputs=numpy.dot(self.wih,inputs)
        #信号を活性化関数で出力
        hidden_outputs=self.activation_function(hidden_inputs)

        #出力層に入る信号の計算
        final_inputs=numpy.dot(self.who,hidden_outputs)
        #出力層で結合された信号を活性化関数により出力
        final_outputs=self.activation_function(final_inputs)

        return final_outputs


#入力層　隠れ層　出力層のノード数
input_nodes=784
hidden_nodes=100
output_nodes=10

#学習率=0.3
learning_rate=0.3

n= neuralNetowork(input_nodes,hidden_nodes,output_nodes,learning_rate)

training_data_file=open("mnist_dataset/mnist_train.csv",'r')
training_data_list=training_data_file.readlines()
training_data_file.close()

f_wih=n.wih
f_who=n.who

own_test_data_list=[]
#テストデータを自作画像に変更
img_array=imageio.imread('自作4.png',as_gray=True)


img_data=255.0 - img_array.reshape(784)
own_test_data_list.append(img_data)

img_array=imageio.imread('自作8.png',as_gray=True)

answer=[4,8]

img_data=255.0 - img_array.reshape(784)
own_test_data_list.append(img_data)

print(own_test_data_list[0])
test = own_test_data_list[0].split(',')


# epochs:訓練データが学習で使われた回数
epochs = 2
for e in range(epochs):
    for record in training_data_list:
        all_values = record.split(',')
        inputs =(numpy.asfarray(all_values[1:])/255.0*0.99)+0.01
        targets=numpy.zeros(output_nodes)+0.01
        targets[int(all_values[0])]=0.99
        n.train(inputs,targets)
        pass
    pass

#MNISTのテストデータをcsvファイルを読み込んでリストにする
test_data_file=open("mnist_dataset/mnist_test.csv",'r')
test_data_list=test_data_file.readlines()
test_data_file.close()



#ニューラルネットワークのテスト

#scorecard は判定のリスト、最初は空
scorecard=[]


#テストデータのすべてのデータに対して実行
for record in test_data_list:
    all_values=record.split(',')
#正解は1番目
    correct_label=int(all_values[0])
    print(correct_label,"correct label;")

    #ラベルを出力

    image_array=numpy.asfarray(all_values[1:]).reshape((28,28))
    matplotlib.pyplot.imshow(image_array,cmap='Greys',interpolation='None')

    matplotlib.pyplot.show()

#入力値のスケーリングとシフト
    inputs =(numpy.asfarray(all_values[1:])/255.0*0.99)+0.01
    outputs = n.query(inputs)
    label=numpy.argmax(outputs)
    print(label,"network's answer")
    #正解・不正解をリストに追加
    if(label==correct_label):
        #正解なら1を追加
        scorecard.append(1)
    else:
        scorecard.append(0)
#制度の計算
scorecard_array=numpy.asarray(scorecard)
print("performance =",scorecard_array.sum()/scorecard_array.size)

