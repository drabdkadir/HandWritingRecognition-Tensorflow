#%%
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2' # 滤掉乱七八糟的输出信息

# 定义checkpoin文件路径
checkpoint_dir = './cnncheckpoint1201/'
checkpoint_prefix = os.path.join(checkpoint_dir, 'model')


import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets(r'D:\tmp\MNIST_data', one_hot=True)
sess = tf.InteractiveSession()

# 定义网络层的结构函数
## 定义卷积层的函数 
def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')
## 定义池化层的函数
def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1], padding='SAME')  


#定义输入格式                     
x = tf.placeholder(tf.float32, [None, 784])
y_ = tf.placeholder(tf.float32, [None, 10])
x_image = tf.reshape(x, [-1,28,28,1])

#第一层卷积和池化
#
W_conv1 = tf.get_variable('w_conv1',[5, 5, 1, 32],initializer=tf.truncated_normal_initializer(stddev=0.1))
b_conv1 = tf.get_variable('b_conv1',[32],initializer=tf.constant_initializer(0.1))
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

#第二层卷积和池化
#
W_conv2 = tf.get_variable('W_conv2',[5, 5, 32, 64],initializer=tf.truncated_normal_initializer(stddev=0.1))
b_conv2 = tf.get_variable('b_conv2',[64],initializer=tf.constant_initializer(0.1))
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

#全连接层
#
W_fc1 = tf.get_variable('W_fc1',[7*7*64,1024],initializer=tf.truncated_normal_initializer(stddev=0.1))
b_fc1 = tf.get_variable('b_fc1',[1024],initializer=tf.constant_initializer(0.1))
h_pool2_flat = tf.reshape(h_pool2,[-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat,W_fc1) + b_fc1)

#Dropout
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

#softmax
W_fc2 = tf.get_variable('W_fc2',[1024,10],initializer=tf.truncated_normal_initializer(stddev=0.1))
b_fc2 = tf.get_variable('b_fc2',[10],initializer=tf.constant_initializer(0.1))
y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)
result = tf.argmax(y_conv,1)
saver = tf.train.Saver()
#cross emtropy
cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

correct_prediction = tf.equal(result, tf.argmax(y_,1))

accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
tf.global_variables_initializer().run()
for i in range(10000):
    batch = mnist.train.next_batch(50)
    if i%1000 == 0:
        train_accuracy = accuracy.eval(feed_dict={x:batch[0], y_: batch[1], keep_prob: 1.0})
        print("step %d, training accuracy %g"%(i, train_accuracy))
    train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})
    if (i + 1) % 1000 == 0:
        saver.save(sess, checkpoint_prefix, global_step=i+1)
print("test accuracy %g"%accuracy.eval(feed_dict={
    x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))

    
    