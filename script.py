import numpy as np
from scipy.io import loadmat
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


e_total = np.zeros(10)
i=0
def preprocess():
    """ 
     Input:
     Although this function doesn't have any input, you are required to load
     the MNIST data set from file 'mnist_all.mat'.

     Output:
     train_data: matrix of training set. Each row of train_data contains 
       feature vector of a image
     train_label: vector of label corresponding to each image in the training
       set
     validation_data: matrix of training set. Each row of validation_data 
       contains feature vector of a image
     validation_label: vector of label corresponding to each image in the 
       training set
     test_data: matrix of training set. Each row of test_data contains 
       feature vector of a image
     test_label: vector of label corresponding to each image in the testing
       set
    """

    mat = loadmat('mnist_all.mat')  # loads the MAT object as a Dictionary

    n_feature = mat.get("train1").shape[1]
    n_sample = 0
    for i in range(10):
        n_sample = n_sample + mat.get("train" + str(i)).shape[0]
    n_validation = 1000
    n_train = n_sample - 10 * n_validation

    # Construct validation data
    validation_data = np.zeros((10 * n_validation, n_feature))
    for i in range(10):
        validation_data[i * n_validation:(i + 1) * n_validation, :] = mat.get("train" + str(i))[0:n_validation, :]

    # Construct validation label
    validation_label = np.ones((10 * n_validation, 1))
    for i in range(10):
        validation_label[i * n_validation:(i + 1) * n_validation, :] = i * np.ones((n_validation, 1))

    # Construct training data and label
    train_data = np.zeros((n_train, n_feature))
    train_label = np.zeros((n_train, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("train" + str(i)).shape[0]
        train_data[temp:temp + size_i - n_validation, :] = mat.get("train" + str(i))[n_validation:size_i, :]
        train_label[temp:temp + size_i - n_validation, :] = i * np.ones((size_i - n_validation, 1))
        temp = temp + size_i - n_validation

    # Construct test data and label
    n_test = 0
    for i in range(10):
        n_test = n_test + mat.get("test" + str(i)).shape[0]
    test_data = np.zeros((n_test, n_feature))
    test_label = np.zeros((n_test, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("test" + str(i)).shape[0]
        test_data[temp:temp + size_i, :] = mat.get("test" + str(i))
        test_label[temp:temp + size_i, :] = i * np.ones((size_i, 1))
        temp = temp + size_i

    # Delete features which don't provide any useful information for classifiers
    sigma = np.std(train_data, axis=0)
    index = np.array([])
    for i in range(n_feature):
        if (sigma[i] > 0.001):
            index = np.append(index, [i])
    train_data = train_data[:, index.astype(int)]
    validation_data = validation_data[:, index.astype(int)]
    test_data = test_data[:, index.astype(int)]

    # Scale data to 0 and 1
    train_data /= 255.0
    validation_data /= 255.0
    test_data /= 255.0

    return train_data, train_label, validation_data, validation_label, test_data, test_label


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def blrObjFunction(initialWeights, *args):
    """
    blrObjFunction computes 2-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector (w_k) of size (D + 1) x 1 
        train_data: the data matrix of size N x D
        labeli: the label vector (y_k) of size N x 1 where each entry can be either 0 or 1 representing the label of corresponding feature vector

    Output: 
        error: the scalar value of error function of 2-class logistic regression
        error_grad: the vector of size (D+1) x 1 representing the gradient of
                    error function
    """
    global e_total
    train_data, labeli = args
    initialWeights = initialWeights.reshape((-1, 1))
    # print("W shape:")
    # print(initialWeights.shape)
    
    # print("x shape:")
    # print(train_data.shape)
    
    n_data = train_data.shape[0]
    n_features = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_features + 1, 1))
    #print("W shape:1")
    
    ones = np.ones((train_data.shape[0], 1))
    #print("W shape:2")

    biastrain_data = np.hstack((ones, train_data))
    #print("W shape:3")
    
    # print("x shape:")
    # print(biastrain_data.shape)
    
    theta = sigmoid(np.dot( biastrain_data, initialWeights))
    #print("W shape:4")
    
    labeli = labeli.reshape(-1, 1) 
    #print("W shape:5")
    
    per_sample_errors = -(labeli * np.log(theta) + (1 - labeli) * np.log(1 - theta))
    error = np.mean(per_sample_errors)
    
    current_class_index = np.sum(labeli) == labeli.shape[0] 
    e_total[i] = np.sum(per_sample_errors)
    #print("W shape:6")
    
    error_grad = np.zeros((n_features + 1, 1))
    #print("W shape:7")
    
    xb= theta-labeli
    
    error_grad = np.dot(biastrain_data.T, (theta - labeli))/n_data
    #print("W shape:8")
    
    
    # plt.figure(figsize=(4, 6))
    # plt.bar(['Total Error'], [e_total], color='salmon')
    # plt.ylabel("Total Error")
    # plt.title("Total Training Error")
    # plt.tight_layout()
    # plt.show()

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data
    #print(error)
    return error, error_grad.flatten()


def blrPredict(W, data):
    """
     blrObjFunction predicts the label of data given the data and parameter W 
     of Logistic Regression
     
     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight 
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D
         
     Output: 
         label: vector of size N x 1 representing the predicted label of 
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))
    
   # W = W.reshape((-1, 1))
    ones = np.ones((data.shape[0], 1))

    biastrain_data = np.hstack((ones, data))
    
    # print("W shape:")
    # print(W.shape)
    
    # print("x shape:")
    # print(biastrain_data.shape)
    
    theta = sigmoid(np.dot(biastrain_data,  W))
    
    label = np.argmax(theta, axis=1)
    label = label.reshape(-1, 1)
    
    
    

    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    return label

def mlrObjFunction(params, *args):
    """
    mlrObjFunction computes multi-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights_b: the weight vector of size (D + 1) x 10
        train_data: the data matrix of size N x D
        labeli: the label vector of size N x 1 where each entry can be either 0 or 1
                representing the label of corresponding feature vector

    Output:
        error: the scalar value of error function of multi-class logistic regression
        error_grad: the vector of size (D+1) x 10 representing the gradient of
                    error function
    """
    global e_total
    train_data, labeli = args
    n_class = labeli.shape[1]
    n_features = train_data.shape[1]
    params = params.reshape((n_features + 1, n_class))
    # print("W shape:")
    # print(initialWeights.shape)
    
    # print("x shape:")
    # print(train_data.shape)
    
    n_data = train_data.shape[0]
    n_features = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_features + 1, 1))
    #print("W shape:1")
    
    ones = np.ones((train_data.shape[0], 1))
    #print("W shape:2")

    biastrain_data = np.hstack((ones, train_data))
    #print("W shape:3")
    
    # print("x shape:")
    # print(biastrain_data.shape)
    Z = np.dot(biastrain_data, params)  
    px = (np.exp(Z - np.max(Z, axis=1, keepdims=True)))/np.sum(np.exp(Z - np.max(Z, axis=1, keepdims=True)), axis=1, keepdims=True)
    
    
    error = -np.sum(labeli * np.log(px))/n_data
    
    theta = sigmoid(np.dot( biastrain_data, params))
    #print("W shape:4")
    
      
    #print("W shape:5")
    
    # per_sample_errors = -(labeli * np.log(px))
    # error = np.mean(per_sample_errors)
    
    error_grad = np.dot(biastrain_data.T, (px - labeli))/n_data
    
    # current_class_index = np.sum(labeli) == labeli.shape[0] 
    # e_total[i] = np.sum(per_sample_errors)
    #print("W shape:6")
    
    # error_grad = np.zeros((n_features + 1, 1))
    #print("W shape:7")
    
    # xb= theta-labeli
    
    # error_grad = np.dot(biastrain_data.T, (theta - labeli))/n_data


    return error, error_grad.flatten()


def mlrPredict(W, data):
    """
     mlrObjFunction predicts the label of data given the data and parameter W
     of Logistic Regression

     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D

     Output:
         label: vector of size N x 1 representing the predicted label of
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

    n_data = data.shape[0]
    ones = np.ones((n_data, 1))
    bias_data = np.hstack((ones, data))


    Z = np.dot(bias_data, W) 
 
    xy = (np.exp(Z - np.max(Z, axis=1, keepdims=True)))/np.sum((np.exp(Z - np.max(Z, axis=1, keepdims=True))), axis=1, keepdims=True)  

    # Predict label = class with max probability
    label = np.argmax(xy, axis=1).reshape(-1, 1)
  
    ##################
    # YOUR CODE HERE #
    ##################
    # HINT: Do not forget to add the bias term to your input data

    return label


"""
Script for Logistic Regression
"""
train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# number of classes
n_class = 10

# number of training samples
n_train = train_data.shape[0]

# number of features
n_feature = train_data.shape[1]

Y = np.zeros((n_train, n_class))
for i in range(n_class):
    Y[:, i] = (train_label == i).astype(int).ravel()
print("NUM Fea:")
print(n_feature+1)
# Logistic Regression with Gradient Descent
W = np.zeros((n_feature + 1, n_class))
initialWeights = np.zeros(n_feature + 1)
opts = {'maxiter': 100}
for class_index in range(n_class):
        
    i = class_index
    labeli = Y[:, class_index].reshape(n_train, 1)
    args = (train_data, labeli)
    nn_params = minimize(blrObjFunction, initialWeights, jac=True, args=args, method='CG', options=opts)
    W[:, class_index] = nn_params.x.reshape((n_feature + 1,))

# Find the accuracy on Training Dataset
predicted_label = blrPredict(W, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label == train_label).astype(float))) + '%')

# Find the accuracy on Validation Dataset
predicted_label = blrPredict(W, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label = blrPredict(W, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label == test_label).astype(float))) + '%')


plt.figure(figsize=(10, 5))
plt.bar(range(10), e_total, color='salmon')
plt.xlabel("Digit Class")
plt.ylabel("Total Training Error")
plt.title("Total Cross-Entropy Training Error per Class using BLR")
plt.xticks(range(10))
plt.tight_layout()
plt.show()


print('-------------------For Test data---------------------')
e_total = np.zeros(10)
i=0
# number of training samples
n_test = test_data.shape[0]

# number of features
n_featurey = test_data.shape[1]
Y1 = np.zeros((n_test, n_class))
for i in range(n_class):
    Y1[:, i] = (test_label == i).astype(int).ravel()
print("NUM Fea:")
print(n_featurey+1)
# Logistic Regression with Gradient Descent
W2 = np.zeros((n_featurey + 1, n_class))
initialWeights1 = np.zeros(n_featurey + 1)
opts1 = {'maxiter': 100}
for i in range(n_class):
    labeli1 = Y1[:, i].reshape(n_test, 1)
    args1 = (test_data, labeli1)
    nn_params1 = minimize(blrObjFunction, initialWeights1, jac=True, args=args1, method='CG', options=opts1)
    W2[:, i] = nn_params1.x.reshape((n_featurey + 1,))

plt.figure(figsize=(10, 5))
plt.bar(range(10), e_total, color='salmon')
plt.xlabel("Digit Class")
plt.ylabel("Total BLR Testing Error")
plt.title("Total Cross-Entropy Test Error per Class using BLR")
plt.xticks(range(10))
plt.tight_layout()
plt.show()

# """
# Script for Support Vector Machine
# """

# print('\n\n--------------SVM-------------------\n\n')
# ################## 
# # YOUR CODE HERE #
# ##################

# # Linear Kernel

# train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# train_label = train_label.ravel()
# validation_label = validation_label.ravel()
# test_label = test_label.ravel()


# svclin = SVC(kernel='linear') 
# svclin.fit(train_data, train_label)

# train_acc_lin = accuracy_score(train_label, svclin.predict(train_data))
# vacc_lin = accuracy_score(validation_label, svclin.predict(validation_data))
# test_acc_lin = accuracy_score(test_label, svclin.predict(test_data))

# print("Linear Kernel Accuracies:")
# print("Train:", train_acc_lin, "Val:", vacc_lin, "Test:", test_acc_lin)

# train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# train_label = train_label.ravel()
# validation_label = validation_label.ravel()
# test_label = test_label.ravel()

# svcrbfdef = SVC(kernel='rbf')  
# svcrbfdef.fit(train_data, train_label)

# train_acc_rbfd = accuracy_score(train_label, svcrbfdef.predict(train_data))
# val_acc_rbfd = accuracy_score(validation_label, svcrbfdef.predict(validation_data))
# test_acc_rbfd = accuracy_score(test_label, svcrbfdef.predict(test_data))


# print("RBF default gamma Accuracies:")
# print("Train:", train_acc_rbfd, "Val:", val_acc_rbfd, "Test:", test_acc_rbfd)

# # Radial basis function with value of gamma setting to 1
# train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# train_label = train_label.ravel()
# validation_label = validation_label.ravel()
# test_label = test_label.ravel()

# svcrbfg1 = SVC(kernel='rbf', gamma=1)
# svcrbfg1.fit(train_data, train_label)

# train_acc_rbfg1 = accuracy_score(train_label, svcrbfg1.predict(train_data))
# vacc_rbfg1 = accuracy_score(validation_label, svcrbfg1.predict(validation_data))
# test_acc_rbfg1 = accuracy_score(test_label, svcrbfg1.predict(test_data))

# print("RBF gamma=1 Accuracies:")
# print("Train:", train_acc_rbfg1, "Val:", vacc_rbfg1, "Test:", test_acc_rbfg1)


# # Radial basis function with value of gamma setting to default
# train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# train_label = train_label.ravel()
# validation_label = validation_label.ravel()
# test_label = test_label.ravel()

# svcrbfdef = SVC(kernel='rbf')  
# svcrbfdef.fit(train_data, train_label)

# train_acc_rbfd = accuracy_score(train_label, svcrbfdef.predict(train_data))
# val_acc_rbfd = accuracy_score(validation_label, svcrbfdef.predict(validation_data))
# test_acc_rbfd = accuracy_score(test_label, svcrbfdef.predict(test_data))


# print("RBF default gamma Accuracies:")
# print("Train:", train_acc_rbfd, "Val:", val_acc_rbfd, "Test:", test_acc_rbfd)


# # Radial basis function with value of gamma setting to default and varying value of C (1, 10, 20, 30,..., 100)
# train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# train_label = train_label.ravel()
# validation_label = validation_label.ravel()
# test_label = test_label.ravel()

# Cval = list(range(1, 101, 10))  

# trainacc = []
# valacc = []
# testacc = []

# for i in Cval:
#     svc_rbfc = SVC(kernel='rbf', C=i) 
#     svc_rbfc.fit(train_data, train_label)
    
#     train_acc = accuracy_score(train_label, svc_rbfc.predict(train_data))
#     val_acc = accuracy_score(validation_label, svc_rbfc.predict(validation_data))
#     test_acc = accuracy_score(test_label, svc_rbfc.predict(test_data))
    
#     trainacc.append(train_acc)
#     valacc.append(val_acc)
#     testacc.append(test_acc)

# best_c_index = np.argmax(valacc)
# best_c = Cval[best_c_index]
# best_val_acc = valacc[best_c_index]
# best_train_acc = trainacc[best_c_index]
# best_test_acc = testacc[best_c_index]

# print(f"\nBest C based on Validation Accuracy: C = {best_c}")
# print(f"Train Accuracy: {best_train_acc:.4f}, Validation Accuracy: {best_val_acc:.4f}, Test Accuracy: {best_test_acc:.4f}")


# plt.figure(figsize=(8, 5))
# plt.plot(Cval, trainacc, label='Train Accuracy', marker='o')
# plt.plot(Cval, valacc, label='Validation Accuracy', marker='x')
# plt.plot(Cval, testacc, label='Test Accuracy', marker='s', linestyle='--')

# plt.axvline(x=best_c, color='red', linestyle=':', label=f'Best C = {best_c}')
# plt.xlabel('C Value')
# plt.ylabel('Accuracy')
# plt.title('SVM Accuracy with varying C (RBF Kernel)')

# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.savefig("svmacc_varyingC.png") 
# plt.show()


"""
Script for Extra Credit Part
"""
train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()
# FOR EXTRA CREDIT ONLY
e_total = np.zeros(10)
i=0
W_b = np.zeros((n_feature + 1, n_class))
initialWeights_b = np.zeros((n_feature + 1, n_class)).flatten()
opts_b = {'maxiter': 100}

args_b = (train_data, Y)
nn_params = minimize(mlrObjFunction, initialWeights_b, jac=True, args=args_b, method='CG', options=opts_b)
W_b = nn_params.x.reshape((n_feature + 1, n_class))

# Find the accuracy on Training Dataset
predicted_label_b = mlrPredict(W_b, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label_b == train_label).astype(float))) + '%')

# Find the accuracy on Validation Dataset
predicted_label_b = mlrPredict(W_b, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label_b == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label_b = mlrPredict(W_b, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label_b == test_label).astype(float))) + '%')

plt.figure(figsize=(10, 5))
plt.bar(range(10), e_total, color='salmon')
plt.xlabel("Digit Class")
plt.ylabel("Total MLR Training Error")
plt.title("Total Cross-Entropy Train Error using MLR")
plt.xticks(range(10))
plt.tight_layout()
plt.show()


print('-------------------For Test data MLR---------------------')

e_total = np.zeros(10)
i=0
W_b = np.zeros((n_featurey + 1, n_class))
initialWeights_b = np.zeros((n_featurey + 1, n_class)).flatten()
opts_b12 = {'maxiter': 100}

args_b12 = (test_data, Y1)
nn_params12 = minimize(mlrObjFunction, initialWeights_b, jac=True, args=args_b12, method='CG', options=opts_b12)
W_b = nn_params12.x.reshape((n_featurey + 1, n_class))

# # Find the accuracy on Training Dataset
# predicted_label_b = mlrPredict(W_b, test_data)
# print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label_b == train_label).astype(float))) + '%')

# # Find the accuracy on Validation Dataset
# predicted_label_b = mlrPredict(W_b, validation_data)
# print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label_b == validation_label).astype(float))) + '%')

# # Find the accuracy on Testing Dataset
# predicted_label_b = mlrPredict(W_b, test_data)
# print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label_b == test_label).astype(float))) + '%')

plt.figure(figsize=(10, 5))
plt.bar(range(10), e_total, color='salmon')
plt.xlabel("Digit Class")
plt.ylabel("Total MLR Testing Error")
plt.title("Total Cross-Entropy Test Error using MLR")
plt.xticks(range(10))
plt.tight_layout()
plt.show()
