import tensorflow as tf
import numpy as np
from sklearn.utils import shuffle


#filename is an array ie [filename]
def getData(filename):
    X = []
    Y = []
    filename_queue = tf.train.string_input_producer(filename)

    reader = tf.TextLineReader()
    key, value = reader.read(filename_queue)

    # Default values, in case of empty columns. Also specifies the type of the
    # decoded result.
    record_defaults = [tf.constant([], dtype=tf.string),    # Column 0
                       tf.constant([], dtype=tf.string),    # Column 1
                       tf.constant([], dtype=tf.string),    # Column 2
                       tf.constant([], dtype=tf.string),
                       tf.constant([], dtype=tf.string)]
    col1, col2, col3, col4, col5 = tf.decode_csv(
        value, record_defaults=record_defaults)
    features = tf.stack([col1, col2, col3, col4])

    with tf.Session() as sess:
        # Start populating the filename queue.
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)

        for i in range(1369):
            # Retrieve a single instance:
            single_x, label = sess.run([features, col5])
            single_x = [[int(single_x[0][i:i+1]) for i in range(0, len(single_x[0]), 1)]+
                         [int(single_x[1][i:i+1]) for i in range(0, len(single_x[0]), 1)]+
                         [int(single_x[2][i:i+1]) for i in range(0, len(single_x[0]), 1)]+
                         [int(single_x[3][i:i+1]) for i in range(0, len(single_x[0]), 1)]]
            label = [[label[i:i+1] for i in range(0, len(label), 1)]]
            X.extend(single_x)
            Y.extend(label)
        coord.request_stop()
        coord.join(threads)
        
    return {'features': X, 'labels': Y}

    

train_data = getData(["data/data.csv"])
# train_data['features'], train_data['labels'] = shuffle(train_data['features'], train_data['labels'])
# print(data['features'][0])
# print(data['labels'][0])
# print(data['labels'][492])
total_examples = len(train_data['labels'])

# print(np.shape(train_data['features']))

n_nodes_input = 104
n_nodes_hl1 = 52
n_nodes_hl2 = 52
n_nodes_output = 26

x = tf.placeholder('float',[None, 104], name="x")
y = tf.placeholder('float')


def binary_activation(z):
    cond = tf.less(z, tf.multiply(tf.ones(tf.shape(z), dtype=tf.float32), 0.5))
    out = tf.where(cond, tf.zeros(tf.shape(z), dtype=tf.float32), tf.ones(tf.shape(z), dtype=tf.float32))
    
    return out

    
def neural_network_model(data):

    n_nodes_output_name = 16
    n_nodes_output_attr = 3
    n_nodes_output_anum = 7
    
    n_nodes_input_div = int(n_nodes_input/4)
    n_nodes_h1_div = int(n_nodes_hl1/4)
    
    hidden_1_layer_1 = {'weights': tf.Variable(tf.random_normal([n_nodes_input_div, n_nodes_h1_div])),
                      'biases': tf.Variable(tf.zeros([1,n_nodes_h1_div]))}
    hidden_1_layer_2 = {'weights': tf.Variable(tf.random_normal([n_nodes_input_div, n_nodes_h1_div])),
                      'biases': tf.Variable(tf.zeros([1,n_nodes_h1_div]))}
    hidden_1_layer_3 = {'weights': tf.Variable(tf.random_normal([n_nodes_input_div, n_nodes_h1_div])),
                      'biases': tf.Variable(tf.zeros([1,n_nodes_h1_div]))}
    hidden_1_layer_4 = {'weights': tf.Variable(tf.random_normal([n_nodes_input_div, n_nodes_h1_div])),
                      'biases': tf.Variable(tf.zeros([1,n_nodes_h1_div]))}
                      
    hidden_2_layer = {'weights': tf.Variable(tf.random_normal([n_nodes_hl1, n_nodes_hl2])),
                      'biases': tf.Variable(tf.zeros([1,n_nodes_hl2]))}
    
    output_layer_name = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_output_name])),
                    'biases': tf.Variable(tf.zeros([1,n_nodes_output_name]))}
    output_layer_attr = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_output_attr])),
                    'biases': tf.Variable(tf.zeros([1,n_nodes_output_attr]))}
    output_layer_anum = {'weights': tf.Variable(tf.random_normal([n_nodes_hl2, n_nodes_output_anum])),
                    'biases': tf.Variable(tf.zeros([1,n_nodes_output_anum]))}
    
    data_1 = tf.slice(data, [0,0], [tf.shape(data)[0],26])
    data_2 = tf.slice(data, [0,26], [tf.shape(data)[0],26])
    data_3 = tf.slice(data, [0,26*2], [tf.shape(data)[0],26])
    data_4 = tf.slice(data, [0,26*3], [tf.shape(data)[0],26])
    
    l1_1 = tf.tanh(tf.add(tf.matmul(data_1, hidden_1_layer_1['weights']), hidden_1_layer_1['biases']))
    l1_2 = tf.tanh(tf.add(tf.matmul(data_2, hidden_1_layer_2['weights']), hidden_1_layer_2['biases']))
    l1_3 = tf.tanh(tf.add(tf.matmul(data_3, hidden_1_layer_3['weights']), hidden_1_layer_3['biases']))
    l1_4 = tf.tanh(tf.add(tf.matmul(data_4, hidden_1_layer_4['weights']), hidden_1_layer_4['biases']))
    
    # (input_data * weights) + biases
    
    l1 = tf.concat([l1_1, l1_2, l1_3, l1_4], 1)
    #l1 = binary_activation(l1)
    
    l2 = tf.add(tf.matmul(l1, hidden_2_layer['weights']), hidden_2_layer['biases'])
    l2 = tf.tanh(l2)
    #l2 = binary_activation(l2)
    
    output_name = tf.add(tf.matmul(l2, output_layer_name['weights']), output_layer_name['biases'])
    ac_output_name = tf.nn.softmax(output_name)
    
    output_attr = tf.add(tf.matmul(l2, output_layer_attr['weights']), output_layer_attr['biases'])
    ac_output_attr = tf.sigmoid(output_attr)
    
    output_anum = tf.add(tf.matmul(l2, output_layer_anum['weights']), output_layer_anum['biases'])
    ac_output_anum = tf.sigmoid(output_anum)
    
    output = tf.concat([output_name, output_attr, output_anum], 1)
    ac_output = tf.concat([ac_output_name, ac_output_attr, ac_output_anum], 1)
    #output = binary_activation(output)
    ac_output = tf.identity(ac_output, name="output")
    return output
    
    
def cost_function(input, target, prediction):
    output_1 =tf.slice(target,[0,0],[tf.shape(target)[0], 16])
    pred_1 = tf.slice(prediction,[0,0],[tf.shape(target)[0], 16])
    output_2_3 = tf.slice(target,[0,16],[tf.shape(target)[0], 10])
    pred_2_3 = tf.slice(prediction,[0,16],[tf.shape(target)[0], 10])
    cost = tf.nn.softmax_cross_entropy_with_logits(labels=output_1, logits=pred_1)
    cost += tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=output_2_3, logits=pred_2_3))
    cost = tf.reduce_mean(cost)
    
    '''
    input_1 = tf.slice(input,[0,0],[tf.shape(input)[0], 16])
    input_2 = tf.slice(input,[0,26],[tf.shape(input)[0], 16])
    input_3 = tf.slice(input,[0,26*2],[tf.shape(input)[0], 16])
    input_4 = tf.slice(input,[0,26*3],[tf.shape(input)[0], 16])
    
    add_cost = tf.minimum(avg_distance_between(input_1, pred_1), avg_distance_between(input_2, pred_1))
    add_cost = tf.minimum(add_cost, avg_distance_between(input_3, pred_1))
    add_cost = tf.minimum(add_cost, avg_distance_between(input_4, pred_1))
    
    # TODO: check math
    cost = tf.multiply(cost, 10)
    cost = tf.divide(cost, add_cost)
    '''
    
    return cost
    
def avg_distance_between(p_1, p_2):
    #tf.Print(p_2, p_2)
    res = tf.subtract(p_1, p_2)
    res = tf.square(res)
    res = tf.reduce_sum(res, 1)
    res = tf.sqrt(res)
    res = tf.reduce_mean(res)
    return res
    


def train_neural_network(x):
    prediction = neural_network_model(x)
    cost = cost_function(x, y, prediction)
    #                    learning_rate = 0.001
    optimizer = tf.train.AdamOptimizer().minimize(cost)
    
    hm_epochs = 1000
    
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        
        for epoch in range(hm_epochs):
            
            epoch_loss = 0
            _, c = sess.run([optimizer, cost], feed_dict = {x:train_data['features'], y:train_data['labels']})
            epoch_loss = c
            print('Epoch', (epoch+1), 'completed out of', hm_epochs, 'loss: ', epoch_loss)
        
        
        # testing part
        correct = avg_distance_between(prediction, y)
        accuracy = tf.reduce_mean(tf.cast(correct, 'float'))
        print('Accuracy: ', accuracy.eval({x:train_data['features'], y:train_data['labels']}))
        
        
        saver.save(sess, 'model/model.ckpt')
        print('saved model at model/model')
        

train_neural_network(x)






















