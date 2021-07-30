import time,sys,glob,os
import scipy.io.wavfile as wav
print("importing psf")
from python_speech_features import mfcc
print("importing numpy")
import numpy as np
print("importing RFC")
from sklearn.ensemble import RandomForestClassifier
#mfccs = []
mfccs=np.array([])
true_labels = []
file_names = []

segments=50 #grains
cepstra=12

#DON'T FORGET, TREELITE SORTS YOUR CATEGORIES ALPHABETICALLY. THUS, YOUR PREDICTOR NEEDS TO HAVE THEM SORTED ALPHABETICALLY AS WELL
labels=sorted(['LUCIA','LIA','PAUL','NIKOLOZ','DANIEL','IOLANDA','DOROTHEA','OLIVER'])
session_id=sys.argv[1]
print(labels)
print("activating predictor for identification of voice in session "+session_id)
import treelite_runtime     # runtime module
predictor = treelite_runtime.Predictor('./classifiers/personae.so', verbose=True)
print("predictor activated")

sounds = glob.glob('./sessions/'+session_id+'/*')
i=0

sum_predictions=np.zeros([len(labels)])

for s in sounds:
  print(s)
  i=i+1
  start_time=time.time()
  (sampling_rate,signal)=wav.read(s)
  hop=(len(signal)/(segments-1)/sampling_rate)
  features= mfcc(signal,sampling_rate,numcep=cepstra,winstep=hop,nfft=512)
  features.resize(((segments*2)-2,cepstra))
  f=features.flatten()
  batch = treelite_runtime.Batch.from_npy2d(np.array([f]))
  prediction = predictor.predict(batch)
  sum_predictions+=prediction.flatten()
  best_prediction =  int(np.argmax(prediction,axis=1))
  end_time=time.time()
  print(prediction,labels[best_prediction],str(end_time-start_time)+' seconds')

print(sum_predictions/i)
