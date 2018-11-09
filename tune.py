import numpy as np
import train
from keras.preprocessing.image import ImageDataGenerator
from keras.models import model_from_json,clone_model
import importlib, importlib.util, os.path
from keras.applications import resnet50
import sys
import os
import zipfile

def make_dirs(path):
	if not os.path.exists(path):
		os.makedirs(path)

def saveModel(model,path,config,log_file_path):
    # serialize model to JSON
    model_json = model.to_json()
    with open(os.path.join(path,config+"_"+"best_model.json"), "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(os.path.join(path,config+"_"+"best_model.h5"))
    print(config,file = open(os.path.join(log_file_path,"Tune.log"),"a"))
    print("Saved model to disk-->",path+"best_model.h5")



def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def train_and_tune(train_data,valid_data):
	#optimizers = ['SGD', 'RMSprop', 'Adam']
	learn_rate = [0.010,0.025,0.050]
	#activation_function = ['softmax', 'softplus', 'softsign']
	#dropout_rate = [0.25,0.50,0.75]
	train_conv_layer = [10,15,20,25]
	#denselayer_size = [512,1024,2048]




	log_file_path = os.path.join(os.getcwd(),'logs')
	#valid_data = 'fer2013/PublicTest1'
	#valid_data = 'drive/COLAB_NOTEBOOKS/sample/PublicTest1'
	best_models_path = os.path.join(os.getcwd(),'models','best_models')


	make_dirs(log_file_path)
	make_dirs(best_models_path)




	img_width, img_height = 224, 224
	num_channels = 3
	num_classes = 7
	batch_size = 32
	patience = 50

	epoch=3
	if 'Under_90' in train_data:
		epoch = 10
	if 'Under_10' in train_data:
		epoch = 5
	

	valid_data_gen = ImageDataGenerator(rescale=1.0/255)
	valid_generator = valid_data_gen.flow_from_directory(valid_data, (img_width, img_height), batch_size=batch_size,class_mode='categorical')
	fnames = valid_generator.filenames
	ground_truth = valid_generator.classes
	
	# print("Loading Resnet")
	# #resnet_conv = resnet50.ResNet50(weights='imagenet', include_top=False, input_shape=(img_height,img_width, num_channels))
	# resnet152 = module_from_file("resnet152_keras","resnet152_keras.py")
	# resnet_conv = resnet152.ResNet152(include_top=False, weights='imagenet',input_shape=(img_height,img_width, num_channels))
	# print("Resnet Loaded")

	resnet152 = module_from_file("resnet152_keras",os.path.join("Lib","resnet152_keras.py"))

	cur_best = None
	cur_error = np.inf

	best_lr = -1
	best_conv = -1

	print("learning_rate,train_conv_layer,performance",file=open("tuning_results.txt","w"))

	print("Starting log file.....",file=open(os.path.join(log_file_path,"Tune.log"),"w"))

	for lr in learn_rate:
		for conv in train_conv_layer:
			print("Loading Resnet")
			#resnet_conv = resnet50.ResNet50(weights='imagenet', include_top=False, input_shape=(img_height,img_width, num_channels))
			
			#resnet_conv = resnet152.ResNet152(include_top=False, weights='imagenet',input_shape=(img_height,img_width, num_channels))
			resnet_conv = resnet50.ResNet50(include_top=False, weights='imagenet',input_shape=(img_height,img_width, num_channels))

			print("Resnet Loaded")
			print("Training Model With Hyper Paramters:learning_rate {}, train_conv_layer {} ".format(lr,conv))
			print("Training Model With Hyper Paramters: learning_rate {}, train_conv_layer {} ".format(lr,conv),file=open(os.path.join(log_file_path,"Tune.log"),"a"))
			model = train.TrainModel(train_data=train_data,valid_data=valid_data,resnet_conv =resnet_conv,learning_rate=lr,train_conv_layer=conv,num_epochs=epoch)
			
			print("Model Trained.............Validation...........")
			predictions = model.predict_generator(valid_generator, steps=valid_generator.samples/valid_generator.batch_size,verbose=1)
			predicted_classes = np.argmax(predictions,axis=1)

			errors = np.where(predicted_classes != ground_truth)[0]
			print("No of errors = {}/{}".format(len(errors),valid_generator.samples),file=open(os.path.join(log_file_path,"Tune.log"),"a"))


			print("{},{},{}/{}".format(lr,conv,len(errors),valid_generator.samples),file=open("tuning_results.txt","a"))

			if(len(errors)<cur_error):
				cur_best = model
				cur_error = len(errors)
				print("Found New Best Model with params, learning_rate {}, train_conv_layer {}-->errors: {}".format(lr,conv,1.0*len(errors)/valid_generator.samples),file=open(os.path.join(log_file_path,"Tune.log"),"a"))
				saveModel(model,best_models_path,str(lr)+'_'+str(conv),log_file_path)
				best_lr = lr
				best_conv = conv

	print(best_lr,best_conv,file=open("hyperparameter.txt","w"))



if __name__ == '__main__':
	train_data = sys.argv[1]
	valid_data = sys.argv[2]

	print(os.path.dirname(train_data))

	zip_ref = zipfile.ZipFile(train_data,'r')
	zip_ref.extractall(os.path.join(os.path.dirname(train_data),"MAIN_DATA"))
	zip_ref.close()
	train_data = os.path.join(os.path.dirname(train_data),"MAIN_DATA")
	


	zip_ref = zipfile.ZipFile(valid_data,'r')
	zip_ref.extractall(os.path.join(os.path.dirname(valid_data),"MAIN_DATA"))
	zip_ref.close()
	valid_data = os.path.join(os.path.dirname(valid_data),"MAIN_DATA")
	
	best_lr = 0.010
	best_conv = 10
	print(best_lr,best_conv,file=open("hyperparameter.txt","w"))



	#train_and_tune(train_data,valid_data)